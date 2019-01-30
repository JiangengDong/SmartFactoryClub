# -*- coding: UTF-8 -*-
import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone, datetime_safe
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
import markdown
from xpinyin import Pinyin
import datetime
import re
import shutil


def convertToAscii(str, forbidden=r'[\\\-\"\'/:*?<>|,@#$&();+.!%]'):
    return re.sub('[^\x00-\xff]', '_',
                  re.sub(forbidden, '_',
                         Pinyin().get_pinyin(str, "")))

def storage_redirect(instance, name):
    name = convertToAscii(instance.name) + '.' + name.split('.')[-1]
    ids = list(map(str, instance.article.category.get_ancestors(include_self=True).values_list('id', flat=True)))
    path = os.path.join(*ids)
    return os.path.join(path, str(instance.article_id), name)


class CommonInfo(models.Model):
    # editable
    name = models.CharField(max_length=25,
                            blank=False,
                            verbose_name='名称',
                            help_text='不允许与其他条目重复。')
    # not editable (used to record)
    timeModify = models.DateTimeField(default=timezone.now,
                                      editable=False,
                                      verbose_name='修改时间')
    userModify = models.ForeignKey(to=User,
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   editable=False,
                                   related_name='%(class)s_modified',
                                   verbose_name='修改者')
    timeCreate = models.DateTimeField(default=timezone.now,
                                      editable=False,
                                      verbose_name='创建时间')
    userCreate = models.ForeignKey(to=User,
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   editable=False,
                                   related_name='%(class)s_created',
                                   verbose_name='创建者')

    class Meta:
        abstract = True
        db_table = '%(app_label)s_%(class)s'


class Category(MPTTModel, CommonInfo):
    # Tree
    parent = TreeForeignKey(to='self',
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True,
                            related_name='children',
                            verbose_name='上级目录',
                            help_text='若上级目录为空，则此目录为顶级目录。')
    group = models.ForeignKey(to=Group,
                              on_delete=models.SET_NULL,
                              blank=True,
                              null=True,
                              verbose_name='组',
                              help_text='组内用户有此条目下文章的编辑权限。')
    level = models.PositiveIntegerField(default=0,
                                        editable=False,
                                        verbose_name='等级')


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if self.is_root_node():
            if self.children.exists():
                return self.children.first().get_absolute_url()
            elif self.article_set.exists():
                return self.article_set.first().get_absolute_url()
            else:
                return '#'
        elif self.level == 1:
            return reverse('blog:subcategory', kwargs={'cat': self.parent.name, 'sub': self.name})
        else:
            return '#'

    class MPTTMeta:
        order_insertion_by = []
        level_attr = 'level'

    class Meta:
        verbose_name = '目录'
        verbose_name_plural = '目录'


class Article(CommonInfo):
    category = TreeForeignKey(to=Category,
                              on_delete=models.CASCADE,
                              null=True,
                              verbose_name='类别')
    markdownBody = models.TextField(default=' ',
                                    blank=True,
                                    verbose_name='正文')
    timePublish = models.DateTimeField(blank=True,
                                       null=True,
                                       verbose_name='发布时间')
    status = models.BooleanField(default=False,
                                 verbose_name='发布状态')
    body = models.TextField(default=' ',
                            blank=True,
                            editable=False)

    def __str__(self):
        ancestors = self.category.get_ancestors(include_self=True).values_list('name', flat=True)
        categoryPath = '/'.join(ancestors)
        return '/'.join([categoryPath, self.name])

    def get_absolute_url(self):
        if self.category.is_root_node():
            return reverse('blog:article1', kwargs={'cat': self.category.name, 'art': self.name})
        elif self.category.level == 1:
            return reverse('blog:article2', kwargs={'cat': self.category.parent.name,
                                                    'sub': self.category.name,
                                                    'art': self.name})
        else:
            return '#'


    class Meta:
        verbose_name_plural = '文章'
        verbose_name = '文章'
        permissions = (
            ('publish_article', 'Can publish 文章'),
        )


class Resource(CommonInfo):
    file = models.FileField(upload_to=storage_redirect,
                            verbose_name='文件')
    article = models.ForeignKey(to=Article,
                                on_delete=models.CASCADE,
                                verbose_name='文章')
    url = models.CharField(max_length=64,
                           blank=True,
                           editable=False,
                           verbose_name='访问路径')

    def __str__(self):
        return str(self.article) + '/' + self.name

    def get_absolute_url(self):
        return self.url

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        self.url = self.file.url
        return super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        args = [settings.MEDIA_ROOT] + self.url.split('/')[2:]
        path = os.path.join(*args)
        if os.path.exists(path):
            os.remove(path)
        return super().delete(using, keep_parents)

    class Meta:
        verbose_name_plural = '资源'
        verbose_name = '资源'