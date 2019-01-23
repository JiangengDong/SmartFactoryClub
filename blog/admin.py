# -*- coding: UTF-8 -*-
from django.contrib import admin
from django.conf import settings
from .models import Category, Article, Picture


class ArticleAdminInline(admin.TabularInline):
    model = Article
    fields = ['title', 'timePublish', 'modifier', 'timeModify', 'author', 'timeCreate']
    extra = 1
    readonly_fields = ['timePublish', 'modifier', 'timeModify', 'author', 'timeCreate']
    show_change_link = True


class PictureAdminInline(admin.TabularInline):
    model = Picture
    fields = ['name', 'img', 'url']
    extra = 1
    readonly_fields = ['url']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ['name', 'group']
    list_display = ['id', 'name', 'group', 'timeModify', 'numArticle']
    list_editable = ['name', 'group']
    inlines = [ArticleAdminInline]

    def save_model(self, request, obj, form, change):
        return super().save_related(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        if formsets:
            formset = formsets[0]
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
                obj.delete()
            for instance in instances:
                instance.author = instance.author or request.user
                instance.modifier = request.user
                instance.save()
            formsets = formsets[1:]
        super().save_related(request, form, formsets, change)

    def delete_queryset(self, request, queryset):
        for obj in queryset.all():
            obj.delete()


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    fields = ['title', 'category', 'MarkdownBody', 'timePublish']
    list_display = ['title', 'category', 'hasPublished', 'timePublish', 'modifier', 'timeModify']
    list_editable = ['category']
    list_filter = ['modifier', 'category__name', 'timePublish']
    inlines = [PictureAdminInline]

    def save_model(self, request, obj, form, change):
        obj.author = obj.author or request.user
        obj.modifier = request.user
        obj.save()

    def save_related(self, request, form, formsets, change):
        if formsets:
            formset = formsets[0]
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
                obj.delete()
            for instance in instances:
                instance.painter = request.user
                instance.save()
            formsets = formsets[1:]
        super().save_related(request, form, formsets, change)

    def delete_queryset(self, request, queryset):
        for obj in queryset.all():
            obj.delete()


@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    fields = ['name', 'img', 'url', 'article']
    list_display = ['name', 'url', 'article', 'painter', 'timeCreate']
    list_editable = ['article']
    list_filter = ['article__category__name', 'painter', 'timeCreate']
    readonly_fields = ['url']

    def save_model(self, request, obj, form, change):
        obj.painter = obj.painter or request.user
        obj.save()

    def delete_queryset(self, request, queryset):
        for obj in queryset.all():
            obj.delete()


admin.site.site_header = settings.SITE_NAME
admin.site.site_title = settings.SITE_NAME
