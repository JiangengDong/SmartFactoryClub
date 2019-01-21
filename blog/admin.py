from django.contrib import admin
from django.utils import timezone
from django.conf import settings
from .models import Category, Article
import markdown


@admin.register(Category)
class SectionAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ['name', 'numArticle']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    fields = ['title', 'category', 'MarkdownBody', 'timePublish']
    list_display = ['title', 'category', 'timePublish', 'modifier', 'timeModify', 'author', 'timeCreate']
    list_filter = ('author', 'modifier', 'category__name', 'timePublish')

    def save_model(self, request, obj, form, change):
        obj.timeCreate = obj.timeCreate or timezone.now()
        obj.timeModify = timezone.now()
        obj.author = obj.author or request.user
        obj.modifier = request.user
        obj.body = markdown.markdown(obj.MarkdownBody)
        obj.save()

admin.site.site_header = settings.SITE_NAME
admin.site.site_title = settings.SITE_NAME
