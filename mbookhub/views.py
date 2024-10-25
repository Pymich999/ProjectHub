import requests
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest,HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from .models import Book, Profile, Books, Post, Comment, Rating
from .forms import SignupForm, ProfileUpdateForm, PostForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import settings
from requests.exceptions import RequestException
from django.db.models import Count
# Create your views here.

def book_list(request):
    books = Book.objects.annotate(post_count=Count('post')).filter(post_count__gt=0).prefetch_related('post_set__comments')
    return render(request, 'mbook/book_list.html', {'books': books})

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request,user)
            return redirect('book_list')
        else:
            print(form.errors)

    else:
        form = SignupForm()
    return render(request,'mbook/signup.html',{'form':form})

@login_required(login_url='login')
def profile(request):
    user_books = Books.objects.filter(user=request.user)
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('profile')
    else:
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'mbook/profile.html', {'profile_form':profile_form, 'user_books':user_books})


class CustomLoginView(LoginView):
    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password, If you dont have an account please sign up")
        return super().form_invalid(form)



def addbook(request):
    query = request.GET.get('q', '')
    books = []
    error_message = None  # Initialize error message to None

    if query:
        try:
            # Make the Google Books API call
            url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={settings.GOOGLE_BOOKS_API_KEY}'
            response = requests.get(url, timeout=10)  # Set a timeout for the API request

            if response.status_code == 200:
                data = response.json()

                # Extract relevant info from the API
                for item in data.get('items', []):
                    book_info = item['volumeInfo']
                    books.append({
                        'google_id': item['id'],
                        'title': book_info.get('title'),
                        'authors': ', '.join(book_info.get('authors', ['Unknown Authors'])),
                        'published_date': book_info.get('publishedDate', 'N/A'),
                        'description': book_info.get('description', 'No description available'),
                        'thumbnail': book_info.get('imageLinks', {}).get('thumbnail'),
                        'infolink': book_info.get('infoLink')
                    })
            else:
                error_message = "Oops, unable to connect right now, check your connection and try again."
        except RequestException:
            # Handle connection errors, timeouts, etc.
            error_message = "Oops, unable to connect right now, check your connection and try again."

    # Check if the request method is POST before accessing action
    if request.method == 'POST':
        google_id = request.POST.get('google_id')
        title = request.POST.get('title')
        authors = request.POST.get('authors')
        published_date = request.POST.get('published_date')
        description = request.POST.get('description')
        thumbnail = request.POST.get('thumbnail')
        action = request.POST.get('action', '')  # Safely initialize 'action' to an empty string if not provided

        if action == 'add_to_catalogue':
            # Add to profile catalogue
            book, created = Books.objects.get_or_create(
                google_id=google_id,
                defaults={
                    'title': title,
                    'authors': authors,
                    'published_date': published_date,
                    'description': description,
                    'thumbnail': thumbnail,
                    'user': request.user,
                }
            )
            return redirect('profile')

        elif action == 'post_to_booklist':
            # Add to public booklist
            book, created = Book.objects.get_or_create(
                title=title,
                authors=authors,
                defaults={
                    'published_date': published_date,
                    'description': description,
                    'thumbnail': thumbnail,
                }
            )
            # Redirect to create post page
            return redirect('create_post', book_id=book.id)

        # Add error message if action is unrecognized or missing
        else:
            error_message = "Invalid action. Please try again."

    # Pass the books and error message to the template
    return render(request, 'mbook/addbook.html', {'books': books, 'query': query, 'error_message': error_message})


@login_required
def create_post(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        caption = request.POST.get('caption')
        if caption:
            # Use the book's thumbnail for the post's thumbnail
            post = Post.objects.create(
                book=book, 
                user=request.user, 
                caption=caption,
                thumbnail=book.thumbnail  # Set the post thumbnail from the book's thumbnail
            )
            return redirect('book_list')  # Redirect to the book list or homepage

    return render(request, 'mbook/create_post.html', {'book': book})


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Toggle like or unlike
    if request.user in post.likes.all():
        post.likes.remove(request.user)  # Unlike the post
    else:
        post.likes.add(request.user)  # Like the post

    # Return the updated like count as a JSON response
    return JsonResponse({
        'success': True,
        'likes_count': post.likes.count()  # Send back the updated like count
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Create and save the comment
            Comment.objects.create(post=post, user=request.user, content=content)
    
    return redirect('book_list')  # Redirect to the book list page

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Ensure only the post owner can delete the post
    if post.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this post.")

    post.delete()  # Delete the post
    return redirect('book_list')  # Redirect to the book list page after deletion

@login_required
def rate_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Ensure we are handling a JSON POST request
    try:
        data = json.loads(request.body)  # Load JSON data from request body
        rating_value = data.get('rating')
        
        if rating_value and 1 <= int(rating_value) <= 5:  # Validate rating value
            rating, created = Rating.objects.update_or_create(
                book=book,
                user=request.user,
                defaults={'rating': int(rating_value)}
            )
            return JsonResponse({'success': True, 'new_rating': rating.rating})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid rating value'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid data format'}, status=400)
