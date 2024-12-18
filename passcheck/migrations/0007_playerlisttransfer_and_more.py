# Generated by Django 5.0.4 on 2024-12-06 12:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamedays', '0022_person'),
        ('passcheck', '0006_remove_playerlist_unique_team_jersey_number_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerlistTransfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('approval_date', models.DateTimeField(blank=True, default=None, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('note', models.TextField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.RemoveConstraint(
            model_name='playerlist',
            name='unique_team_jersey_number',
        ),
        migrations.AlterField(
            model_name='playerlist',
            name='jersey_number',
            field=models.IntegerField(null=True),
        ),
        migrations.AddConstraint(
            model_name='playerlist',
            constraint=models.UniqueConstraint(condition=models.Q(('left_on', None), models.Q(('jersey_number', None), _negated=True)), fields=('team', 'jersey_number'), name='unique_team_jersey_number'),
        ),
        migrations.AddField(
            model_name='playerlisttransfer',
            name='approved_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='playerlisttransfer',
            name='current_team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='passcheck.playerlist'),
        ),
        migrations.AddField(
            model_name='playerlisttransfer',
            name='new_team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamedays.team'),
        ),
    ]
