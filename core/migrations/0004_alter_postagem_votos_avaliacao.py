# Generated by Django 5.1.3 on 2024-12-11 17:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_postagem_natureza'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postagem',
            name='votos',
            field=models.FloatField(default=0),
        ),
        migrations.CreateModel(
            name='Avaliacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avaliacao', models.IntegerField()),
                ('postagem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.postagem')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
