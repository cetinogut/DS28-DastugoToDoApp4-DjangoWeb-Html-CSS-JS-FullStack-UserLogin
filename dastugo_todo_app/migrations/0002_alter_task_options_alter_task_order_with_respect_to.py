# Generated by Django 4.0 on 2021-12-08 09:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dastugo_todo_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['completed']},
        ),
        migrations.AlterOrderWithRespectTo(
            name='task',
            order_with_respect_to=None,
        ),
    ]
