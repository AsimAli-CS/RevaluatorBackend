# Generated by Django 5.0.1 on 2024-05-31 19:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authAPI', '0006_user_otp'),
        ('revapp', '0004_candidate_skills'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='recruiterId',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='authAPI.user'),
        ),
    ]
