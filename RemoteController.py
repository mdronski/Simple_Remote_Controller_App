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

        self.__init_search_box()
        self.__init_rooms()
        self.__init_appliances_with_search()
        self.__init_layouts()
        self.__center_window()
        self.__init_menu_bar()


    def keyPressEvent(self, event: QKeyEvent):

        if event.key() == Qt.Key_Right:
            self.search_HBox.itemAt(0).widget().setFocus()
        elif event.key() == Qt.Key_Escape:
            self.room_list.setFocus()
        elif event.key() == Qt.Key_Down and QApplication.focusWidget() == self.search_HBox.itemAt(0).widget():
            if self.room_list.currentRow() == 0:
                index = 1
                while type(self.appliances_layout.itemAt(index).widget()) == QLabel or \
                        self.appliances_layout.itemAt(index).widget().isHidden() and \
                        index < self.appliances_layout.count():
                    index = index + 1
                self.appliances_layout.itemAt(index).widget().setFocus()
            else:
                self.appliances_layout.itemAt(0).widget().setFocus()

    def __init_search_box(self):
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
        self.search_HBox = qvb

    def __init_layouts(self):
        self.central_layout = QHBoxLayout()
        self.central_widget = QWidget()
        self.central_layout.addLayout(self.room_list_layout)
        self.central_layout.addLayout(self.appliances_search_layout)
        self.central_widget.setLayout(self.central_layout)
        self.setCentralWidget(self.central_widget)

    def __init_appliances_with_search(self):
        self.appliances_content = QWidget()

        qvb = QVBoxLayout()
        qvb.setAlignment(Qt.AlignTop)
        for appliance in self.remote_controller.rooms_list[0].stuff:
            button = ApplianceButton(appliance)
            qvb.addWidget(button)
            button.setCheckable(True)

        self.appliances_content.setLayout(qvb)

        self.appliances_list = QScrollArea()
        self.appliances_list.setWidgetResizable(True)
        self.appliances_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.appliances_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.appliances_list.setWidget(self.appliances_content)

        self.appliances_layout = qvb

        qvb = QVBoxLayout()
        qvb.setAlignment(Qt.AlignTop)
        qvb.addWidget(self.search_widget)
        qvb.addWidget(self.appliances_list)

        self.appliances_search_layout = qvb

    def __init_rooms(self):
        room_list_widget = QListWidget()
        room_list_widget.addItem("Wszystko")
        room_list_widget.addItems([room.name for room in self.remote_controller.rooms_list])
        room_list_widget.setMinimumWidth(125)
        room_list_widget.setMaximumWidth(225)
        room_list_widget.setCurrentRow(1)

        self.room_list = room_list_widget
        self.room_list.currentItemChanged.connect(self.__update_appliances)

        qvb = QVBoxLayout()
        qvb.addWidget(self.room_list)
        self.room_list_layout = qvb

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
                    self.appliances_layout.addWidget(ApplianceButton(appliance))
        else:
            for appliance in self.remote_controller.rooms_list[room_number].stuff:
                button = ApplianceButton(appliance)
                self.appliances_layout.addWidget(button)

    def __init_menu_bar(self):
        menu = self.menuBar()
        turn_on_off_menu = menu.addMenu("Opcje")

        turn_on_all = QAction("Włącz wszystkie", self)
        turn_on_all.setShortcut("Ctrl+N")
        turn_on_all.triggered.connect(self.__turn_on_all)
        turn_on_off_menu.addAction(turn_on_all)

        turn_off_all = QAction("Wyłącz wszystkie", self)
        turn_off_all.setShortcut("Ctrl+F")
        turn_off_all.triggered.connect(self.__turn_off_all)
        turn_on_off_menu.addAction(turn_off_all)

        self.setMenuBar(menu)

    def __turn_on_all(self):
        self.__change_state_for_all(True)

    def __turn_off_all(self):
        self.__change_state_for_all(False)

    def __change_state_for_all(self, state):
        for i in reversed(range(self.appliances_layout.count())):
            child = self.appliances_layout.itemAt(i)
            if child.widget() is not None and type(child.widget()) == ApplianceButton:
                child.widget().change_state(state)

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

    def __on_click(self):
        if self.isChecked():
            self.setStyleSheet('background-color: lightGreen')
            self.setText(self.appliance.name + " : ON")
        else:
            self.setStyleSheet('background-color: red')
            self.setText(self.appliance.name + " : OFF")

        self.appliance.toggle_state()

    def change_state(self, state):
        if self.appliance.state == state:
            pass

        if state:
            self.setStyleSheet('background-color: lightGreen')
            self.setText(self.appliance.name + " : ON")
            self.setChecked(True)
            self.appliance.state = True
            self.appliance.send_to_socket()

        else:
            self.setStyleSheet('background-color: red')
            self.setText(self.appliance.name + " : OFF")
            self.setChecked(False)
            self.appliance.state = False
            self.appliance.send_to_socket()




app = QApplication(sys.argv)
ex = GUI(RemoteController("data.yml"))
sys.exit(app.exec_())

