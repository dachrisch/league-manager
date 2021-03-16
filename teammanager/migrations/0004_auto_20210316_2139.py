# Generated by Django 3.1.5 on 2021-03-16 20:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teammanager', '0003_auto_20210309_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='teamlog',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='teamlog',
            name='created_time',
            field=models.TimeField(default=django.utils.timezone.now),
        ),
    ]
