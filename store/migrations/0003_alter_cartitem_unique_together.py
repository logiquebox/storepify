# Generated by Django 4.0.2 on 2022-02-18 12:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_cart_id_alter_cartitem_cart'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cartitem',
            unique_together={('cart', 'product')},
        ),
    ]