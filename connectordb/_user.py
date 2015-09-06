# -*- coding: utf-8 -*-

from _connectorobject import ConnectorObject

import _device


class User(ConnectorObject):
    def create(self, email, password):
        """Creates the given user - using the passed in email and password"""
        self.metadata = self.db.create(
            self.path, {"email": email,
                        "password": password}).json()

    def set_password(self, new_password):
        """Sets a new password for the user"""
        self.set({"password": new_password})

    def devices(self):
        """Returns the list of devices that belong to the user"""
        result = self.db.read(self.path, {"q": "ls"})

        if result is None or result.json() is None:
            return []
        devices = []
        for d in result.json():
            dev = self[d["name"]]
            dev.metadata = d
            devices.append(dev)
        return devices

    def __getitem__(self, device_name):
        """Gets the child device by name"""
        return _device.Device(self.db, self.path + "/" + device_name)

    def __repr__(self):
        """Returns a string representation of the user"""
        return "[User:%s]" % (self.path, )

    # -----------------------------------------------------------------------
    # Following are getters and setters of the user's properties

    @property
    def email(self):
        """gets the user's email address"""
        if "email" in self.data:
            return self.data["email"]
        return None

    @email.setter
    def email(self, new_email):
        """sets the user's email address"""
        self.set({"email": new_email})
