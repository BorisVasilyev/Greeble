# Generated by Django 2.1.1 on 2018-09-09 14:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0009_user_useranswer_userslideview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useranswer',
            name='last_submit_time',
            field=models.DateTimeField(verbose_name='last submit date'),
        ),
        migrations.AlterField(
            model_name='useranswer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userslideview',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]
