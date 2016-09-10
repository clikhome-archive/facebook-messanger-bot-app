from django.db import models
from django_extensions.db.models import TimeStampedModel


class PhoneNumber(TimeStampedModel):
    sender = models.CharField(max_length=255, db_index=True)
    sender_data = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, db_index=True)


class ChatLog(TimeStampedModel):
    TYPES_CHOICE = (
        ('in', 'In'),
        ('out', 'Out'),
    )
    recipient = models.CharField(max_length=255, db_index=True)
    question_class = models.CharField(max_length=255, db_index=True)
    errors = models.TextField(blank=True)
    text = models.TextField(blank=True)
    type = models.CharField(max_length=200, choices=TYPES_CHOICE, db_index=True)

    def __unicode__(self):
        return '{type} {recipient}: {text}'.format(**self.__dict__)
