# Generated by Django 2.1 on 2019-09-03 10:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0009_auto_20190903_1313'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='author',
            name='catalog_aut_last_na_73102a_idx',
        ),
        migrations.RemoveIndex(
            model_name='author',
            name='first_name_idx',
        ),
    ]
