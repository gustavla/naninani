#!/usr/bin/env python
#coding: utf-8
import urllib
import urllib2
import cookielib
import httplib
from HTMLParser import HTMLParser

class WebClient:
	def __init__(self):
		self.pwmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(), urllib2.HTTPBasicAuthHandler(self.pwmgr))
		self.opener.addheaders = [('User-agent', 'Mozilla/5.0')] #could help
		httplib.HTTPConnection.debuglevel = 1 
	def setAuth(self, url, user, pwd):
		"url should be base url only!"
		self.pwmgr.add_password(None, url, user, pwd)
	def get(self, url):
		fp = self.opener.open(url)
		s = fp.read()
		fp.close()
		return s
	def post(self, url, data):
		if not (isinstance(data, str) or isinstance(data, unicode)):
			data = urllib.urlencode(data)
		try:
			fp = self.opener.open(url, data)
			s = fp.read()
			fp.close()
			return s
		except urllib2.HTTPError, e:
			print e
		

def extractInputFields(html):
	res = {}
	class InputParser(HTMLParser):
		def handle_starttag(self, tag, attrs):
			if tag == 'input':
				d = dict(attrs)
				if d.has_key('name'):
					if not d.has_key('value'):
						d['value'] = '';
					res[d['name']] = d['value']
	parser = InputParser()
	parser.feed(html)
	parser.close()
	return res
	
