# Generated by Django 2.0 on 2018-02-23 09:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('academy_site', '0015_auto_20180222_1704'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lesson',
            options={'ordering': ['date'], 'verbose_name': 'lesson', 'verbose_name_plural': 'lessons'},
        ),
    ]
