# Generated by Django 2.2.17 on 2020-12-29 01:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'verbose_name': 'Comment'},
        ),
        migrations.AlterModelOptions(
            name='commentvote',
            options={'verbose_name': 'Comment Vote'},
        ),
        migrations.AlterModelOptions(
            name='qtag',
            options={'verbose_name': 'Question Tag'},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'verbose_name': 'Question'},
        ),
        migrations.AlterModelOptions(
            name='questionqtag',
            options={'verbose_name': 'Question QTags (Joined)'},
        ),
        migrations.AlterModelOptions(
            name='questionviews',
            options={'verbose_name': 'Question View'},
        ),
        migrations.AlterModelOptions(
            name='questionvote',
            options={'verbose_name': 'Question Vote'},
        ),
        migrations.AlterModelOptions(
            name='questionwatchers',
            options={'verbose_name': 'Question Watcher'},
        ),
        migrations.AlterModelOptions(
            name='reply',
            options={'verbose_name': 'Reply'},
        ),
        migrations.AlterModelOptions(
            name='replyvote',
            options={'verbose_name': 'Reply Vote'},
        ),
    ]
