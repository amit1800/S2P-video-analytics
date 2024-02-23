# Generated by Django 5.0.1 on 2024-02-23 06:17

import django.db.models.deletion
import multiselectfield.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_remove_cuser_streamnames'),
    ]

    operations = [
        migrations.CreateModel(
            name='Detection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', multiselectfield.db.fields.MultiSelectField(choices=[('human', 'human'), ('fire', 'fire'), ('weapon', 'weapon'), ('numberplate', 'numberplate')], default=None, max_length=2048)),
                ('value', models.TextField(max_length=30)),
                ('date_time', models.DateTimeField(auto_now=True)),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.track')),
            ],
        ),
    ]