# Generated by Django 4.0.6 on 2022-09-02 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institute', '0009_remove_historicalbatch_batch_subject_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalownerprofile',
            name='about_me',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='historicalownerprofile',
            name='location',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='ownerprofile',
            name='about_me',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='ownerprofile',
            name='location',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]