from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from .models import Article, Category

def indexView(request):
    article = get_object_or_404(Article, pk=2)
    context = {'article': article}
    return render(request, 'blog/index.html', context)

def categoryView(request, categoryName):
    category = get_object_or_404(Category, name=categoryName)
    return HttpResponse('not finished')

def articleView(request, categoryName, articleTitle):
    category = get_object_or_404(Category, name=categoryName)
    article = get_object_or_404(Article, title=articleTitle)
    return render(request, '')

class CategoryView(ListView):
    queryset = Category
    template_name = ''

