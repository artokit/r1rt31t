# Generated by Django 5.0.1 on 2024-01-18 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0018_typeofbuy_pack_type_of_buy'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentcrypto',
            name='qr_code_image',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='QR-код для оплаты'),
        ),
    ]