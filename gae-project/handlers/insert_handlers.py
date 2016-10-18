from datetime import datetime
import logging

from google.appengine.api import users
from google.appengine.api.blobstore.blobstore import BlobKey
from google.appengine.ext import ndb
from handlers import base_handlers
from models import Contact, ContactList, TextMessageEvent
from utils import account_utils, date_utils, message_utils
from google.appengine.ext.webapp import blobstore_handlers


class AccountInfoAction(base_handlers.BaseAction):
    """Set account info for this user."""
    def handle_post(self, user, account_info):
        account_info.twilio_sid = self.request.get("twilio_sid")
        account_info.twilio_auth_token = self.request.get("twilio_auth_token") 
        account_info.twilio_phone_number = self.request.get("twilio_phone_number")
        account_info.auto_response_sms = self.request.get("auto_response_sms")
        account_info.auto_response_voice = self.request.get("auto_response_voice") 
        account_info.time_zone = self.request.get("time_zone") 
        account_info.signature_text = self.request.get("signature_text")
        account_info.put()
        self.redirect("/")


class InsertContactAction(base_handlers.BaseAction):
    """Insert a new contact or update and existing contact."""
    def handle_post(self, user, account_info):
        phone_number = self.request.get('phone_number')
        urlsafe_entity_key = self.request.get('contact_entity_key')
        if len(urlsafe_entity_key) > 0:
            contact_key = ndb.Key(urlsafe=urlsafe_entity_key)
            if contact_key.string_id() == phone_number:
                # The phone number is the same, just do a simple edit
                contact = contact_key.get()
            else:
                # The phone number has changed.    ugh.    Do it the hard way.
                logging.info("The phone number changed when editing this contact!")
                original_contact = contact_key.get()
                contact = Contact(parent=account_utils.get_parent_key(user), id=phone_number)
                contact.list_keys = original_contact.list_keys
                original_contact.key.delete()  # Remove the old one to avoid a duplicate contact.
            
        else:
            contact = Contact(parent=account_utils.get_parent_key(user), id=phone_number)

        # Update all fields other than the list_keys field.    Leave it alone in case this is an edit.
        contact.nickname = self.request.get('nickname')
        contact.phone_number = phone_number
        contact.real_first_name = self.request.get('real_first_name')
        contact.real_last_name = self.request.get('real_last_name')
        contact.email = self.request.get('email')
        contact.other_info = self.request.get('other_info')
        
        contact.put()
        self.redirect("/contacts")


class AddListAction(base_handlers.BaseAction):
    """Create a new list and go straight into editing it."""
    def handle_post(self, user, account_info):
        new_list = ContactList(parent=account_utils.get_parent_key(user),
                                                            name=self.request.get('name'))
        new_list.put()
        self.redirect("/list?list_key=" + new_list.key.urlsafe())


class UpdateListAction(base_handlers.BaseAction):
    """Update the contacts that are in this list."""
    def handle_post(self, user, account_info):
        contact_list_name = self.request.get('contact_list_name')
        urlsafe_entity_key = self.request.get('contact_list_entity_key')
        urlsafe_contact_keys_to_add = self.request.get('contact_keys_to_add')
        urlsafe_contact_keys_to_remove = self.request.get('contact_keys_to_remove')

        add_to_keys = urlsafe_contact_keys_to_add.split(",")
        remove_from_keys = urlsafe_contact_keys_to_remove.split(",")

        contact_list_key = ndb.Key(urlsafe=urlsafe_entity_key)
        for add_to_key in add_to_keys:
            if len(add_to_key) > 0:
                contact = ndb.Key(urlsafe=add_to_key).get()
                contact.list_keys.append(contact_list_key)
                contact.put()
        for remove_from_key in remove_from_keys:
            if len(remove_from_key) > 0:
                contact = ndb.Key(urlsafe=remove_from_key).get()
                contact.list_keys.remove(contact_list_key)
                contact.put()

        # Update the list name if necessary.
        contact_list = contact_list_key.get()
        if contact_list_name != contact_list.name:
            contact_list.name = contact_list_name
            contact_list.put()

        self.redirect("/lists")


class InsertTextMessageEventAction(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        user = users.get_current_user()
        
        # If this is an "edit" start by deleting the old event and just make a new one from scratch.
        # Note, "edits" like this only work if there is no other data saved on the object.
        urlsafe_text_message_event_key = self.request.get("urlsafe_text_message_event_key")
        if urlsafe_text_message_event_key:
            text_message_event_key = ndb.Key(urlsafe=urlsafe_text_message_event_key)
            message_utils.delete_text_message_event(text_message_event_key.get())

        # Create a new text message event
        text_message_event = TextMessageEvent(parent=account_utils.get_parent_key(user),
                                                                                    message_body=self.request.get("message_body"))
        
        # Determine the send_datetime (making sure it's in UTC).
        send_now = False
        if self.request.get("when_radio_group") == "scheduled":
            send_datetime = date_utils.get_utc_datetime_from_user_input(account_utils.get_account_info(user).time_zone,
                                                                                                                                    self.request.get("send_date_time"))
        elif self.request.get("when_radio_group") == "now":
            send_datetime = datetime.now()
            send_now = True
        else:
            raise Exception("Invalid send time radio selected.")
        text_message_event.send_datetime = send_datetime
        
        # Determine who the text message is to
        if self.request.get("to_radio_group") == "list":
            text_message_event.recipient_type = TextMessageEvent.RecipientType.LIST
            text_message_event.recipient_list_key = ndb.Key(urlsafe=self.request.get("to_list"))
        elif self.request.get("to_radio_group") == "individual":
            text_message_event.recipient_type = TextMessageEvent.RecipientType.INDIVIDUAL
            text_message_event.recipient_contact_key = ndb.Key(urlsafe=self.request.get("to_individual"))
        elif self.request.get("to_radio_group") == "all":
            text_message_event.recipient_type = TextMessageEvent.RecipientType.ALL
        else:
            raise Exception("Invalid recipient type")
        
        if self.get_uploads() and len(self.get_uploads()) == 1:
            logging.info("Received an image blob with this text message event.")
            media_blob = self.get_uploads()[0]
            text_message_event.media_blob_key = media_blob.key()
        else:
            # There is a chance this is an edit in which case we should check for an existing blob key.
            original_blob_key = self.request.get("original_blob_key")
            if original_blob_key:
                logging.info("Attaching original blob key (this must have been an edit or duplicate)")
                text_message_event.media_blob_key = BlobKey(original_blob_key)
            else:
                logging.info("This message is an SMS without an image attachment.")

        
        # TODO: Send the message, schedule the message, or do nothing (if it is too far away).
        # Note, each path should perform a .put() on the text message event (at the time of its choosing).
        if send_now:
            message_utils.send_message_now(text_message_event)
        else:
            if date_utils.is_within_next_24_hours(text_message_event.send_datetime):
                message_utils.add_text_message_event_to_task_queue(text_message_event)
            else: 
                logging.info("Text message event saved, but not added to the task queue because it is not within the next 24 hours.")
                text_message_event.put()
        text_message_event.put()  # For now just make sure the event is saved without doing any sending
        
        self.redirect("/text-messages")
