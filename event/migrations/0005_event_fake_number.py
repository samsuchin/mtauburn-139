# Generated by Django 4.2 on 2024-04-13 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0004_event_email_subject'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='fake_number',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
