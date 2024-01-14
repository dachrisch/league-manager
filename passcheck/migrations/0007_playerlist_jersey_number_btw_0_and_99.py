# Generated by Django 4.1.7 on 2024-01-14 11:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('passcheck', '0006_playerlist_unique team_jersey_number_and_more'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='playerlist',
            constraint=models.CheckConstraint(check=models.Q(('jersey_number__gte', 0), ('jersey_number__lte', 99)),
                                              name='jersey_number_btw_0_and_99'),
        ),
    ]
