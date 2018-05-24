import yaml
from socket import *


class RemoteController:
    """Class containing list of rooms given in yaml file
        Each room contain list of appliances
    """

    def __init__(self, filename):
        self.rooms_list = self.__parse_yaml__(filename)

    @staticmethod
    def __parse_yaml__(filename):

        with open(filename, 'r') as stream:
            try:
                data = (yaml.load(stream))
            except yaml.YAMLError as exc:
                print(exc)

        rooms = []
        for stuff_list in [list(room.items()) for room in data]:
            rooms.append(
                Room(stuff_list[0][0], [Appliance(appliance[0], appliance[1]) for appliance in stuff_list[1:]]))
        return rooms

    def __str__(self):
        string = []
        for room in self.rooms_list:
            string.append(room.name + "\n")
            for appliance in room.stuff:
                string.append(appliance.function + " " + appliance.name + " " + appliance.state + "\n")
            string.append("\n")
        return "".join(string)


class Room:
    """Class containing name and list of appliances"""

    def __init__(self, name, stuff):
        self.name = name
        self.stuff = stuff


class Appliance:
    """Class representing single appliance
        Appliance has ability to change own state
        and send necessary information to given socket
    """

    def __init__(self, fun, name, state=False):
        self.function = fun
        self.name = name
        self.state = state

    def toggle_state(self):
        self.state = not self.state
        self.send_to_socket()

    def send_to_socket(self):
        message = ("on " if self.state else "off ") + self.function
        udp_sock = socket(AF_INET, SOCK_DGRAM)
        udp_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        udp_sock.sendto(message.encode('utf8'), ("255.255.255.255", 2018))
        udp_sock.close()


