#!/usr/bin/env python

import os

import jinja2
import webapp2

from handlers import (delete_handlers, insert_handlers, main_handler,
    blob_handler, auto_responders, scheduled_send_handlers)
from utils import date_utils, message_utils


# Jinja environment instance necessary to use Jinja templates.
def __init_jinja_env():
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols", "jinja2.ext.with_"],
        autoescape=True)
    jenv.filters["date_time_display_format"] = date_utils.date_time_display_format
    jenv.filters["date_time_input_format"] = date_utils.date_time_input_format
    jenv.filters["recipient_format"] = message_utils.recipient_format
    return jenv

jinja_env = __init_jinja_env()

app = webapp2.WSGIApplication([
    # Home
    ('/', main_handler.MainHandler),

    # Pages
    ('/account-info', main_handler.AccountInfoPage),
    ('/contacts', main_handler.ContactsPage),
    ('/lists', main_handler.ListsPage),
    ('/list', main_handler.ListDetailPage),
    ('/text-messages', main_handler.TextMessagesPage),
    ('/create-message', main_handler.CreateMessagePage),
    
    # Actions - Insert
    ('/account-info-action', insert_handlers.AccountInfoAction),
    ("/insert-contact", insert_handlers.InsertContactAction),
    ("/insert-list", insert_handlers.AddListAction),
    ('/update-list', insert_handlers.UpdateListAction),
    ("/insert-text-message-event", insert_handlers.InsertTextMessageEventAction),

    # Actions - Delete
    ("/delete-contact", delete_handlers.DeleteContactAction),
    ("/delete-list", delete_handlers.DeleteListAction),
    ("/delete-text-message-event", delete_handlers.DeleteTextMessageEventAction),
    
    #Blobs
    ('/img/([^/]+)?', blob_handler.BlobServer),
    
    # SMS and Voice auto responders
    ('/voice-auto-reply', auto_responders.VoiceReply),
    ('/sms-auto-reply', auto_responders.SmsReply),
    
    # Cron jobs
    ("/cron/check-message-events", scheduled_send_handlers.CronCheckMessagesForSends),
    
    # Task Queue handlers
    ("/queue/send-message", scheduled_send_handlers.QueueSendMessage)



  ], debug=True)
