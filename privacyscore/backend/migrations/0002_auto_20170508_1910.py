# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-08 19:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import privacyscore.backend.models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='listcolumn',
            name='sort_key',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='scangroup',
            name='list',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='scan_groups', to='backend.List'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='list',
            name='token',
            field=models.CharField(default=privacyscore.backend.models.generate_random_token, max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='list',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tags', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='listcolumn',
            unique_together=set([('list', 'sort_key'), ('name', 'list')]),
        ),
    ]