# Generated by Django 2.0.1 on 2018-01-27 05:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0017_auto_20180127_0508'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subcategory',
            old_name='catagory',
            new_name='category',
        ),
    ]
