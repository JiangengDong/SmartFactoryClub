# -*- coding: UTF-8 -*-
import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone, datetime_safe
from django.urls import reverse
import markdown
from xpinyin import Pinyin
import datetime


class Category(models.Model):
    # field that are editable
    name = models.CharField(max_length=64,
                            verbose_name='分类')
    group = models.ForeignKey(to=Group,
                              on_delete=models.SET_NULL,
                              null=True,
                              verbose_name='用户组')

    # fields that are not editable (used to record)
    timeModify = models.DateTimeField(default=timezone.now,
                                      verbose_name='上次修改时间',
                                      editable=False)

    # methods for getting attribution
    def numArticle(self):
        return self.article_set.count()

    numArticle.short_description = '文章数量'

    # methods for better display
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'categoryName': self.name})

    # pre- and post- operations
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.timeModify = timezone.now()
        return super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        os.removedirs(os.path.join(settings.MEDIA_ROOT, str(self.id)))
        return super().delete(using, keep_parents)

    # A user-friendly name for this model
    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'


class Article(models.Model):
    # field that are editable
    title = models.CharField(max_length=64,
                             verbose_name='网页标题')
    MarkdownBody = models.TextField(default=' ',
                                    null=True,
                                    blank=True,
                                    verbose_name='正文')
    timePublish = models.DateTimeField(verbose_name='发布时间')
    category = models.ForeignKey(to=Category,
                                 on_delete=models.CASCADE,
                                 verbose_name='类别')
    # fields that are not editable (used to record)
    author = models.ForeignKey(to=User,
                               on_delete=models.SET_NULL,
                               null=True,
                               related_name='author',
                               verbose_name='创建者',
                               editable=False)
    modifier = models.ForeignKey(to=User,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 related_name='modifier',
                                 verbose_name='修改者',
                                 editable=False)
    timeCreate = models.DateTimeField(verbose_name='创建时间',
                                      editable=False)
    timeModify = models.DateTimeField(verbose_name='上次修改时间',
                                      editable=False)
    body = models.TextField(default=' ',
                            null=True,
                            blank=True,
                            editable=False)

    # methods for getting attribution
    def hasPublished(self):
        if self.timePublish < timezone.now():
            return 'Publish'
        else:
            return 'Draft'

    hasPublished.short_description = '发布状态'

    # methods for better display
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:article', kwargs={'categoryName': self.category.name, 'articleTitle': self.title})

    # pre- and post- operations
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.timePublish = self.timePublish or (timezone.now() + datetime.timedelta(days=3650))
        self.timeCreate = self.timeCreate or timezone.now()
        self.timeModify = timezone.now()
        self.body = markdown.markdown(self.MarkdownBody)
        self.category.save()
        return super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        os.removedirs(os.path.join(settings.MEDIA_ROOT, str(self.category.id), str(self.id)))
        return super().delete(using, keep_parents)

    # A user-friendly name for this model
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
    # field that are editable
    name = models.CharField(max_length=64,
                            verbose_name='图片名称')
    img = models.ImageField(upload_to=storage_redirect,
                            verbose_name='图片')
    article = models.ForeignKey(to=Article,
                                on_delete=models.CASCADE,
                                verbose_name='文章')
    # fields that are not editable (used to record)
    url = models.CharField(max_length=64,
                           blank=True,
                           editable=False)
    timeCreate = models.DateTimeField(verbose_name='创建时间',
                                      default=timezone.now,
                                      editable=False)
    painter = models.ForeignKey(to=User,
                                on_delete=models.SET_NULL,
                                null=True,
                                related_name='painter',
                                verbose_name='创建者',
                                editable=False)

    # methods for better display
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.url

    # pre- and post- operations
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.timeCreate = timezone.now()
        self.article.save()
        super().save(force_insert, force_update, using, update_fields)
        self.url = self.img.url
        return super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.img.name))
        return super().delete(using, keep_parents)

    # A user-friendly name for this model
    class Meta:
        verbose_name = '图片'
        verbose_name_plural = '图片'
