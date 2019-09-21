# Generated by Django 2.1 on 2019-09-03 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_auto_20190903_0215'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='author',
            index=models.Index(fields=['last_name', 'first_name'], name='catalog_aut_last_na_73102a_idx'),
        ),
        migrations.AddIndex(
            model_name='author',
            index=models.Index(fields=['first_name'], name='first_name_idx'),
        ),
    ]