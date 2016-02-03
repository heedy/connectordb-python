from __future__ import absolute_import

from ._connectorobject import ConnectorObject


class User(ConnectorObject):
    def create(self, email, password, role="user", public=True):
        """Creates the given user - using the passed in email and password"""
        self.metadata = self.db.create(
            self.path, {"email": email,
                        "password": password,
                        "role": role,
                        "public": public}).json()

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
        return Device(self.db, self.path + "/" + device_name)

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

    @property
    def public(self):
        """gets whether the user is public
        (this means different things based on connectordb permissions setup - connectordb.com
        has this be whether the user is publically visible. Devices are individually public/private.)
        """
        if "public" in self.data:
            return self.data["public"]
        return None

    @public.setter
    def public(self,new_public):
        """Attempts to set whether the user is public"""
        self.set({"public": new_public})

    @property
    def role(self):
        """Gets the role of the user. This is the permissions level that the user has. It might
        not be accessible depending on the permissions setup of ConnectorDB. Returns None if not accessible"""
        if "role" in self.data:
            return self.data["role"]
        return None

    @role.setter
    def role(self,new_role):
        """ Attempts to set the user's role"""
        self.set({"role": new_role})

# The import has to go on the bottom because py3 imports are annoying
from ._device import Device
