from twilio import twiml

from utils import account_utils
import webapp2


# These are simple auto responders to SMS and voice calls.    These need to be setup with Twilio!!!
# Within Twilio set your account auto voice and auto SMS responders as follows:
# A call comes in... Webhook ==>    http://yourusername-textmessenger.appspot.com/voice-auto-reply
# A message comes in... Webhook ==> http://yourusername-textmessenger.appspot.com/sms-auto-reply
class VoiceReply(webapp2.RequestHandler):
    """ Simple reply if someone calls any phone number. """

    def post(self):
        """ Fancy way to generate the following HTML:
                <?xml version="1.0" encoding="UTF-8"?>
                <Response>
                        <Say voice="alice">This number is really meant for SENDING text messages only.</Say>
                </Response>
                For more visit: https://www.twilio.com/docs/api/twiml/say
        """
        account_sid = self.request.get("AccountSid")
        message_body = self.request.get("Body")
        to_number = self.request.get("To")
        from_number = self.request.get("From")    # Could use this to lookup the contact.
        from_city = self.request.get("FromCity")
        from_state = self.request.get("FromState")
        # CONSIDER: Could use other fields in interesting ways. For example if this user knows the person could give a custom response.
        
        r = twiml.Response()
        account_info = account_utils.get_account_info_from_sid(account_sid)
        if account_info and account_info.auto_response_voice:
            r.say(account_info.auto_response_voice, voice=twiml.Say.WOMAN, loop=2)
#             Could also play mp3 files
#             r.play(url="/static/audio/voicemail_test.mp3")
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.write(str(r))


class SmsReply(webapp2.RequestHandler):
        """ Simple reply if someone responds to a text message. 
                Fancy way to generate the following HTML:
                        <?xml version="1.0" encoding="UTF-8"?>
                        <Response>
                                <Sms>This number is really meant for SENDING text messages only.</Sms>
                        </Response>
        
                        For more visit: https://www.twilio.com/docs/api/twiml/sms
        """

        def post(self):
            account_sid = self.request.get("AccountSid")
            message_body = self.request.get("Body")
            to_number = self.request.get("To")
            from_number = self.request.get("From")    # Could use this to lookup the contact.
            from_city = self.request.get("FromCity")
            from_state = self.request.get("FromState")
            # CONSIDER: Could use other fields in interesting ways. For example if this user knowns the person could give a custom response.
            
            # Twilio library code:    https://github.com/twilio/twilio-python
            # Twilio library docs: http://twilio-python.readthedocs.io/en/latest/usage/twiml.html
            r = twiml.Response()
            account_info = account_utils.get_account_info_from_sid(account_sid)
            if account_info and account_info.auto_response_sms:
                r.message(account_info.auto_response_sms)

            self.response.headers['Content-Type'] = 'text/xml'
            self.response.write(str(r))