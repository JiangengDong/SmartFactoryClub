# Generated by Django 2.1.4 on 2019-01-23 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='picture',
            name='url',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
