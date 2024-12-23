# Generated by Django 5.1.1 on 2024-10-10 10:03

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=255)),
                ('post_code', models.CharField(max_length=10)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='VehicleType',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('model', models.CharField(max_length=100)),
                ('brand', models.CharField(max_length=100)),
                ('description', models.TextField()),
                (
                    'rate',
                    models.DecimalField(
                        decimal_places=2, help_text='Hourly rental rate', max_digits=5
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                (
                    'code',
                    models.CharField(
                        max_length=6, primary_key=True, serialize=False, unique=True
                    ),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[('available', 'Available'), ('in_use', 'In use')],
                        max_length=10,
                    ),
                ),
                (
                    'battery_level',
                    models.IntegerField(
                        default=100,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'location',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='vehicles',
                        to='core.location',
                    ),
                ),
                (
                    'type',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='vehicles',
                        to='core.vehicletype',
                    ),
                ),
            ],
        ),
    ]
