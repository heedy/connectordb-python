# -*- coding: utf-8 -*-

from _connectorobject import ConnectorObject

import _user
import _device

from jsonschema import validate, Draft4Validator
import json
import time

class Stream(ConnectorObject):
	def create(self,schema):
		"""Creates a stream given a JSON schema encoded as a python dict"""
		Draft4Validator.check_schema(schema)
		self.metadata = self.db.create(self.path,schema)

	def insert_array(self,datapoint_array, restamp = False):
		"""given an array of datapoints, inserts them to the stream. This is different from insert(),
		because it requires an array of valid datapoints, whereas insert only requires the data portion
		of the datapoint, and fills out the rest."""
		if restamp:
			self.db.update(self.path+"/data",datapoint_array)
		else:
			self.db.create(self.path+"/data",datapoint_array)

	def insert(self,data):
		"""insert inserts one datapoint with the given data, and appends it to the end of the stream.

			stream[-5:]	#Returns the most recent 5 datapoints from the stream

			stream[:] #Returns all the data the stream holds.

		In order to perform transforms on the stream and to aggreagate data, look at __call__,
		which allows getting index ranges along with a transform.

		"""
		self.insert_array([{"d": data}], restamp=True)


	def __call__(self,t1=None, t2=None, limit=None, i1=None, i2=None, transform=None):
		"""By calling the stream as a function, you can query it by either time range or index,
		and further you can perform a custom transform on the stream

			#Returns all datapoints with their data < 50 from the past minute
			stream(t1=time.time()-60, transform="if $ < 50")

			#Performs an aggregation on the stream, returning a single datapoint
			#which contains the sum of the datapoints
			stream(transform="sum | if last")

		"""
		params = {}
		if not t1 is None:
			params["t1"] = str(t1)
		if not t2 is None:
			params["t2"] = str(t2)
		if not limit is None:
			params["limit"] = str(limit)
		if not i1 is None or not i2 is None:
			if len(params) > 0:
				raise AssertionError("Stream cannot be accessed both by index and by timestamp at the same time.")
			if not i1 is None:
				params["i1"] = str(i1)
			if not i2 is None:
				params["i2"] = str(i2)

		#In order to avoid accidental requests for full streams, ConnectorDB does not permit requests
		#without any url parameters, so we set i1=0 if we are requesting the full stream
		if len(params) == 0:
			params["i1"] = "0"

		if not transform is None:
			params["transform"] = transform

		return self.db.read(self.path + "/data",params).json()

	def __getitem__(self,getrange):
		"""Allows accessing the stream just as if it were just one big python array."""
		if not isinstance(getrange, slice):
			#Return the single datapoint
			return self(i1=getrange,i2=getrange+1)[0]

		#The query is a slice - return the range
		return self(i1=getrange.start, i2=getrange.stop)


	def __len__(self):
		"""taking len(stream) returns the number of datapoints saved within the database for the stream"""
		return int(self.db.read(self.path+"/data",{"q":"length"}).text)

	def __repr__(self):
		"""Returns a string representation of the stream"""
		return "[Stream:%s]"%(self.path,)

	#-----------------------------------------------------------------------
	#Following are getters and setters of the stream's properties

	@property
	def downlink(self):
		"""returns whether the stream is a downlink, meaning that it accepts input (like turning lights on/off)"""
		if "downlink" in self.data:
			return self.data["downlink"]
		return False

	@downlink.setter
	def downlink(self, is_downlink):
		self.set({"downlink": is_downlink})

	@property
	def ephemeral(self):
		"""returns whether the stream is ephemeral, meaning that data is not saved, but just passes through the messaging system."""
		if "ephemeral" in self.data:
			return self.data["ephemeral"]
		return False

	@ephemeral.setter
	def ephemeral(self, is_ephemeral):
		"""sets whether the stream is ephemeral, meaning that it sets whether the datapoints are saved in the database.
		an ephemeral stream is useful for things which are set very frequently, and which could want a subscription, but
		which are not important enough to be saved in the database"""
		self.set({"ephemeral": is_ephemeral})

	@property
	def schema(self):
		"""Returns the JSON schema of the stream as a python dict"""
		if "type" in self.data:
			return json.loads(self.data["type"])
		return None

	@property
	def user(self):
		"""user returns the user which owns the given stream"""
		return _user.User(self.db,self.path.split("/")[0])

	@property
	def device(self):
		"""returns the device which owns the given stream"""
		splitted_path = self.path.split("/")

		return _device.Device(self.db,splitted_path[0] + "/" + splitted_path[1])