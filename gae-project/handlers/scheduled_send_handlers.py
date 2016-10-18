from datetime import datetime, timedelta
import logging, json

from google.appengine.ext import ndb
import webapp2

from models import TextMessageEvent
from utils import message_utils



CRON_JOB_INTERVAL_H = 24

class CronCheckMessagesForSends(webapp2.RequestHandler):
    """ Daily cron job to check for messages that need to be queued up for the day."""
    def get(self):
        now = datetime.now()
        next_check = now + timedelta(hours=(CRON_JOB_INTERVAL_H + 1))
        query = TextMessageEvent.query(ndb.AND(TextMessageEvent.has_been_sent == False, ndb.AND(TextMessageEvent.send_datetime >= now, TextMessageEvent.send_datetime < next_check))).order(TextMessageEvent.send_datetime)
        num_text_messages_events_scheduled = 0
        for text_message_event in query.fetch():
            num_text_messages_events_scheduled += 1
            # Originally we just sent the message during the cron job now we'll schedule a task. 
            message_utils.add_text_message_event_to_task_queue(text_message_event)

        logging.info("Scheduled " + str(num_text_messages_events_scheduled) + " text messages from cron job.")
        self.response.out.write("Checked for messages to schedule.    Scheduled " + str(num_text_messages_events_scheduled) + " text messages.") 
        
class QueueSendMessage(webapp2.RequestHandler):
    """ Sends the SMS message."""
    
    def post(self):
        logging.info("Fired task queue")
        payload = json.loads(self.request.body)
        urlsafe_entity_key = payload["urlsafe_entity_key"]
        text_message_event_key = ndb.Key(urlsafe=urlsafe_entity_key)
        message_utils.send_text_messages_for_event_key(text_message_event_key)