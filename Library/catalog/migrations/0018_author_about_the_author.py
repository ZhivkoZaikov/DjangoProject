# Generated by Django 2.1 on 2019-09-04 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0017_author_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='about_the_author',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]