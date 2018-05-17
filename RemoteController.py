import sys
import yaml
from enum import Enum
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from PyQt5 import QtCore

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
        self.setWindowTitle(self.title)
        self.width = 640
        self.height = 480
        self.resize(self.width, self.height)

        self.central_layout = QHBoxLayout()

        self.central_widget = QWidget()
        self.search_HBox = self.__init_search_HBox()

        self.room_list = self.__init_room_list()
        self.room_list.currentItemChanged.connect(self.__update_appliances)
        self.room_list_layout = self.__init_room_list_layout()

        self.appliances_layout = self.__make_appliances_layout(0)
        self.appliances_search_layout = self.__init_appliances_search_list_layout()

        self.central_layout.addLayout(self.room_list_layout)
        self.central_layout.addLayout(self.appliances_search_layout)

        self.central_widget.setLayout(self.central_layout)


        self.setCentralWidget(self.central_widget)



    def keyPressEvent(self, event: QKeyEvent):

        if event.key() == Qt.Key_Right:
            self.search_HBox.itemAt(0).widget().setFocus()
        elif event.key() == Qt.Key_Escape:
            self.room_list.setFocus()
        elif event.key() == Qt.Key_Down and QApplication.focusWidget() == self.search_HBox.itemAt(0).widget():
            if self.room_list.currentRow() == 0:
                index = 1
                print(type(self.appliances_layout.itemAt(index).widget()))
                print(self.appliances_layout.itemAt(index).widget().text())

                while type(self.appliances_layout.itemAt(index).widget()) == QLabel or \
                        self.appliances_layout.itemAt(index).widget().isHidden() and \
                        index < self.appliances_layout.count():
                    index = index + 1
                print(QApplication.focusWidget().text())
                print(index)
                self.appliances_layout.itemAt(index).widget().setFocus()
                print(QApplication.focusWidget().text())

            else:
                self.appliances_layout.itemAt(0).widget().setFocus()




    def __init_search_HBox(self):
        self.search_widget = QWidget()

        qvb = QHBoxLayout()
        text_box = QLineEdit()
        text_box.returnPressed.connect(self.__search_appliances)
        search_button = QPushButton()
        search_button.setText("Szukaj")
        search_button.setFixedWidth(125)
        search_button.clicked.connect(self.__search_appliances)
        qvb.addWidget(text_box)
        qvb.addWidget(search_button)

        self.search_widget.setLayout(qvb)

        return qvb

    def __show_all_appliances(self):

        for i in reversed(range(self.appliances_layout.count())):
            child = self.appliances_layout.itemAt(i)
            if child.widget() is not None and type(child.widget()) == ApplianceButton:
                child.widget().show()

    def __search_appliances(self):
        pattern = self.search_HBox.itemAt(0).widget().text()
        self.__show_all_appliances()

        for i in reversed(range(self.appliances_layout.count())):
            child = self.appliances_layout.itemAt(i)
            if child.widget() is not None and type(child.widget()) == ApplianceButton:
                if pattern not in child.widget().text():
                    child.widget().hide()


    def __make_appliances_layout(self, room_number):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(QWidget())

        self.appliances_widget = QWidget()

        qfl = QVBoxLayout(self.scroll_area)
        qfl.setAlignment(Qt.AlignTop)
        for appliance in self.remote_controller.rooms_list[room_number].stuff:
            button = ApplianceButton(appliance)
            qfl.addWidget(button)
            button.setCheckable(True)
        return qfl

    def __init_appliances_search_list_layout(self):
        qvb = QVBoxLayout()
        qvb.setAlignment(Qt.AlignTop)
        qvb.addLayout(self.search_HBox)
        qvb.addLayout(self.appliances_layout)

        return qvb

    def __init_room_list_layout(self):
        qvb = QVBoxLayout()
        qvb.addWidget(self.room_list)
        return qvb

    def __init_room_list(self):
        q_list_widget = QListWidget()
        q_list_widget.addItem("Wszystko")
        q_list_widget.addItems([room.name for room in self.remote_controller.rooms_list])
        q_list_widget.setMinimumWidth(125)
        q_list_widget.setMaximumWidth(225)
        q_list_widget.setCurrentRow(1)
        return q_list_widget

    def __update_appliances(self):

        room_number = self.room_list.currentRow() - 1

        for i in reversed(range(self.appliances_layout.count())):
            child = self.appliances_layout.itemAt(i)
            if child.widget() is not None:
                self.appliances_layout.itemAt(i).widget().deleteLater()

        if room_number == -1:
            for room in self.remote_controller.rooms_list:
                room_label = QLabel(room.name)
                room_label.setAlignment(Qt.AlignHCenter)
                self.appliances_layout.addWidget(room_label)
                for appliance in room.stuff:
                    button = ApplianceButton(appliance)
                    self.appliances_layout.addWidget(button)

        else:
            for appliance in self.remote_controller.rooms_list[room_number].stuff:
                button = ApplianceButton(appliance)
                self.appliances_layout.addWidget(button)

    def __center_window(self):
        qt_position = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_position.moveCenter(center_point)
        self.move(qt_position.topLeft())


class ApplianceButton(QPushButton):

    def __init__(self, appliance):
        super().__init__()
        self.appliance = appliance
        self.setText(appliance.name + (" : OFF" if not appliance.state else " : ON"))
        self.setStyleSheet('background-color:' + ('red' if not appliance.state else 'lightGreen'))
        self.setCheckable(True)
        if self.appliance.state:
            self.setChecked(True)
        self.clicked.connect(self.__on_click)
        # self.pressed.connect(self.__on_click)

    def __on_click(self):
        if self.isChecked():
            self.setStyleSheet('background-color: lightGreen')
            self.setText(self.appliance.name + " : ON")
            self.appliance.toggle_state()
        else:
            self.setStyleSheet('background-color: red')
            self.setText(self.appliance.name + " : OFF")
            self.appliance.toggle_state()






app = QApplication(sys.argv)
ex = GUI(RemoteController("data.yml"))
sys.exit(app.exec_())

