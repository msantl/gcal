#!/usr/bin/env python
import imaplib, re
import sys
import datetime
import os
from xml.etree import ElementTree
import gdata.calendar.client
import gdata.acl.data
import gdata.calendar.data
import string
import base64

CONFIGPATH="/home/matija/scripts/gcal/.config.ini"

def get_user_and_pass():
	username = ""
	password = ""
	dpassword = ""

	try:
		dat = open( CONFIGPATH, "r" )
		for line in dat:
			line = line.strip()
			match = re.search( r"<user>[\w.@]+</user>", line )
			if match: username = line.split(">")[1].split("<")[0]
			match = re.search( r"<pass>.+</pass>", line )
			if match: dpassword = line.split(">")[1].split("<")[0]
	
		password = base64.b64decode( dpassword )
		dat.close()

	except IOError as e:
		print "If you are running this script for the first time, you need to enter your email and password for your google account"
		print "Email address: ",
		username = raw_input().strip()
		print "Password: ",
		password = raw_input().strip();

		dpassword = base64.b64encode( password )

		dat = open( CONFIGPATH, "w" );

		dat.write( "<user>%s</user>\n<pass>%s</pass>\n" % ( username, dpassword ) )

		dat.close()
	
	return (username, password)


class gcal:
	"""docstring for gcal"""
	def __init__(self, email, password):
		
		self.cal_client = gdata.calendar.client.CalendarClient( source="Ferko kalendar" )
		try:
			self.cal_client.ClientLogin( email, password, self.cal_client.source );
		except:
			print "Looks like you entered your credentials wrong"
			os.remove( CONFIGPATH )
			sys.exit(1)
		
	def get_agenda(self, start, end):
		"""docstring for get_agenda"""
		feed = self.cal_client.GetAllCalendarsFeed()
		raspored = list()
		query = gdata.calendar.client.CalendarEventQuery( start_min=start, start_max=end )

		for event in feed.entry:
			cfeed = self.cal_client.GetCalendarEventFeed( q=query, uri=event.link[0].href )

			for cevent in cfeed.entry:
				raspored.append( (cevent.title.text, cevent.when[0].start[11:16]) )

		return raspored

def main():
	username, password = get_user_and_pass();
	
	today = datetime.date.today()
	tomorrow = today + datetime.timedelta(days=1)

	g = gcal( username, password )

	danas = datetime.datetime.utcnow().isoformat('T') + 'Z'	
	
	raspored = g.get_agenda( start=danas, end=tomorrow.isoformat() )

	count = len( raspored )
	counter = 0
	LINEMAX = 8

	for event, start in sorted( raspored, key=lambda event: event[1]  ):
		print ("%-27s%s" % ( event[0:25], start )).encode('utf-8')
		counter = counter + 1
		if counter > LINEMAX:
			break;

	if count > LINEMAX:
		print "... and more"
	
	if count == 0:
		print "Seems like you have a day off."

	return 0

if __name__ == "__main__":
    main()

