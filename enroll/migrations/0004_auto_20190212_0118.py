# Generated by Django 2.1.4 on 2019-02-11 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enroll', '0003_auto_20190212_0100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='order',
            field=models.IntegerField(default=3, verbose_name='题号'),
        ),
    ]