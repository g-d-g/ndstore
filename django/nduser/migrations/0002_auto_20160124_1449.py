# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-24 19:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nduser', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='kvengine',
            field=models.CharField(choices=[(b'MySQL', b'MySQL'), (b'Cassandra', b'Cassandra'), (b'Riak', b'Riak'), (b'DynamoDB', b'DynamoDB')], default=b'MySQL', max_length=255),
        ),
    ]