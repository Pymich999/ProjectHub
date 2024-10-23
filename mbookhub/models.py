from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=250)
    authors = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    published_date = models.CharField(max_length=10)
    thumbnail = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.title
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=100, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username
    

class Books(models.Model):
    google_id = models.CharField(max_length=250, unique=True)
    title = models.CharField(max_length=250)
    authors = models.CharField(max_length=250, null=True, blank=True)
    published_date = models.CharField(max_length=10)
    description = models.TextField(blank=True, null=True)
    thumbnail = models.URLField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='books')


    def __str__(self):
        return f"{self.title} by {self.author}"

#model to store users post about a book
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    caption = models.TextField(null=True, blank=True) #users thoughts about a book
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="post_likes", blank=True) #Users like on a book

    def __str__(self):
        return f"{self.user.username}'s post about {self.book.title}"
    

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment By {self.user.username}'s on {self.post.book.title}"
    

class Rating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)]) #rating between 1 and 5

    def __str__(self):
        return f"{self.user.username} rated {self.book.title} {self.rating}/5"
    
    