# Generated by Django 3.1.3 on 2021-02-05 06:49

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('emp_evaluation_system', '0025_auto_20210205_0646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='algorithm',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 4, 6, 49, 55, 217220, tzinfo=utc), help_text='A starting time for the algorithm simulation.'),
        ),
        migrations.AlterField(
            model_name='comparisongraph',
            name='type',
            field=models.CharField(choices=[('area', 'area'), ('bar', 'bar')], default='area', help_text='Allows configuring the chart type.', max_length=6),
        ),
    ]
