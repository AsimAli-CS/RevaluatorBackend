# Generated by Django 5.0.1 on 2024-04-04 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authAPI', '0005_alter_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='otp',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
