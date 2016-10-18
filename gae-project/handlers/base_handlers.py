
from google.appengine.api import users
import main
from utils import account_utils
import webapp2


### Pages ###

class BasePage(webapp2.RequestHandler):
  """Page handlers should inherit from this one."""
  def get(self):
    user = users.get_current_user()
    if not user:
      raise Exception("Missing user!")
    account_info = account_utils.get_account_info(user)
    values = {"user_email": user.email().lower(),
              "account_info": account_info,
              "logout_url": users.create_logout_url("/")}
    self.update_values(user, values)
    template = main.jinja_env.get_template(self.get_template())
    self.response.out.write(template.render(values))

  def update_values(self, user, values):
    # Subclasses should override this method to add additional data.
    pass

  def get_template(self):
    # Subclasses must override this method to set the Jinja template.
    raise Exception("Subclass must implement handle_post!")
    pass


### Actions ###

class BaseAction(webapp2.RequestHandler):
  """ALL action handlers should inherit from this one."""
  def post(self):
    user = users.get_current_user()
    if not user:
      raise Exception("Missing user!")
    account_info = account_utils.get_account_info(user)
    self.handle_post(user, account_info)

  def get(self):
    self.post()  # Just makes sure not subclasses try to make a simple quick and dirty page out of an Action.

  def handle_post(self, user, account_info):
    raise Exception("Subclass must implement handle_post!")
