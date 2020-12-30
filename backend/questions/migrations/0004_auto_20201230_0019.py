# Generated by Django 2.2.17 on 2020-12-30 00:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0003_auto_20201229_0410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentvote',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='comment_votes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='questionvote',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='question_votes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='replyvote',
            name='reply',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='reply_votes', to='questions.Reply'),
        ),
        migrations.AlterField(
            model_name='replyvote',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='reply_votes', to=settings.AUTH_USER_MODEL),
        ),
    ]
