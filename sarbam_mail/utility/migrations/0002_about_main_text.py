# Generated by Django 5.1.4 on 2025-01-22 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utility', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='about',
            name='main_text',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
    ]
