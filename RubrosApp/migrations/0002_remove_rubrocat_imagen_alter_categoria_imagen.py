# Generated by Django 5.2 on 2025-05-23 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RubrosApp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rubrocat',
            name='imagen',
        ),
        migrations.AlterField(
            model_name='categoria',
            name='imagen',
            field=models.ImageField(upload_to='RubrosMedia', verbose_name='Imagen'),
        ),
    ]
