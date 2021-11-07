# Generated by Django 3.2.2 on 2021-05-12 00:05

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BotUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('chat_id', models.CharField(max_length=255)),
                ('username', models.CharField(blank=True, max_length=255, null=True)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('has_blocked_bot', models.BooleanField(default=False)),
                ('last_action_datetime', models.DateTimeField(blank=True, null=True)),
                ('accepted_tos', models.BooleanField(default=False)),
                ('language', models.CharField(blank=True, choices=[('ES', 'es'), ('EN', 'en')], default=None, max_length=2, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
