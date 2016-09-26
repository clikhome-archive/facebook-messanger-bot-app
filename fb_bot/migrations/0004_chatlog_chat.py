# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    Chat = apps.get_model('fb_bot', 'Chat')
    ChatLog = apps.get_model('fb_bot', 'ChatLog')
    db_alias = schema_editor.connection.alias

    seen = set()
    chat_objects = list()
    for recipient in ChatLog.objects.filter(type='in').values_list('recipient', flat=True):
        if recipient in seen:
            continue
        else:
            seen.add(recipient)
        chat_objects.append(Chat(fb_user_id=recipient))

    seen.clear()

    Chat.objects.using(db_alias).bulk_create(chat_objects)

    for chat in Chat.objects.all():
        if chat.fb_user_id in seen:
            continue
        else:
            seen.add(chat.fb_user_id)
        updated = ChatLog.objects.filter(recipient=chat.fb_user_id).update(chat=chat)
        print 'Updated %d chats for %s' % (updated, chat.fb_user_id)


class Migration(migrations.Migration):

    dependencies = [
        ('fb_bot', '0003_chat'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatlog',
            name='chat',
            field=models.ForeignKey(to='fb_bot.Chat', null=True),
        ),
        migrations.RunPython(forwards_func),
        migrations.AlterField(
            model_name='chatlog',
            name='chat',
            field=models.ForeignKey(to='fb_bot.Chat'),
        ),
        migrations.RemoveField(
            model_name='chatlog',
            name='recipient',
        ),
    ]
