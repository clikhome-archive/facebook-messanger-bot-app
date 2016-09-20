# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fb_bot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonenumber',
            name='sender_data',
            field=models.TextField(),
        ),
    ]
