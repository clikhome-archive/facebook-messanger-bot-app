from django.contrib import admin

from fb_bot import models


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
admin.site.register(models.PhoneNumber, PhoneNumberAdmin)


class ChatLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'chat',
        'text',
        'type',
        'question_class',
        'errors',
        'created',
    )
    list_filter = (
        'chat',
        'created',
        'type',
    )
admin.site.register(models.ChatLog, ChatLogAdmin)


class ChatAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'fb_user_id',
        'muted_at',
        'mute_expire',
        'created',
    )
    list_filter = (
        'created',
    )

admin.site.register(models.Chat, ChatAdmin)
