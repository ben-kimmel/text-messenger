from datetime import datetime, timedelta
import logging
import pytz


def get_utc_datetime_from_user_input(tz_str, date_time_str):
  """Returns a datetime object from a string, taking into account the time zone for that string.
     Note that the date_time_str must be in the one and only acceptable format %m-%d-%Y %I:%M %p"""
  try:
    tz = pytz.timezone(tz_str)  # Convert the time zone string into a time zone object.
  except:
    logging.warn("Time zone string did NOT parse.  tz_str = " + tz_str)
    tz = pytz.utc
  
  # Convert the string into a datetime object (time zone naive)
  send_datetime_raw = datetime.strptime(date_time_str, "%m-%d-%Y %I:%M %p")
  
  # Set the time zone to the user's preference value (make the datetime object time zone aware instead of time zone naive).
  send_datetime_in_user_tz = send_datetime_raw.replace(tzinfo=tz)
  
  # Adjust for Daylight Savings Time if appropriate (only an issue in the US March-November).
  send_datetime_adj_for_dst = send_datetime_in_user_tz - tz.normalize(send_datetime_in_user_tz).dst()

  # Shift the time to UTC time (all datetime objects stored on the server should always be in UTC no exceptions)
  send_datetime_in_utc = send_datetime_adj_for_dst.astimezone(pytz.utc)

  # Used during development to make sure I did the time zone stuff correctly.
#   print("send_datetime = " + date_time_display_format(send_datetime_in_utc, "UTC"))
#   print("now           = " + date_time_display_format(datetime.now(), "UTC"))
  
  # Then remove the tzinfo to make the datatime again time zone naive, which is how AppEngine stores the time. (naive but known to be UTC)  
  return send_datetime_in_utc.replace(tzinfo=None)


def is_within_next_24_hours(send_time):
  """Returns true if the datetime object passed in is within the next 24 hours."""
  one_day = timedelta(1)  # Create a timedelta object set to 1 day long
  time_delta = send_time - datetime.utcnow()  # Creates a timedelta ojbect that is the difference between now and the send_time
  return time_delta.total_seconds() > 0 and time_delta < one_day 


def get_seconds_since_epoch(datetime):
  """Returns the seconds since epoch.  Note, this function is not used in this app I just like it."""
  return int(datetime.strftime("%s"))


# ## Jinja filters
        
def date_time_input_format(value, tz_str):
  """Take a date time object and convert it into a string that uses the required input box format.
     Note, this format MUST match the format used in the get_utc_datetime_from_user_input function."""
  try:
    tz = pytz.timezone(tz_str)
  except:
    tz = pytz.utc
  value = value.replace(tzinfo=pytz.utc).astimezone(tz)
  return value.strftime("%m-%d-%Y %I:%M %p")


def date_time_display_format(value, tz_str):
  """Take a date time object and convert it into a string that can be displayed in the text message event tables."""
  try:
    tz = pytz.timezone(tz_str)
  except:
    tz = pytz.utc
  value = value.replace(tzinfo=pytz.utc).astimezone(tz)
  if value.year == value.now(tz).year:
    # current year
    if value.month == value.now(tz).month and value.day == value.now(tz).day:
      # today, just show the time
      format_str = "Today %I:%M %p %Z"
    else:
      # otherwise show the month and day
      format_str = "%b %d %I:%M %p %Z"
  else:
    # previous year, show the year, too
    format_str = "%m/%d/%y %I:%M %p %Z"
  return value.strftime(format_str)
