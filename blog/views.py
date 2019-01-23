from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from .models import Article, Category

def indexView(request):
    article = get_object_or_404(Article, pk=2)
    context = {'article': article}
    return render(request, 'blog/index.html', context)

class CategoryView(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'articles'

    def get_queryset(self):
        self.category = get_object_or_404(Category, name=self.kwargs['categoryName'])
        return Article.objects.filter(category=self.category)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ArticleView(DetailView):
    template_name = 'blog/article.html'
    context_object_name = 'article'

    def get_queryset(self):
        self.category = get_object_or_404(Category, name=self.kwargs['categoryName'])
        return Article.objects.filter(category=self.category)

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, title=self.kwargs['articleTitle'])