import logging

from google.appengine.ext import ndb
from models import AccountInfo


# Different helper methods to get the parent key.
def get_parent_key_from_email(email):
  return ndb.Key("Entity", email.lower())

def get_parent_key(user):
  return get_parent_key_from_email(user.email())



# Different helper methods to get the account_info.
def get_account_info_from_email(email):
  """Gets the one and only AccountInfo object for this email. Returns None if AccountInfo object doesn't exist"""
  email = email.lower()  # Just in case.
  parent_key = get_parent_key_from_email(email)
  return AccountInfo.get_by_id(email, parent=parent_key)
  
  
def get_account_info(user):
  """Gets the one and only AccountInfo object for this user.  Creates a new AccountInfo object if none exist."""
  email = user.email().lower()
  account_info = get_account_info_from_email(email)

  if not account_info:
      parent_key = get_parent_key(user)
      logging.info("Creating a new AccountInfo for new user " + email)
      account_info = AccountInfo(parent=parent_key, id=email)
      account_info.put()

  return account_info


def get_account_info_from_sid(account_sid):
  """Gets the account info for a given Twilio account sid"""
#   return AccountInfo.query(AccountInfo.twilio_sid == account_sid).fetch(1)[0]
  return AccountInfo.query(AccountInfo.twilio_sid == account_sid).get()
  
