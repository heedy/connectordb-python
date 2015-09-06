# -*- coding: utf-8 -*-

from _connectorobject import ConnectorObject

import _user
import _stream


class Device(ConnectorObject):
    def create(self):
        """Creates the device."""
        self.metadata = self.db.create(self.path).json()

    def streams(self):
        """Returns the list of streams that belong to the device"""
        result = self.db.read(self.path, {"q": "ls"})

        if result is None or result.json() is None:
            return []
        streams = []
        for s in result.json():
            strm = self[s["name"]]
            strm.metadata = s
            streams.append(strm)
        return streams

    def __getitem__(self, stream_name):
        """Gets the child stream by name"""
        return _stream.Stream(self.db, self.path + "/" + stream_name)

    def __repr__(self):
        """Returns a string representation of the device"""
        return "[Device:%s]" % (self.path, )

    # -----------------------------------------------------------------------
    # Following are getters and setters of the device's properties

    @property
    def apikey(self):
        """gets the device's api key"""
        if "apikey" in self.data:
            return self.data["apikey"]
        return None

    def reset_apikey(self):
        """invalidates the device's current api key, and generates a new one"""
        self.set({"apikey": ""})
        return self.metadata["apikey"]

    @property
    def user(self):
        """user returns the user which owns the given device"""
        return _user.User(self.db, self.path.split("/")[0])
