# Generated by Django 5.1.1 on 2024-10-26 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_add_status_vehicle'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicletype',
            name='image',
            field=models.ImageField(
                default='vehicle_types/bike.webp', upload_to='vehicle_types/'
            ),
            preserve_default=False,
        ),
    ]
