# Generated by Django 5.1.1 on 2024-12-05 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roadmap', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='milestone',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]