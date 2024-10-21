from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    genre = models.CharField(max_length= 15)
    description = models.TextField()
    isbn = models.CharField(max_length=13, unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)

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

