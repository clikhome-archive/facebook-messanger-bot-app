from django.db import models
from django_extensions.db.models import TimeStampedModel


class PhoneNumber(TimeStampedModel):
    sender = models.CharField(max_length=255, db_index=True)
    sender_data = models.TextField()
    phone = models.CharField(max_length=255, db_index=True)


class ChatLog(TimeStampedModel):
    TYPES_CHOICE = (
        ('in', 'In'),
        ('out', 'Out'),
    )
    question_class = models.CharField(max_length=255, db_index=True)
    errors = models.TextField(blank=True)
    text = models.TextField(blank=True)
    type = models.CharField(max_length=200, choices=TYPES_CHOICE, db_index=True)
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE)

    def __unicode__(self):
        return '{type} {recipient}: {text}'.format(**self.__dict__)


class Chat(TimeStampedModel):
    muted_at = models.DateTimeField(db_index=True, null=True, default=None)
    fb_user_id = models.CharField(max_length=255, blank=False, db_index=True, unique=True)

    def __unicode__(self):
        return '{fb_user_id}'.format(**self.__dict__)
