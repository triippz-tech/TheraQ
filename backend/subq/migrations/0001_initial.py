# Generated by Django 2.2.17 on 2020-12-28 23:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SubQ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateField(auto_now_add=True, null=True)),
                ('updated_date', models.DateField(blank=True, null=True)),
                ('status', models.BooleanField(blank=True, default=False, null=True)),
                ('sub_name', models.CharField(db_index=True, max_length=250, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('slug', models.SlugField(max_length=80, unique=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'subq',
            },
        ),
        migrations.CreateModel(
            name='SubQFollower',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateField(auto_now_add=True, null=True)),
                ('updated_date', models.DateField(blank=True, null=True)),
                ('status', models.BooleanField(blank=True, default=False, null=True)),
                ('is_moderator', models.BooleanField(blank=True, default=False, null=True)),
                ('join_date', models.DateField(blank=True, null=True)),
                ('notifications_enabled', models.BooleanField(blank=True, default=True)),
                ('subq', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='subq.SubQ')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'subq_follower',
            },
        ),
    ]
