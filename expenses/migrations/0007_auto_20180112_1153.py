# Generated by Django 2.0.1 on 2018-01-12 11:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('expenses', '0006_auto_20180112_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='subcatagory',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='expenses.SubCategory'),
        ),
    ]