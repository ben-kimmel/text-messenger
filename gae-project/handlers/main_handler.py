import logging
import google.appengine.api.blobstore.blobstore as blobstore

from google.appengine.ext import ndb
from handlers import base_handlers
from models import TextMessageEvent
from utils import contact_utils, message_utils


### Pages ###
class MainHandler(base_handlers.BasePage):
    def get_template(self):
        return "templates/main_menu.html"


class AccountInfoPage(base_handlers.BasePage):
    def get_template(self):
        return "templates/account_info.html"

    def update_values(self, user, values):
        values["timezones"] = ["US/Pacific", "US/Mountain", "US/Central", "US/Eastern"]


class ContactsPage(base_handlers.BasePage):
    def get_template(self):
        return "templates/contacts.html"

    def update_values(self, user, values):
        values["contacts"] = contact_utils.get_contacts_for_user(user)


class ListsPage(base_handlers.BasePage):
    def get_template(self):
        return "templates/lists.html"

    def update_values(self, user, values):
        lists = contact_utils.get_lists(user)
        values["lists"] = lists
        
        # Add a string onto each list showing the contacts.
        list_contacts_map = {}
        for contact_list in lists:
            list_contacts_map[contact_list.key.urlsafe()] = ""
        contacts = contact_utils.get_contacts_for_user(user)
        for contact in contacts:
            for contact_list_key in contact.list_keys:
                current_contacts = list_contacts_map[contact_list_key.urlsafe()]
                if current_contacts:
                    current_contacts += ", "
                current_contacts += contact.nickname
                list_contacts_map[contact_list_key.urlsafe()] = current_contacts 
        values["list_contacts_map"] = list_contacts_map
        

class ListDetailPage(base_handlers.BasePage):
    def get_template(self):
        return "templates/list.html"

    def update_values(self, user, values):
        contact_list = ndb.Key(urlsafe=self.request.get('list_key')).get()
        contacts = contact_utils.get_contacts_for_user(user)
        contacts_in_list = []
        contacts_not_in_list = []
        for contact in contacts:
            if contact_list.key in contact.list_keys:
                contacts_in_list.append(contact)
            else:
                contacts_not_in_list.append(contact)
        values["contact_list"] = contact_list
        values["contacts_in_list"] = contacts_in_list
        values["contacts_not_in_list"] = contacts_not_in_list


class TextMessagesPage(base_handlers.BasePage):
    def get_template(self):
        return "templates/text_messages.html"

    def update_values(self, user, values):
        values["text_messages_that_did_not_send"] = message_utils.get_unsent_text_message_events_for_user(user)
        values["text_messages_pending"] = message_utils.get_pending_text_message_events_for_user(user)
        values["text_messages_sent"] = message_utils.get_sent_text_message_events_for_user(user, None)


class CreateMessagePage(base_handlers.BasePage):
    def get_template(self):
        return "templates/create_message.html"

    def update_values(self, user, values):
        # Load all the contacts and contact lists for the TO select elements.
        values["contacts"] = contact_utils.get_contacts_for_user(user)
        values["contact_lists"] = contact_utils.get_lists(user)
        values["form_action"] = blobstore.create_upload_url('/insert-text-message-event')
                
        # If this is an edit or duplicate prepopulate some fields.
        urlsafe_edit_key = self.request.get("edit")
        urlsafe_duplicate_key = self.request.get("duplicate")
        if urlsafe_edit_key or urlsafe_duplicate_key:
            if urlsafe_edit_key:
                edit_key = ndb.Key(urlsafe=urlsafe_edit_key)
                text_message_event = edit_key.get()
                values["is_edit"] = True
            elif urlsafe_duplicate_key:
                duplicate_key = ndb.Key(urlsafe=urlsafe_duplicate_key)
                text_message_event = duplicate_key.get()
                
            values["text_message_event"] = text_message_event
            if text_message_event.recipient_type == TextMessageEvent.RecipientType.LIST:
                recipient_contact_list = text_message_event.recipient_list_key.get()
                values["text_message_event_list_name"] = recipient_contact_list.name
            elif text_message_event.recipient_type == TextMessageEvent.RecipientType.INDIVIDUAL:
                recipient_contact = text_message_event.recipient_contact_key.get() 
                logging.info("Put in " + recipient_contact.display_nickname_and_name())
                values["text_message_event_individual_name"] = recipient_contact.display_nickname_and_name()
