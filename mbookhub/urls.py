from django.urls import path
from .views import CustomLoginView, signup, add_book,book_list,profile,addbook
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.book_list, name = 'book_list'),
    path('add/', views.add_book, name= 'add'),
    path('signup/', views.signup, name= 'signup'),
    path('login/', CustomLoginView.as_view(template_name='mbook/login.html'), name='login' ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.addbook, name='search'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
