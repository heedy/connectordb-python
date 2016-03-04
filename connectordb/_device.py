from __future__ import absolute_import

from ._connectorobject import ConnectorObject


class Device(ConnectorObject):
    def create(self, public=False, **kwargs):
        """Creates the device. Attempts to create private devices by default,
        but if public is set to true, creates public devices.

        You can also set other default properties by passing in the relevant information.
        For example, setting a device with the given nickname and description::

            dev.create(nickname="mydevice", description="This is an example")

        Furthermore, ConnectorDB supports creation of a device's streams immediately,
        which can considerably speed up device setup::

            dev.create(streams={
                "stream1": {"schema": "{\"type\":\"number\"}"}
            })

        Note that the schema must be encoded as a string when creating in this format.
        """
        kwargs["public"] = public
        self.metadata = self.db.create(self.path,kwargs).json()

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
        return Stream(self.db, self.path + "/" + stream_name)

    def __repr__(self):
        """Returns a string representation of the device"""
        return "[Device:%s]" % (self.path, )

    # -----------------------------------------------------------------------
    # Following are getters and setters of the device's properties

    @property
    def apikey(self):
        """gets the device's api key. Returns None if apikey not accessible."""
        if "apikey" in self.data:
            return self.data["apikey"]
        return None

    def reset_apikey(self):
        """invalidates the device's current api key, and generates a new one"""
        self.set({"apikey": ""})
        return self.metadata["apikey"]


    @property
    def public(self):
        """gets whether the device is public
        (this means different things based on connectordb permissions setup - connectordb.com
        has this be whether the device is publically visible. Devices are individually public/private.)
        """
        if "public" in self.data:
            return self.data["public"]
        return None

    @public.setter
    def public(self,new_public):
        """Attempts to set whether the device is public"""
        self.set({"public": new_public})

    @property
    def role(self):
        """Gets the role of the device. This is the permissions level that the device has. It might
        not be accessible depending on the permissions setup of ConnectorDB. Returns None if not accessible"""
        if "role" in self.data:
            return self.data["role"]
        return None

    @role.setter
    def role(self,new_role):
        """ Attempts to set the device's role"""
        self.set({"role": new_role})

    @property
    def user(self):
        """user returns the user which owns the given device"""
        return User(self.db, self.path.split("/")[0])


# The import has to go on the bottom because py3 imports are annoying about circular dependencies
from ._user import User
from ._stream import Stream
