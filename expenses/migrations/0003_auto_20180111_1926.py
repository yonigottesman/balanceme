# Generated by Django 2.0.1 on 2018-01-11 19:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0002_auto_20180111_1446'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subcatagory',
            old_name='Catagory',
            new_name='catagory',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='txn_tag',
        ),
        migrations.AddField(
            model_name='transaction',
            name='subcatagory',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='expenses.SubCatagory'),
        ),
    ]
