# Generated by Django 5.1.3 on 2025-02-06 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_bairro_quantidade_reclamacoes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='email',
            field=models.EmailField(blank=True, max_length=254, unique=True),
        ),
    ]
