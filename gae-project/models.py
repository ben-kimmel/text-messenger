from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from protorpc.messages import Enum


class AccountInfo(ndb.Model):
        """ Information about the Twilio account to use with this user and other global info for this user.
                Note there is only 1 of these per user. """

        # Twilio account info for this user
        twilio_sid = ndb.StringProperty(default="")
        twilio_auth_token = ndb.StringProperty(default="")
        twilio_phone_number = ndb.StringProperty(default="")

        # Time zone to be used when setting the time that the Text Messages will be sent
        time_zone = ndb.StringProperty(default="US/Eastern")

        # Optional signature text.    This will replace the word SIG in text messages (optional feature).
        signature_text = ndb.StringProperty(default="")
        
        # Twilio auto responders
        auto_response_voice = ndb.StringProperty(default="")
        auto_response_sms = ndb.StringProperty(default="")


class ContactList(ndb.Model):
        """ Collection of Contacts. """

        # Simple name for this contact list
        name = ndb.StringProperty()

        # Note, Contacts are connected to this list by their list_keys field.


class Contact(ndb.Model):
        """ Individual that can be sent a message. """

        # This String is very important as it will be used in String substitutions if present.
        nickname = ndb.StringProperty(default="")

        # This will be the value put into the 'to' field for text messages in E.164 number format.
        # All of these strings will always start this with the + character (if they don't the user messed up)
        # Examples: +18122729351 (+1 for US numbers), +353860701582 (international number)
        phone_number = ndb.StringProperty(required=True)

        # Real name for the Contact
        real_first_name = ndb.StringProperty(default="Unknown first")
        real_last_name = ndb.StringProperty(default="Unknown last")

        # Email for the Contact
        email = ndb.StringProperty()

        # Optional area to add comments about this Contact.
        other_info = ndb.TextProperty()

        # Lists that this contact is in.
        list_keys = ndb.KeyProperty(kind=ContactList, repeated=True)
        
        def display_nickname_and_name(self):
            """ Returns a string that combines the nickname and real name as a single string for display. """
            return self.nickname + " (" + self.real_first_name + " " + self.real_last_name + ")"


class TextMessageEvent(ndb.Model):
        """ Scheduled (or already fired) text message events. """

        # Boolean that tracks if this text message event has already been sent or not.
        has_been_sent = ndb.BooleanProperty(default=False)
        
        class RecipientType(Enum):
            """Determines if this text message is to a list, an individual, or all contacts."""
            LIST = 1
            INDIVIDUAL = 2
            ALL = 3
        recipient_type = msgprop.EnumProperty(RecipientType, default=RecipientType.ALL)

        # If recipient_type is LIST, this is the list of contacts that will be receiving this message. Otherwise None.
        recipient_list_key = ndb.KeyProperty(kind=ContactList)

        # If recipient_type is INDIVIDUAL, this is the contact that will be receiving this message. Otherwise None.
        recipient_contact_key = ndb.KeyProperty(kind=Contact)

        # The SMS message will fire at this UTC date time.    Cron jobs will check this value.
        send_datetime = ndb.DateTimeProperty()

        # Text message content that will be sent.    Uses the template syntax for NICKNAME and SIG
        # Example: "Hey NICKNAME, have I ever told you... --SIG".
        message_body = ndb.TextProperty()
        media_blob_key = ndb.BlobKeyProperty()
        
        # Boolean that tracks if this text message event has been placed into the task queue for delivery.
        is_in_task_queue = ndb.BooleanProperty(default=False)
        
        def get_task_name(self):
            """ Returns a unique name for this text message event."""
            return self.key.urlsafe()  # Just use the entity key urlsafe string (ugly for display but easy)
