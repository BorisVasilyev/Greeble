# Generated by Django 3.0.5 on 2020-04-28 19:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0018_slide_test'),
    ]

    operations = [
        migrations.RenameField(
            model_name='test',
            old_name='content_xml',
            new_name='content',
        ),
    ]
