# Generated by Django 4.2 on 2024-03-28 02:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0002_remove_attendee_type_attendee_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Error',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField(max_length=1000)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timelines', to='event.event')),
            ],
        ),
    ]
