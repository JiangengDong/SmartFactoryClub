from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils import timezone
from .models import Category, Article


def indexView(request, **kwargs):
    context = {}
    context['active_navbar'] = {'name': '首页', 'sub': {'name': ''}}
    return render(request, 'blog/index.html', context)


class SubCategoryView(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'articles'
    paginate_by = 1

    def get_queryset(self):
        self.category = get_object_or_404(Category, name=self.kwargs['cat'])
        self.subcategory = get_object_or_404(self.category.children, name=self.kwargs['sub'])
        return self.subcategory.article_set.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_navbar'] = {'name': self.category.name, 'sub': {'name': self.subcategory.name}}
        context['category'] = self.subcategory
        return context


class ArticleView(DetailView):
    template_name = 'blog/article.html'
    context_object_name = 'article'

    def get_queryset(self):
        self.category = get_object_or_404(Category, name=self.kwargs['cat'])
        if 'sub' in self.kwargs.keys():
            self.subcategory = get_object_or_404(self.category.children, name=self.kwargs['sub'])
        else:
            self.subcategory = None
        return (self.subcategory or self.category).article_set

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        self.article = get_object_or_404(queryset, name=self.kwargs['art'])
        return self.article

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_navbar'] = {'name': self.category.name, 'sub': {'name': (self.subcategory or self.article).name}}
        context['breadcrumb'] = [self.category, self.subcategory, self.article] if self.subcategory \
            else [self.category, self.article]
        return context