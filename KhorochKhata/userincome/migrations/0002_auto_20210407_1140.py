# Generated by Django 3.1.7 on 2021-04-07 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userincome', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='userincome',
            name='source',
            field=models.CharField(max_length=266),
        ),
    ]
