# Generated by Django 3.2.2 on 2021-05-12 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_botuser_pocket_access_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='pocket_username',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]