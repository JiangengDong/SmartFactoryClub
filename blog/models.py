# -*- coding: UTF-8 -*-
import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone, datetime_safe
from django.urls import reverse
import markdown
from xpinyin import Pinyin
import datetime


class Category(models.Model):
    name = models.CharField(max_length=64, verbose_name='分类')

    def numArticle(self):
        return self.article_set.count()

    numArticle.short_description = '文章数量'

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        os.removedirs(os.path.join(settings.MEDIA_ROOT, str(self.id)))
        return super().delete(using, keep_parents)

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'categoryName': self.name})

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

    def hasPublished(self):
        if self.timePublish < timezone.now():
            return 'Publish'
        else:
            return 'Draft'

    hasPublished.short_description = '发布状态'

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.timePublish = self.timePublish or (timezone.now() + datetime.timedelta(days=3650))
        self.timeCreate = self.timeCreate or timezone.now()
        self.timeModify = timezone.now()
        self.body = markdown.markdown(self.MarkdownBody)
        return super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        os.removedirs(os.path.join(settings.MEDIA_ROOT, str(self.category.id), str(self.id)))
        return super().delete(using, keep_parents)

    def get_absolute_url(self):
        return reverse('blog:article', kwargs={'categoryName': self.category.name, 'articleTitle': self.title})

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'


def storage_redirect(instance, name):
    article = instance.article
    category = article.category
    ext = name.split('.')[-1]
    name = Pinyin().get_pinyin(instance.name, '_') + '.' + ext
    return os.path.join(str(category.id), str(article.id), name)


class Picture(models.Model):
    name = models.CharField(max_length=64, verbose_name='图片名称')
    img = models.ImageField(upload_to=storage_redirect, verbose_name='图片')
    url = models.CharField(max_length=64, blank=True)

    timeCreate = models.DateTimeField(verbose_name='创建时间', default=timezone.now, editable=False)
    painter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='painter', verbose_name='创建者', editable=False)

    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='文章')

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.timeCreate = timezone.now()
        super().save(force_insert, force_update, using, update_fields)
        self.url = self.img.url
        return super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.img.name))
        return super().delete(using, keep_parents)

    class Meta:
        verbose_name = '图片'
        verbose_name_plural = '图片'
