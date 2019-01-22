# Generated by Django 2.1.3 on 2019-01-15 18:09

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='HistoryElement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Mail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('sender', models.CharField(max_length=200)),
                ('receiver', models.CharField(max_length=200)),
                ('body', models.TextField()),
                ('answered', models.BooleanField(default=False)),
                ('received_at', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('url', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ProblemClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('email_body', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='issue',
            name='problem_class',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticketsystem.ProblemClass'),
        ),
        migrations.AddField(
            model_name='historyelement',
            name='issue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticketsystem.Issue'),
        ),
        migrations.AddField(
            model_name='historyelement',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticketsystem.State'),
        ),
        migrations.AddField(
            model_name='address',
            name='issue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticketsystem.Issue'),
        ),
    ]
