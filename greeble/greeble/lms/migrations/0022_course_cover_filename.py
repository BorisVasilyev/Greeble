# Generated by Django 3.0.5 on 2020-05-02 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0021_auto_20200502_1034'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='cover_filename',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
