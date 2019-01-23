# Generated by Django 2.1.4 on 2019-01-23 17:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_category_timemodify'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='author',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='author', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AlterField(
            model_name='article',
            name='body',
            field=models.TextField(blank=True, default=' ', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='modifier',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='modifier', to=settings.AUTH_USER_MODEL, verbose_name='修改者'),
        ),
        migrations.AlterField(
            model_name='article',
            name='timeCreate',
            field=models.DateTimeField(editable=False, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='article',
            name='timeModify',
            field=models.DateTimeField(editable=False, verbose_name='上次修改时间'),
        ),
        migrations.AlterField(
            model_name='category',
            name='timeModify',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='上次修改时间'),
        ),
        migrations.AlterField(
            model_name='picture',
            name='url',
            field=models.CharField(blank=True, editable=False, max_length=64),
        ),
    ]
