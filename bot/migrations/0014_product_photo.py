# Generated by Django 5.0.1 on 2024-01-16 14:53

import pathlib
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0013_comment_name_of_product_alter_comment_count_of_stars'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='photo',
            field=models.ImageField(null=True, upload_to=pathlib.PureWindowsPath('C:/Users/`/Desktop/narkNarkReborn/media'), verbose_name='Фото товара'),
        ),
    ]
