# Generated by Django 2.1 on 2019-09-02 23:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_auto_20190902_1233'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'verbose_name': 'Bookies', 'verbose_name_plural': 'Bookers'},
        ),
    ]