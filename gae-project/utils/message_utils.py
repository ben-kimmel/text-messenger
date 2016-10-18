from datetime import datetime
import json
import logging
from twilio.rest import TwilioRestClient

from google.appengine.ext import ndb, deferred
from models import TextMessageEvent
from utils import account_utils, contact_utils
from google.appengine.api import taskqueue
from google.appengine.api.labs.taskqueue.taskqueue import TaskRetryOptions


def replace_message_sig(message, sig_text):
    """Helper method to do a string replacement."""
    return message.replace("SIG", sig_text)


def replace_message_nickname(message, nickname):
    """Helper method to do a string replacement."""
    return message.replace("NICKNAME", nickname)
    
    
def get_parent_key_email_from_text_message_event(text_message_event):
    """ The parent of a text message event is the parent key for this user, which contains the email address of the user.
            This method returns the email address of this text message event's creator."""
    return text_message_event.key.parent().string_id()

    
def delete_text_message_event(text_message_event):
    # DONE: Remove the message from the task queue
    if text_message_event.is_in_task_queue:
        task_name = text_message_event.get_task_name()
        taskqueue.Queue().delete_tasks_by_name(task_name)  # Removes the scheduled task event
    
    
    text_message_event.key.delete();




# Different queries to get TextMessageEvents for this user.
def get_all_text_message_events_for_user(user):
    """ Gets all of the contacts for this user. """
    parent_key = account_utils.get_parent_key(user)
    return TextMessageEvent.query(ancestor=parent_key)


def get_pending_text_message_events_for_user(user):
    """ Gets only the messages that have not yet been sent. """
    query = get_all_text_message_events_for_user(user).order(TextMessageEvent.send_datetime)  # Closest to now on top
    now = datetime.now()
    return query.filter(ndb.AND(TextMessageEvent.has_been_sent == False, TextMessageEvent.send_datetime >= now)).fetch()


def get_unsent_text_message_events_for_user(user):
    """ Gets only the messages that have not yet been sent. """
    query = get_all_text_message_events_for_user(user).order(-TextMessageEvent.send_datetime)  # Closest to now on top
    now = datetime.now()
    return query.filter(ndb.AND(TextMessageEvent.has_been_sent == False, TextMessageEvent.send_datetime < now)).fetch()


def get_sent_text_message_events_for_user(user, limit=20):
    """ Gets text messages that have been sent in the past with a default limit of 20."""
    query = get_all_text_message_events_for_user(user).order(-TextMessageEvent.send_datetime)  # Closest to now on top
    return query.filter(TextMessageEvent.has_been_sent == True).fetch(limit)

    
    
# Jinja filters
def recipient_format(text_message_event):
    if text_message_event.recipient_type == TextMessageEvent.RecipientType.LIST:
        contact_list = text_message_event.recipient_list_key.get()
        if contact_list:
            return contact_list.name
        return "Deleted list"
    elif text_message_event.recipient_type == TextMessageEvent.RecipientType.INDIVIDUAL:
        contact = text_message_event.recipient_contact_key.get()
        if contact:
            return contact.nickname
        return "Deleted contact"
    elif text_message_event.recipient_type == TextMessageEvent.RecipientType.ALL:
        return "All contacts"
    return "Unknown"
    
def send_text_messages_for_event(text_message_event):
    """ Sends messages to recipients based on the text message event parameters, then marks the message as sent."""
    
    
    # Get the Twilio account information needed to send this text message event.
    creators_email = get_parent_key_email_from_text_message_event(text_message_event)
    account_info = account_utils.get_account_info_from_email(creators_email)
    logging.info("Sending a text message.    Creators email = " + creators_email + " body = " + str(text_message_event.message_body))

    message_body = replace_message_sig(text_message_event.message_body, account_info.signature_text)
    if message_body == None or len(message_body) < 1:
        logging.warn("Missing message body")
        return

    account_sid = account_info.twilio_sid
    auth_token = account_info.twilio_auth_token
    from_number = account_info.twilio_phone_number

    if not account_info or not account_sid or not auth_token or not from_number:
        logging.warn("Missing required Twilio account information")
        return

    client = TwilioRestClient(account_sid, auth_token)
   
    # Send the message only to the appropriate contacts.
    if text_message_event.recipient_type == TextMessageEvent.RecipientType.LIST:
        # Get the list and loop over the contacts in that list.
        logging.info("Sending a message to the list named: " + str(text_message_event.recipient_list_key.get().name))
        contacts = contact_utils.get_contacts_for_list_key(text_message_event.recipient_list_key)
        if not contacts:
            logging.warn("There are no contacts in this list!!!")
        return
    elif text_message_event.recipient_type == TextMessageEvent.RecipientType.INDIVIDUAL:
        # Just the one person
        contact = text_message_event.recipient_contact_key.get()
        logging.info("Sending a message to an individual: " + contact.nickname)
        contacts = [contact]
    else:
        logging.info("Sending a message to all contacts")
        contacts = contact_utils.get_contacts_for_email(creators_email)
    
    media_url = None
    if text_message_event.media_blob_key:
        media_url = "http://kimmelbs-text-messenger.appspot.com/img/" + str(text_message_event.media_blob_key) 
        logging.info("Sending an MMS using media_url = " + media_url)
    
    for contact in contacts:
        to_number = contact.phone_number
        if not to_number:
            logging.info(creators_email + " tried to send the message to " + contact.nickname + ", but failed since that contact has no phone number.")
            continue
        body = replace_message_nickname(message_body, contact.nickname)
    
    # Twilio library code:  https://github.com/twilio/twilio-python
    # Twilio library docs: http://twilio-python.readthedocs.io/en/latest/
    rv = client.messages.create(to=to_number, from_=from_number, body=body, media_url=media_url)
    if rv.error_message:
        logging.info("Message had an error " + rv.error_message)
    logging.info("Message from " + creators_email + " " + str(from_number) + \
    " to " + str(contact.nickname) + " " + str(to_number) + \
    " body: " + str(body) + "   return value status: " + str(rv.status))
    
    # Mark this message as Done!
    text_message_event.has_been_sent = True
    text_message_event.put()
    
def send_text_messages_for_event_key(k):
    try:
        send_text_messages_for_event(k.get())
    except:
        logging.error("Oopsie! There's an error in the text sender!")
    
    
def send_message_now(text_message_event):
    text_message_event.has_been_sent = True
    text_message_event.put()
    # send_text_messages_for_event(text_message_event)
    deferred.defer(send_text_messages_for_event_key, text_message_event.key)
    
def add_text_message_event_to_task_queue(text_message_event):
    """ Adds the text message event to the task queue for later delivery. """
    
    if text_message_event.is_in_task_queue:
        logging.info("Text message event already present in the task queue!")
        return
    
    logging.info("Adding text message event to the task queue.")
    text_message_event.is_in_task_queue = True
    text_message_event_key = text_message_event.put()    # Also done to get the key to use as the name of the task.
    
    # https://cloud.google.com/appengine/docs/python/refdocs/google.appengine.api.taskqueue#google.appengine.api.taskqueue.add
    payload = {"urlsafe_entity_key": text_message_event_key.urlsafe()}
    taskqueue.add(url='/queue/send-message',
                                name=text_message_event.get_task_name(),
                                payload=json.dumps(payload),
                                eta=text_message_event.send_datetime,
                                retry_options=TaskRetryOptions(task_retry_limit=1))

