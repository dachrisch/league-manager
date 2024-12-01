# Generated by Django 5.0.4 on 2024-11-10 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamedays', '0021_gameday_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('sex', models.IntegerField(blank=True, choices=[(1, 'Weiblich'), (2, 'Männlich')], default=None, null=True)),
                ('year_of_birth', models.PositiveIntegerField(blank=True, default=None, null=True)),
            ],
        ),
    ]
