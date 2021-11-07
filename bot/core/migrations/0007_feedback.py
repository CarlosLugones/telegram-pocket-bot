# Generated by Django 3.2.2 on 2021-05-12 06:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_stats'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('bot_user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.botuser')),
            ],
        ),
    ]