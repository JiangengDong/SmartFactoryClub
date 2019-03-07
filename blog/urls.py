from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.indexView, name='index'),
    path('cat_<int:cat>/sub_<int:sub>/', views.SubCategoryView.as_view(), name='subcategory'),
    path('cat_<int:cat>/art_<int:art>/', views.ArticleView.as_view(), name='article1'),
    path('cat_<int:cat>/sub_<int:sub>/art_<int:art>/', views.ArticleView.as_view(), name='article2'),
]