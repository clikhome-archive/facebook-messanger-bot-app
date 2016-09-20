from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Setup https://developers.facebook.com/docs/messenger-platform/thread-settings/get-started-button"

    def handle(self, *args, **options):
        from fb_bot.bot.utils import CallToActions
        print CallToActions.setup()
