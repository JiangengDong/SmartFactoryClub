from django.urls import path

from . import views
from .models import Category

app_name = 'blog'
urlpatterns = [
    path('<str:categoryName>/', views.CategoryView.as_view(), name='category'),
    path('<str:categoryName>/<str:articleTitle>', views.ArticleView.as_view(), name='article'),
    path('', views.indexView, name='index'),
]