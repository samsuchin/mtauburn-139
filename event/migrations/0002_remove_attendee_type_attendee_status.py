# Generated by Django 4.2 on 2024-03-28 01:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendee',
            name='type',
        ),
        migrations.AddField(
            model_name='attendee',
            name='status',
            field=models.CharField(default='Default', max_length=50),
        ),
    ]
