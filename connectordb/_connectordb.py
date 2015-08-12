# -*- coding: utf-8 -*-
import json
import time

from urlparse import urljoin

from requests import Session
from requests.auth import HTTPBasicAuth

from _connection import DatabaseConnection

from _device import Device
from _user import User
from _stream import Stream

class ConnectorDB(Device):
	def __init__(self,user_or_apikey,user_password=None,url="https://connectordb.com"):

		db = DatabaseConnection(user_or_apikey,user_password,url)

		Device.__init__(self,db, db.ping())

	def __call__(self, path):
		"""Enables getting arbitrary users/devices/streams in a simple way. Just call the object
		with the u/d/s uri
			cdb = ConnectorDB("myapikey")
			cdb("user1") -> user1 object
			cdb("user1/device1") -> user1/device1 object
			cdb("user1/device1/stream1") -> user1/device1/stream1 object
		"""
		n = path.count("/")
		if n==0:
			return User(self.db,path)
		elif n==1:
			return Device(self.db,path)
		else:
			return Stream(self.db,path)

	def close(self):
		"""shuts down all active connections to ConnectorDB"""
		self.db.close()

	def count_users(self):
		"""Gets the total number of users registered with the database. Only available to administrator."""
		return int(self.db.get("",{"q":"countusers"}).text)
	def count_devices(self):
		"""Gets the total number of devices registered with the database. Only available to administrator."""
		return int(self.db.get("",{"q":"countdevices"}).text)
	def count_streams(self):
		"""Gets the total number of streams registered with the database. Only available to administrator."""
		return int(self.db.get("",{"q":"countstreams"}).text)

	def info(self):
		"""returns a dictionary of information about the database, including the database version, the transforms
		and the interpolators supported"""
		return {
			"version": self.db.get("meta/version").text,
			"transforms": self.db.get("meta/transforms").json(),
			"interpolators": self.db.get("meta/interpolators").json()
		}

	def __repr__(self):
		return "[ConnectorDB:%s]"%(self.path,)
