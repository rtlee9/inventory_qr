# Generated by Django 5.0.2 on 2024-02-19 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('url', '0003_alter_urlaction_action_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='urlaction',
            name='url_key',
            field=models.CharField(default='', max_length=100),
        ),
    ]
