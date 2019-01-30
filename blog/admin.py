# -*- coding: UTF-8 -*-
from django.contrib import admin, messages
from mptt.admin import DraggableMPTTAdmin, TreeRelatedFieldListFilter
from django.conf import settings
from django.utils import timezone
from .models import Category, Article, Resource
import datetime
from markdown import markdown

"""
The following three classes work for the category editing pages.
"""


class ArticleInline(admin.TabularInline):
    model = Article
    fields = ['name', 'status', 'timePublish']
    readonly_fields = ['status', 'timePublish']
    show_change_link = True
    extra = 0


class CategoryInline(admin.TabularInline):
    model = Category
    fields = ['name', 'group', 'related_articles_count']
    readonly_fields = ['group', 'related_articles_count']
    show_change_link = True
    extra = 0

    # add additional attributes
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = Category.objects.add_related_count(qs, Article, 'category', 'articles_cumulative_count', cumulative=True)
        return qs

    def related_articles_count(self, instance):
        return instance.articles_cumulative_count

    related_articles_count.short_description = '文章数量'


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    mptt_level_indent = 20
    expand_tree_by_default = True

    # changelist view
    list_display = ['tree_actions',
                    'indented_title',
                    'group',
                    'related_articles_count',
                    'userModify',
                    'timeModify']
    list_display_links = ['indented_title']
    list_filter = ['level', 'group', 'timeModify']
    list_editable = ['group']
    list_select_related = ['group']

    # records displayed on the changelist view
    def get_queryset(self, request):
        roots = Category.objects.root_nodes()
        if not request.user.is_superuser:
            roots = roots.filter(group_id__in=request.user.groups.values_list('id', flat=True))
        qs = super().get_queryset(request).filter(tree_id__in=roots.values_list('tree_id', flat=True))
        qs = Category.objects.add_related_count(qs, Article, 'category', 'articles_cumulative_count', cumulative=True)
        return qs

    # additional attributes
    def related_articles_count(self, instance):
        return instance.articles_cumulative_count

    related_articles_count.short_description = '文章数量'

    # foreignkey display behavior
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.model == Category and db_field.name == 'parent':
            if 'queryset' not in kwargs:
                queryset = Category.objects.all() if request.user.is_superuser \
                    else Category.objects.filter(group__in=request.user.groups.all())
                if queryset is not None:
                    kwargs['queryset'] = queryset
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # add/change view
    fields = ['name', 'parent', 'group']
    inlines = [ArticleInline, CategoryInline]

    # save behaviors
    ## save category
    def save_model(self, request, obj, form, change):
        t = timezone.now()
        obj.timeModify = t
        obj.userModify = request.user
        obj.timeCreate = obj.timeCreate or t
        obj.userCreate = obj.userCreate or request.user
        if obj.is_root_node():
            if change:
                obj.get_descendants().update(group=obj.group)
            else:
                pass
        else:
            obj.group = obj.parent.group
        obj.save()

    ## save inline articles and subcategories
    def save_formset(self, request, form, formset, change):
        t = timezone.now()
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for obj in instances:
            obj.timeModify = t
            obj.userModify = request.user
            obj.timeCreate = obj.timeCreate or t
            obj.userCreate = obj.userCreate or request.user
            if formset.model is Category:
                obj.group = obj.parent.group
            obj.save()


"""
The following two classes work for the article editing pages.
"""


class ResourceInline(admin.TabularInline):
    model = Resource
    fields = ['name', 'file', 'url']
    readonly_fields = ['url']
    show_change_link = True
    extra = 0

    # permission control
    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return not obj or not obj.status and super().has_delete_permission(request, obj)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # changelist view
    list_display = ['name', 'category', 'status', 'timePublish', 'userModify', 'timeModify']
    list_filter = [('category', TreeRelatedFieldListFilter), 'status', 'timePublish', 'userModify']
    list_editable = ['category']
    list_select_related = ['category']

    # add/change view
    fields = ['name', 'category', 'markdownBody', 'timePublish']
    inlines = [ResourceInline]

    # fields displayed in changelist view
    def get_fields(self, request, obj=None):
        if request.user.has_perm('blog:publish_article'):
            return self.fields + ['status']
        else:
            return self.fields

    # records displayed on the changelist view
    def get_queryset(self, request):
        roots = Category.objects.root_nodes()
        if not request.user.is_superuser:
            roots = roots.filter(group_id__in=request.user.groups.values_list('id', flat=True))
        qs = super().get_queryset(request).filter(category__tree_id__in=roots.values_list('tree_id', flat=True))
        return qs

    # foreignkey display behavior
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.model == Article and db_field.name == 'category':
            if 'queryset' not in kwargs:
                queryset = Category.objects.all() if request.user.is_superuser \
                    else Category.objects.filter(group__in=request.user.groups.all())
                if queryset is not None:
                    kwargs['queryset'] = queryset
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # save behaviors
    ## save article
    def save_model(self, request, obj, form, change):
        t = timezone.now()
        obj.timeModify = t
        obj.userModify = request.user
        obj.timeCreate = obj.timeCreate or t
        obj.userCreate = obj.userCreate or request.user
        obj.body = markdown(obj.markdownBody)
        if obj.status and obj.timePublish is None:
            obj.status = False
            msg = '未设置发布时间，不能发布。'
            self.message_user(request, msg, messages.ERROR)
        # if obj.status and 'status' in form.changed_data:
        #     obj.timePublish = max(t, obj.timePublish)
        obj.save()

    ## save inline resources
    def save_formset(self, request, form, formset, change):
        t = timezone.now()
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for obj in instances:
            obj.timeModify = t
            obj.userModify = request.user
            obj.timeCreate = obj.timeCreate or t
            obj.userCreate = obj.userCreate or request.user
            obj.save()

    # permission control
    def has_change_permission(self, request, obj=None):
        return not obj or not obj.status and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return not obj or not obj.status and super().has_delete_permission(request, obj)

    # queryset actions
    actions = ['withdraw_queryset', 'publish_queryset', 'publish_queryset_immediately']
    def withdraw_queryset(self, request, queryset):
        if request.user.has_perm('blog:publish_article'):
            qs = queryset.filter(status=True)
            msg = '成功撤稿%d篇文章' % qs.count()
            qs.update(status=False)
            self.message_user(request, msg, messages.SUCCESS)
    withdraw_queryset.short_description = '撤稿'

    def publish_queryset(self, request, queryset):
        if request.user.has_perm('blog:publish_article'):
            t = timezone.now()
            qs = queryset.filter(status=False, timePublish__isnull=False)
            msg = '成功延时发布%d篇文章。' % qs.count()
            # qs.filter(timePublish__lte=t).update(timePublish=t)
            qs.update(status=True)
            self.message_user(request, msg, messages.SUCCESS)
            qs = queryset.filter(timePublish__isnull=True)
            for obj in qs:
                msg = '%s没有指定发布时间，不能延时发布。' % obj.name
                self.message_user(request, msg, messages.ERROR)
    publish_queryset.short_description = '延时发布'

    def publish_queryset_immediately(self, request, queryset):
        if request.user.has_perm('blog:publish_article'):
            t = timezone.now()
            qs = queryset.filter(status=False)
            msg = '成功发布%d篇文章。' % qs.count()
            qs.update(status=True, timePublish=t)
            self.message_user(request, msg, messages.SUCCESS)
    publish_queryset_immediately.short_description = '立即发布'



"""
The following class works for the resources editing pages.
"""


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    # changelist view
    list_display = ['name', 'article', 'url', 'userCreate', 'timeCreate']
    list_select_related = ['article']
    list_filter = [('article__category', TreeRelatedFieldListFilter), 'article__timePublish']

    # add/change view
    fields = ['name', 'article', 'file']

    # records displayed on the changelist view
    def get_queryset(self, request):
        roots = Category.objects.root_nodes()
        if not request.user.is_superuser:
            roots = roots.filter(group_id__in=request.user.groups.values_list('id', flat=True))
        qs = super().get_queryset(request).filter(
            article__category__tree_id__in=roots.values_list('tree_id', flat=True))
        return qs

    # foreignkey display behavior
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.model == Resource and db_field.name == 'article':
            if 'queryset' not in kwargs:
                queryset = Article.objects.all() if request.user.is_superuser \
                    else Article.objects.filter(category__group__in=request.user.groups.all())
                if queryset is not None:
                    kwargs['queryset'] = queryset
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # permission control
    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return not obj or not obj.article.status and super().has_delete_permission(request, obj)


admin.site.site_header = '智能工厂创新俱乐部'
admin.site.site_title = '智能工厂创新俱乐部'
