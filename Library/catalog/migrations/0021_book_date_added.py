# Generated by Django 2.1 on 2019-09-07 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0020_genre_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='date_added',
            field=models.DateField(blank=True, null=True),
        ),
    ]
