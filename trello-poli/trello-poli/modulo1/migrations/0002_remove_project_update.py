# Generated by Django 4.1 on 2022-08-22 15:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('modulo1', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='update',
        ),
    ]
