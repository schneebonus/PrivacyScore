# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-16 17:13
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import privacyscore.backend.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ListColumn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('sort_key', models.PositiveSmallIntegerField()),
                ('visible', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ListColumnValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
                ('column', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='backend.ListColumn')),
            ],
        ),
        migrations.CreateModel(
            name='ListTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='RawScanResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test', models.CharField(max_length=80)),
                ('identifier', models.CharField(max_length=80)),
                ('data_type', models.CharField(max_length=80)),
                ('file_name', models.CharField(blank=True, max_length=80, null=True)),
                ('data', models.BinaryField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Scan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('success', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='ScanGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField(default=django.utils.timezone.now)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'ready'), (1, 'scanning'), (2, 'finish'), (3, 'error')], default=0)),
                ('error', models.CharField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ScanList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField()),
                ('token', models.CharField(default=privacyscore.backend.models.generate_random_token, max_length=50, unique=True)),
                ('private', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tags', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ScanResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('scan', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='backend.Scan')),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=500, unique=True)),
                ('scan_lists', models.ManyToManyField(related_name='sites', to='backend.ScanList')),
            ],
        ),
        migrations.AddField(
            model_name='scangroup',
            name='scan_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scan_groups', to='backend.ScanList'),
        ),
        migrations.AddField(
            model_name='scan',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scans', to='backend.ScanGroup'),
        ),
        migrations.AddField(
            model_name='scan',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scans', to='backend.Site'),
        ),
        migrations.AddField(
            model_name='rawscanresult',
            name='scan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='raw_results', to='backend.Scan'),
        ),
        migrations.AddField(
            model_name='listtag',
            name='scan_lists',
            field=models.ManyToManyField(related_name='tags', to='backend.ScanList'),
        ),
        migrations.AddField(
            model_name='listcolumnvalue',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='column_values', to='backend.Site'),
        ),
        migrations.AddField(
            model_name='listcolumn',
            name='scan_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='columns', to='backend.ScanList'),
        ),
        migrations.AlterUniqueTogether(
            name='listcolumn',
            unique_together=set([('scan_list', 'sort_key'), ('name', 'scan_list')]),
        ),
    ]
