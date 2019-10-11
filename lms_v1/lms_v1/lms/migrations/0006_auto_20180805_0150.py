# Generated by Django 2.0.7 on 2018-08-05 01:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0005_answer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='slide',
            name='slide_num',
        ),
        migrations.AddField(
            model_name='slide',
            name='next_slide_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='slide',
            name='previous_slide_id',
            field=models.IntegerField(default=0),
        ),
    ]
