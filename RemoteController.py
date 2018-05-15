import sys
import yaml
from enum import Enum
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from socket import *


class RemoteController:

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
        # return [room_object for room_object in [
        #     Room(stuff_list[0][0], [Appliance(appliance[0], appliance[1]) for appliance in stuff_list[1:]])
        #     for stuff_list in [list(room.items()) for room in data]]]
        for stuff_list in [list(room.items()) for room in data]:
            rooms.append(
                Room(stuff_list[0][0], [Appliance(appliance[0], appliance[1]) for appliance in stuff_list[1:]]))
        return rooms

    def __str__(self):
        str = []
        for room in self.rooms_list:
            str.append(room.name + "\n")
            for app in room.stuff:
                str.append(app.function + " " + app.name + " " + app.state + "\n")
            str.append("\n")
        return "".join(str)


class Room:

    def __init__(self, name, stuff):
        self.name = name
        self.stuff = stuff


class Appliance:

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


class GUI(QMainWindow):

    def __init__(self, remote_controller):
        super().__init__()
        self.remote_controller = remote_controller
        self.__init_gui()
        self.show()

    def __init_gui(self):
        self.title = 'Remote Controller'
        self.width = 640
        self.height = 480
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)
        self.__center_window()
        h = QHBoxLayout()
        v1 = QVBoxLayout()
        v2 = QVBoxLayout()
        l = self.__init_QListWidget()
        l.setMinimumWidth(125)
        l.setMaximumWidth(200)
        v1.addWidget(l)
        v2.addWidget(self.__init_QListWidget())
        h.addLayout(v1)
        h.addLayout(v2)
        q = QWidget()
        q.setLayout(h)
        self.setCentralWidget(q)

    def __init_QListWidget(self):
        q_list_widget = QListWidget()
        q_list_widget.addItems([room.name for room in self.remote_controller.rooms_list])
        return q_list_widget

    def __center_window(self):
        qt_position = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_position.moveCenter(center_point)
        self.move(qt_position.topLeft())





app = QApplication(sys.argv)
ex = GUI(RemoteController("data.yml"))
sys.exit(app.exec_())


#
# gui = Tk()
#
# listbox = Listbox(gui, font=100)
#
#
#
# def func(name, x):
#     x.set("jhgfds")
#     print(name)
#
# def notify(event):
#     widget = event.widget
#     selection = widget.curselection()
#     value = widget.get(selection[0])
#     print("selection:", selection, ": '%s'" % value)
#
#
# RC = RemoteController("data.yml")
# print(str(RC))
#
#
#
# listbox.configure(selectmode=SINGLE)
# # listbox.configure(width=20)
# # listbox.configure(height=20)
# listbox.configure(font=("bitstream vera sans mono", 20))
# listbox.bind("<<ListboxSelect>>", notify)
# listbox.grid(column=0, row=0)
#
#
# label = Label(gui, text="hello")
# label.option_add("*Font", "courier 10")
# label.grid(column=1, row=0)
#
#
#

#
# print(listbox.get(0, 2))
# gui.mainloop()

