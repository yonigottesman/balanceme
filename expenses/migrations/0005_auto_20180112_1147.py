# Generated by Django 2.0.1 on 2018-01-12 11:47

from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('expenses', '0004_knownkeywords'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Catagory',
            new_name='Category',
        ),
        migrations.RenameModel(
            old_name='SubCatagory',
            new_name='SubCategory',
        ),
    ]