# Generated by Django 2.0 on 2018-02-20 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academy_site', '0005_auto_20180220_1027'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usercourse',
            name='know_academy_through',
        ),
        migrations.AddField(
            model_name='siteuser',
            name='know_academy_through',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
