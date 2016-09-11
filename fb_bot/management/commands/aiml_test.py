from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "My shiny new management command."

    def handle(self, *args, **options):
        from fb_bot.bot.entry_handler import entry_handler
        # print entry_handler.aiml_respond('hey')
        # print entry_handler.aiml_respond('hello')
        # print entry_handler.aiml_respond('What is your fee?')
        # print entry_handler.aiml_respond('WHAT ARE YOU')
        inputs = [
            'What is your fee?',
            'What is your charge?',
            'What is your cost?',
            "What's your fee?",
            "Do you accept any programs? Do you take Section 8?",
            "Do you take Section 8?",
            "Are you a bot?",
            "Are you a chatbot?",
            "Who are you?",
        ]
        for item in inputs:
            print '[%s]: %s' % (item, entry_handler.aiml_respond(item))

        # print entry_handler.aiml._brain
        # while True:
        #     print entry_handler.aiml_respond(raw_input("> "))
