# Generated by Django 2.0 on 2018-02-05 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academy_site', '0012_course_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='theme',
            name='slug',
            field=models.SlugField(blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='theme',
            unique_together={('city', 'slug'), ('city', 'name')},
        ),
    ]
