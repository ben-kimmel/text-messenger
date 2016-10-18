from models import Contact, ContactList
from utils import account_utils


# Different helper methods to get all contacts for this user.
def get_contacts_for_email(email):
  """ Gets all of the contacts for this email address. """
  return get_contacts_for_parent_key(account_utils.get_parent_key_from_email(email))

def get_contacts_for_user(user):
  """ Gets all of the contacts for this user. """
  return get_contacts_for_parent_key(account_utils.get_parent_key(user))

def get_contacts_for_parent_key(parent_key):
  """ Gets all of the contacts under this parent key. """
  return Contact.query(ancestor=parent_key).order(Contact.nickname).fetch()


# Returns only the contacts in a given list.
def get_contacts_for_list_key(list_key):
  creators_email = list_key.parent().string_id()
  parent_key = account_utils.get_parent_key_from_email(creators_email)
  return Contact.query(ancestor=parent_key).order(Contact.nickname, Contact.key).filter(Contact.list_keys.IN([list_key])).fetch()
  

def get_lists(user):
  """ Gets all of the lists for this user. """
  return ContactList.query(ancestor=account_utils.get_parent_key(user)).order(ContactList.name).fetch()


def remove_list_from_all_contacts(user, list_key):
  """ Removes the list from all contacts. """
  contacts = get_contacts_for_user(user)
  for contact in contacts:
    if list_key in contact.list_keys:
      contact.list_keys.remove(list_key)
      contact.put()
