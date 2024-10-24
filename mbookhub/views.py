import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest,HttpResponseRedirect, JsonResponse
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
# Create your views here.


def book_list(request):
    # Fetch books and prefetch related posts for efficiency
    books = Book.objects.prefetch_related('post_set').all()  # `post_set` is the reverse relation for the ForeignKey
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
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)  # Don't save to the database yet
            post.book = book
            post.user = request.user
            post.save()  # Now save it with book and user assigned
            return redirect('book_list')  # Redirect to the book's detail page or where you'd like
    else:
        form = PostForm()

    return render(request, 'mbook/create_post.html', {'form': form, 'book': book})


@login_required
def like_post(request,post_id):
    post = Post.objects.get(id=post_id)

    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user) #if liked, unlike
    else:
        post.likes.add(request.user)

    return JsonResponse(
        {
            'success': True,
            'likes_count': post.likes.count()
        }
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)  # Get the post that the comment is about

    if request.method == 'POST':
        comment_content = request.POST.get('comment_content')

        if comment_content:
            # Create and save the comment
            Comment.objects.create(
                post=post,
                user=request.user,  # Link the comment to the logged-in user
                content=comment_content
            )
        
        # Redirect back to the booklist homepage after adding the comment
        return redirect('booklist_home')
