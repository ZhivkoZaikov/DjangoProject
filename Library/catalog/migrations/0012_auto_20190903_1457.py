# Generated by Django 2.1 on 2019-09-03 11:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0011_book_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'verbose_name': 'Book singular', 'verbose_name_plural': 'Book plural'},
        ),
    ]
