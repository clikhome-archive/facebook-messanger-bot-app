# -*- coding: utf-8 -*-
from __future__ import absolute_import

from messengerbot import attachments, elements, templates


def get_results_attachment(listings_data_items, more_url):
    tpl_elements = list()
    for listing_d in listings_data_items:
        element_kwargs = dict(
            title=listing_d['title'],
            subtitle=listing_d['fmt_address'],
            # item_url=more_url,
            buttons=[
                elements.WebUrlButton(
                    title='View more',
                    url=more_url,
                ),
                elements.WebUrlButton(
                    title='View this listing',
                    url=listing_d['listing_url'],
                )
            ]
        )
        image_url = listing_d.get('image_url', None)
        if image_url:
            element_kwargs['image_url'] = image_url
        element = elements.Element(**element_kwargs)
        tpl_elements.append(element)

    template = templates.GenericTemplate(tpl_elements)
    return attachments.TemplateAttachment(template=template)
