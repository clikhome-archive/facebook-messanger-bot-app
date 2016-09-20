from django.contrib import admin
from fb_bot.models import PhoneNumber, ChatLog


class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'sender',
        'sender_data',
        'phone',
        'created',
    )
    list_filter = (
        'sender',
    )
admin.site.register(PhoneNumber, PhoneNumberAdmin)


class ChatLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipient',
        'text',
        'type',
        'question_class',
        'errors',
        'created',
    )
    list_filter = (
        'recipient',
        'type',
    )
admin.site.register(ChatLog, ChatLogAdmin)
