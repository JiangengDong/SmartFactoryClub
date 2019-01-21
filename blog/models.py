from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=64, verbose_name='分类')

    def numArticle(self):
        return self.article_set.count()

    numArticle.short_description = '文章数量'

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'


class Article(models.Model):
    title = models.CharField(max_length=64, verbose_name='网页标题')
    MarkdownBody = models.TextField(default=' ', null=True, blank=True, verbose_name='正文')
    body = models.TextField(default=' ', null=True, blank=True)

    timeCreate = models.DateTimeField(verbose_name='创建时间')
    timeModify = models.DateTimeField(verbose_name='上次修改时间')
    timePublish = models.DateTimeField(verbose_name='发布时间')

    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='类别')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='author', verbose_name='创建者')
    modifier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='modifier', verbose_name='修改者')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
