# Generated by Django 5.2 on 2025-05-30 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academico', '0002_calificacion_nombre_alter_user_is_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calificacion',
            name='nombre',
            field=models.CharField(help_text='Nombre descriptivo de la calificación', max_length=100, verbose_name='Nombre/Descripción'),
        ),
    ]
