# Generated by Django 2.1 on 2019-09-03 13:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0015_auto_20190903_1638'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookinstance',
            options={'ordering': ['book__title', '-due_back'], 'permissions': (('can_mark_returned', 'Set book as returned'),)},
        ),
    ]
