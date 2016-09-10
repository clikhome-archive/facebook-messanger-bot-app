# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import re
from timestring import Range, TimestringInvalid

from clikhome_fbbot.utils import geolocator


class ImmediateReply(Exception):
    pass


class BadAnswer(Exception):
    pass


class GoToFinish(Exception):
    pass


class BaseQuestion(object):
    question = None
    answer_matcher = re.compile(r'.+', re.IGNORECASE)
    answer_bad_message = 'Bad answer "%(answer)s"'
    param_key = None
    param_value = None
    skip_ask = False
    answer = None

    @property
    def value(self):
        return self.param_value

    @property
    def filter_value(self):
        raise NotImplemented

    def set_answer(self, answer):
        raise NotImplemented()

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
        'location_not_found': """Sorry, we I can't find "{answer}" location."""
    }
    skip_ask = True

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
            return 'Ok, we are going to "%s"' % bbox.formatted_address
        else:
            raise BadAnswer(self.messages['location_not_found'].format(answer=answer))


class BedroomsQuestion(BaseQuestion):
    question = 'Ok, how many bedrooms do you need?'
    param_key = 'bedrooms'
    answer_matcher = re.compile('^\d+$', re.IGNORECASE)

    @property
    def filter_value(self):
        return dict(
            bedrooms=self.param_value
        )

    def set_answer(self, answer):
        # TODO: may be we should accept answers like 'any'?
        # TODO: convert words to numbers
        if answer.strip().lower() == 'studio':
            answer = '0'

        if not self.answer_matcher.match(answer):
            raise BadAnswer(self.answer_bad_message % dict(answer=answer))

        self.param_value = answer


class PriceQuestion(BaseQuestion):
    question = 'What’s your price range?'
    param_key = 'price_range'
    answer_matcher = re.compile('^\d+$', re.IGNORECASE)

    @property
    def filter_value(self):
        return dict(
            price_range=[self.param_value, self.param_value]
        )

    def set_answer(self, answer):
        # TODO: convert words to numbers
        # TODO: accept ranges
        answer = re.sub('\D+', '', answer)
        if not self.answer_matcher.match(answer):
            raise BadAnswer(self.answer_bad_message % dict(answer=answer))
        self.param_value = answer


class LeaseStartQuestion(BaseQuestion):
    question = 'Got it, when are you looking to move?'
    param_key = 'lease_start'
    answer_matcher = re.compile('^.+$', re.IGNORECASE)
    messages = {
        'bad_date': """Sorry, I can't understand this date: '{answer}'"""
    }

    @property
    def filter_value(self):
        return dict(lease_range=self.param_value)

    def set_answer(self, answer):
        try:
            value = Range(answer)
            self.param_value = map(lambda d: d.date, value._dates)
        except TimestringInvalid:
            raise BadAnswer(self.answer_bad_message.format(answer=answer))


class DogWeighAdditionalQuestion(BaseQuestion):
    answer_matcher = re.compile(r'^yes|no|y|n$', re.IGNORECASE)
    question = 'Does your dog weigh more than 25 Lbs?'
    answer_bad_message = 'Sorry, "{answer}" is a bad answer, please choose yes/y or no/n.'

    def __init__(self, parent):
        self.parent = parent
        self.answer = None

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
            raise BadAnswer(self.answer_bad_message.format(answer=answer))
        self.answer = answer


class PetsQuestion(BaseQuestion):
    question = 'Do you have any pets?'
    param_key = 'pets'
    answer_matcher = re.compile(r'^no|dog|cat$', re.IGNORECASE)
    answer_bad_message = 'Sorry, "{answer}" is a bad answer, please choose: No, Dog, Cat'
    additional_question = None

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
            return

        if not self.answer_matcher.match(answer):
            raise BadAnswer(self.answer_bad_message % dict(answer=answer))

        pet_type = answer.strip().lower()

        if pet_type == 'no':
            self.param_value = pet_type
        else:
            self.param_value = {
                'pet_type': self.param_value,
                'dog_have_weigh_gte_25lbs': False
            }
            if self.param_value['pet_type'] == 'dog':
                self.additional_question = DogWeighAdditionalQuestion(parent=self)
                raise ImmediateReply(self.additional_question.question)


class AskPhoneNumberQuestion(BaseQuestion):
    answer_matcher = re.compile(r'^yes|no|y|n$', re.IGNORECASE)
    answer_bad_message = 'Sorry, "{answer}" is a bad answer, please choose yes/y or no/n.'
    question = 'Would you consider this apartment? We want to make sure that we are on the right track.'
    phone_number = None

    def set_answer(self, answer):
        if self.answer:
            # TODO: save the data
            self.phone_number = answer
            return 'Thank you. Have a good day.'
        else:
            answer = answer.strip().lower()
            if not self.answer_matcher.match(answer):
                raise BadAnswer(self.answer_bad_message % dict(answer=answer))

            self.answer = answer

            if self.answer == 'yes':
                raise ImmediateReply(
                    'Perfect, we will process your request and our operation manager '
                    'will get back to you with your apartment recommendations shortly. '
                    'What is your phone number and email address we can contact you on?'
                )
            elif self.answer == 'no':
                raise ImmediateReply(
                    'No problem, we will process your request and our operation manager '
                    'will get back to you with apartment recommendations that better fit your criteria.'
                    ' What is your phone number and email address we can contact you on?'
                )


class Greeting(object):
    greeting = 'Hi {sender_first_name}! This is Mary with Apartment Ocean. How are you?'

    @staticmethod
    def __new__(cls, *more):
        raise Exception('This class cannot be instanced')


class SendApartmentSuggestion(object):
    @staticmethod
    def __new__(cls, *more):
        raise Exception('This class cannot be instanced')


def get_questions_list():
    questions = [
        Greeting,
        LocationQuestion(),
        BedroomsQuestion(),
        PriceQuestion(),
        LeaseStartQuestion(),
        PetsQuestion(),
        SendApartmentSuggestion,
        AskPhoneNumberQuestion(),
    ]

    return questions

