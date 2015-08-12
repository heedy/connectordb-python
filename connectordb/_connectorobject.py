# -*- coding: utf-8 -*-



class ConnectorObject(object):

	def __init__(self,database_connection,object_path):
		self.db = database_connection
		self.path = object_path

		#Metadata represents the object's json representation
		self.metadata = None

	def refresh(self):
		"""Refresh reloads data from the server"""
		self.metadata = self.db.read(self.path).json()

	@property
	def data(self):
		"""Returns the raw dict representing metadata"""
		if self.metadata is None:
			self.refresh()
		return self.metadata

	def delete(self):
		"""Deletes the user/device/stream"""
		self.db.delete(self.path)

	def exists(self):
		"""returns true if the object exists, and false otherwise"""
		try:
			self.refresh()
		except:
			return False
		return True

	def set(self,property_dict):
		"""Attempts to set the given properties of the object"""
		self.metadata = self.db.update(self.path, property_dict).json()

	@property
	def name(self):
		"""Returns the object's name. Object names are immutable (unless logged in is a database admin)"""
		return self.data["name"]
	@name.setter
	def name(self,new_name):
		"""Attempts to rename the object - this won't end well unless logged in as a database administrator. And even then it is a dangerous thing to do.
		The recommendation is never to do this. In fact, in the future, name changes might be disabled altogether."""
		self.set({"name": new_name})

	@property
	def nickname(self):
		"""Returns the object's user-friendly nickname"""
		if "nickname" in self.data:
			return self.data["nickname"]
		return None
	@nickname.setter
	def nickname(self,new_nickname):
		"""Sets the object's user-friendly nickname"""
		self.set({"nickname": new_nickname})
