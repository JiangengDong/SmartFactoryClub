from django.urls import path

from . import views
from .models import Category

app_name = 'blog'
urlpatterns = [
    path('<str:categoryName>/', views.categoryView, name='category'),
    path('<str:categoryName>/<str:articleTitle>', views.articleView, name='article'),
    path('', views.indexView, name='index'),
]