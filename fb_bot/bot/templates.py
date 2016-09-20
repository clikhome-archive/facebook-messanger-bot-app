# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.utils.text import Truncator
from messengerbot import attachments, elements, templates


def make_button_choices(text, choices):
    assert isinstance(choices, dict)
    assert len(choices) <= 3

    postback_buttons = list()
    for payload, button_text in choices.iteritems():
        btn = elements.PostbackButton(
            title=button_text,
            payload=payload
        )
        postback_buttons.append(btn)

    el = templates.ButtonTemplate(
        text=text,
        buttons=postback_buttons
    )
    return attachments.TemplateAttachment(template=el)


def get_results_attachment(listings_data_items, more_url=None):
    tpl_elements = list()
    for listing_d in listings_data_items:
        buttons = list()
        if more_url:
            buttons.append(
                elements.WebUrlButton(
                    title='View more',
                    url=more_url,
                )
            )

        buttons.append(
            elements.WebUrlButton(
                title='View this listing',
                url=listing_d['listing_url'],
            )
        )
        element_kwargs = dict(
            title=Truncator(listing_d['title']).chars(44),
            subtitle=Truncator(listing_d['fmt_address']).chars(79),
            buttons=buttons
        )
        image_url = listing_d.get('image_url', None)
        if image_url:
            element_kwargs['image_url'] = image_url
        element = elements.Element(**element_kwargs)
        tpl_elements.append(element)

    template = templates.GenericTemplate(tpl_elements)
    return attachments.TemplateAttachment(template=template)
