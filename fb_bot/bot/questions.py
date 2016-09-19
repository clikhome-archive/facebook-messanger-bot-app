# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json
import logging

import re
from timestring import Range, TimestringInvalid

from clikhome_fbbot.utils import geolocator
from fb_bot.bot import templates
from fb_bot.bot.ctx import session, search_request
from fb_bot.models import PhoneNumber

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


class BaseQuestion(object):
    question = None
    answer_matcher = re.compile(r'.+', re.IGNORECASE)
    answer_bad_message = 'Bad answer "{answer}"'
    param_key = None
    param_value = None
    skip_ask = False
    answer = None
    wait_for_answer = False

    @property
    def class_name(self):
        return self.__class__.__name__

    @property
    def postback_choices(self):
        # choices = map(lambda x: ('{}:{}'.format(self.class_name, x[0]), x[1]), self.answer_choices)
        return dict(self.answer_choices)

    @property
    def value(self):
        return self.param_value

    def activate(self):
        raise NotImplemented()

    @property
    def filter_value(self):
        raise NotImplemented

    def set_answer(self, answer):
        raise NotImplemented()

    def bad_answer(self, answer):
        q = search_request.go_to_question(AskPhoneNumberQuestion)
        if not q:
            session.reply(self.answer_bad_message.format(answer=answer))
        else:
            q.activate(is_bad_request=True)


    def __repr__(self):
        return '<%s question="%s" key="%s" answer="%r">' % (
            self.__class__.__name__,
            self.question,
            self.param_key,
            self.answer
        )


class LocationQuestion(BaseQuestion):
    question = 'Great, where do you want to move?'
    param_key = 'location_bbox'
    messages = {
        'location_not_found': """Sorry, we I can't find "{answer}" location, please try again."""
    }
    skip_ask = True

    def activate(self):
        session.reply(self.question)
        self.wait_for_answer = True

    @property
    def filter_value(self):
        return {
            '!location_bbox': self.param_value
        }

    def set_answer(self, answer):
        answer = re.sub(r'^to\s+', '', answer, 1, re.IGNORECASE)
        bbox = geolocator.geocode_location_to_bbox(answer)
        if bbox:
            self.param_value = bbox
            self.answer = answer
            self.wait_for_answer = False
            session.reply('Ok, we are going to "%s"' % bbox.formatted_address)
        else:
            session.reply(self.messages['location_not_found'].format(answer=answer))


class BedroomsQuestion(BaseQuestion):
    question = 'Ok, how many bedrooms do you need?'
    param_key = 'bedrooms'
    answer_matcher = re.compile('^\d+$', re.IGNORECASE)

    @property
    def filter_value(self):
        return dict(
            bedrooms=self.param_value
        )

    def activate(self):
        session.reply(self.question)
        self.wait_for_answer = True

    def set_answer(self, answer):
        # TODO: may be we should accept answers like 'any'?
        # TODO: convert words to numbers
        if answer.strip().lower() == 'studio':
            answer = '0'

        if not self.answer_matcher.match(answer):
            self.bad_answer(answer)
        else:
            self.param_value = answer
            self.wait_for_answer = False


class PriceQuestion(BaseQuestion):
    question = 'What’s your price range?'
    param_key = 'price_range'
    answer_matcher = re.compile('^\d+$', re.IGNORECASE)

    @property
    def filter_value(self):
        return dict(
            price_range=[self.param_value, self.param_value]
        )

    def activate(self):
        session.reply(self.question)
        self.wait_for_answer = True

    def set_answer(self, answer):
        # TODO: convert words to numbers
        # TODO: accept ranges
        answer = re.sub('\D+', '', answer)
        if not self.answer_matcher.match(answer):
            session.reply(self.answer_bad_message.format(answer=answer))
        else:
            self.param_value = answer
            self.wait_for_answer = False


class LeaseStartQuestion(BaseQuestion):
    question = 'Got it, when are you looking to move?'
    param_key = 'lease_start'
    answer_matcher = re.compile('^.+$', re.IGNORECASE)
    messages = {
        'bad_date': """Sorry, I can't understand this date: '{answer}'"""
    }

    def activate(self):
        session.reply(self.question)
        self.wait_for_answer = True

    @property
    def filter_value(self):
        return dict(lease_range=self.param_value)

    def set_answer(self, answer):
        answer = answer.strip().lower()
        if answer in (
            'asap',
            'as soon as possible', 'as fast as possible', 'as quick(quickly) as possible',
            'as quick as possible', 'as quickly as possible'
        ):
            answer = 'now'

        try:
            value = Range(answer)
            self.param_value = map(lambda d: d.date, value._dates)
        except TimestringInvalid:
            session.reply(self.answer_bad_message.format(answer=answer))
        else:
            self.wait_for_answer = False


class DogWeighAdditionalQuestion(BaseQuestion):
    answer_matcher = re.compile(r'^yes|no$', re.IGNORECASE)
    question = 'Does your dog weigh more than 25 Lbs?'
    answer_bad_message = 'Sorry, "{answer}" is a bad answer, please choose Yes or No'
    answer_choices = (
        ('No', 'No'),
        ('Yes', 'Yes'),
    )

    def __init__(self, parent):
        self.parent = parent
        self.answer = None

    def activate(self):
        session.attachment_reply(
            templates.make_button_choices(self.question, self.postback_choices)
        )
        self.wait_for_answer = True

    @property
    def value(self):
        if self.answer in ('y', 'yes'):
            return True
        elif self.answer in ('n', 'no'):
            return False
        else:
            raise ValueError(self.answer)

    def set_answer(self, answer):
        answer = answer.strip().lower()
        if not self.answer_matcher.match(answer):
            self.bad_answer(answer)
        else:
            self.answer = answer
            self.wait_for_answer = False


class PetsQuestion(BaseQuestion):
    question = 'Do you have any pets?'
    param_key = 'pets'
    answer_matcher = re.compile(r'^no|dog|cat$', re.IGNORECASE)
    answer_bad_message = 'Sorry, "{answer}" is a bad answer, please choose: No, Dog, Cat'
    answer_choices = (
        ('No', 'No'),
        ('Dog', 'Dog'),
        ('Cat', 'Cat'),
    )
    additional_question = None

    def activate(self):
        session.attachment_reply(
            templates.make_button_choices(self.question, self.postback_choices)
        )
        self.wait_for_answer = True

    @property
    def filter_value(self):
        if self.param_value == 'no':
            return dict()
        else:
            return {
                '!has_pet': self.param_value
            }

    def set_answer(self, answer):
        if self.additional_question:
            self.additional_question.set_answer(answer)
            self.param_value['dog_have_weigh_gte_25lbs'] = self.additional_question.value
            self.wait_for_answer = False
            return

        if not self.answer_matcher.match(answer):
            session.reply(self.answer_bad_message.format(answer=answer))
            return

        pet_type = answer.strip().lower()

        if pet_type == 'no':
            self.param_value = pet_type
            self.wait_for_answer = False
        else:
            self.param_value = pet_type
            self.param_value = {
                'pet_type': self.param_value,
                'dog_have_weigh_gte_25lbs': False
            }
            if self.param_value['pet_type'] == 'dog':
                self.additional_question = DogWeighAdditionalQuestion(parent=self)
                self.additional_question.activate()
                self.wait_for_answer = True
            else:
                self.wait_for_answer = False


class AskPhoneNumberQuestion(BaseQuestion):
    answer_matcher = re.compile(r'^yes|no$', re.IGNORECASE)
    answer_bad_message = 'Sorry, "{answer}" is a bad answer, please choose Yes or No'
    question = 'Would you consider this apartment? We want to make sure that we are on the right track.'
    bad_request_text = (
        'I can connect you with our operation manager who will give you more information. '
        'I apologize for any inconvenience. '
        'What is the phone number or email address our operation manager can contact you on?'
        'Thank you, we will be in touch.'
    )
    answer_choices = (
        ('yes', 'Yes'),
        ('no', 'No'),
    )
    is_bad_request = False

    def activate(self, is_bad_request=False):
        if is_bad_request:
            self.is_bad_request = True
            session.reply(self.bad_request_text)
        else:
            session.attachment_reply(
                templates.make_button_choices(self.question, self.postback_choices)
            )
        self.wait_for_answer = True

    def set_answer(self, answer):
        if self.answer or self.is_bad_request:
            log.info('Accept phone number: %r' % answer)
            try:
                PhoneNumber.objects.create(
                    sender=session.user_id,
                    sender_data=json.dumps(session.data.get('user_profile', [])),
                    phone=answer
                )
            finally:
                self.wait_for_answer = False
                session.reply('Thank you. Have a good day.')
                search_request.reset()
        else:
            answer = answer.strip().lower()
            if not self.answer_matcher.match(answer):
                self.bad_answer(answer)
                return

            self.answer = answer
            if self.answer == 'yes':
                session.reply(
                    'Perfect, we will process your request and our operation manager '
                    'will get back to you with your apartment recommendations shortly. '
                    'What is your phone number and email address we can contact you on?'
                )
            elif self.answer == 'no':
                session.reply(
                    'No problem, we will process your request and our operation manager '
                    'will get back to you with apartment recommendations that better fit your criteria.'
                    ' What is your phone number and email address we can contact you on?'
                )


class Greeting(object):
    _greeting = 'Hi {user_first_name}! This is Mary with Apartment Ocean. How are you?'
    wait_for_answer = False

    def set_answer(self, answer):
        self.wait_for_answer = False

    @property
    def greeting(self):
        return self._greeting.format(user_first_name=session.user_first_name)

    def activate(self):
        session.reply(self.greeting)
        self.wait_for_answer = True


class SendApartmentSuggestion(object):
    wait_for_answer = False

    def set_answer(self, answer):
        pass

    def activate(self):
        session.send_typing_on()
        search_request.request_search_results()


def get_questions_list():
    questions = [
        Greeting(),
        LocationQuestion(),
        BedroomsQuestion(),
        PriceQuestion(),
        LeaseStartQuestion(),
        PetsQuestion(),
        SendApartmentSuggestion(),
        AskPhoneNumberQuestion(),
    ]

    return questions

