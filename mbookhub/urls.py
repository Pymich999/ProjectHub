from django.urls import path
from .views import CustomLoginView, signup,book_list,profile,addbook,like_post
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.book_list, name = 'book_list'),
    path('signup/', views.signup, name= 'signup'),
    path('login/', CustomLoginView.as_view(template_name='mbook/login.html'), name='login' ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.addbook, name='search'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('create-post/<int:book_id>/', views.create_post, name='create_post'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
