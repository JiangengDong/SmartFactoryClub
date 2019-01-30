from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.indexView, name='index'),
    path('cat_<str:cat>/sub_<str:sub>/', views.SubCategoryView.as_view(), name='subcategory'),
    path('cat_<str:cat>/art_<str:art>/', views.ArticleView.as_view(), name='article1'),
    path('cat_<str:cat>/sub_<str:sub>/art_<str:art>/', views.ArticleView.as_view(), name='article2'),
]