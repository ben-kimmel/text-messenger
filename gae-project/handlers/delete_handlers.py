from google.appengine.api import users
from google.appengine.ext import ndb
from utils import contact_utils, message_utils
import webapp2


class DeleteContactAction(webapp2.RequestHandler):
  def post(self):
    contact_key = ndb.Key(urlsafe=self.request.get('contact_to_delete_key'))
    contact_key.delete();
    self.redirect(self.request.referer)


class DeleteListAction(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()
    list_key = ndb.Key(urlsafe=self.request.get('list_to_delete_key'))
    contact_utils.remove_list_from_all_contacts(user, list_key)
    list_key.delete();
    self.redirect("/lists")  # Hardcoded uri since delete is on the /list page


class DeleteTextMessageEventAction(webapp2.RequestHandler):
  def post(self):
    text_message_event_key = ndb.Key(urlsafe=self.request.get('text_message_event_to_delete_key'))
    message_utils.delete_text_message_event(text_message_event_key.get())
    self.redirect("/text-messages")  # Hardcoded uri in case we allow delete from the /create page.
