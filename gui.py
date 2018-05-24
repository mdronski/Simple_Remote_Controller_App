import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from RemoteController import RemoteController


class GUI(QMainWindow):

    def __init__(self, remote_controller):
        """ Initialize gui and show it"""

        super().__init__()
        self.remote_controller = remote_controller
        self.__init_gui()
        self.show()

    def __init_gui(self):
        """Set various gui parameters"""

        self.title = 'Remote Controller'
        self.setWindowTitle(self.title)
        self.width = 640
        self.height = 480
        self.resize(self.width, self.height)

        """Initialize widgets and layouts"""

        self.__init_search_box()
        self.__init_rooms()
        self.__init_appliances_with_search()
        self.__init_layouts()
        self.__center_window()
        self.__init_menu_bar()

    def keyPressEvent(self, event: QKeyEvent):
        """Catching keys pressed to move focus around gui components"""

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
        """Initialise search widget with text box and button"""

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
        """Merge initialized layouts and set them as gui's central widget layout"""

        self.central_layout = QHBoxLayout()
        self.central_widget = QWidget()
        self.central_layout.addLayout(self.room_list_layout)
        self.central_layout.addLayout(self.appliances_search_layout)
        self.central_widget.setLayout(self.central_layout)
        self.setCentralWidget(self.central_widget)

    def __init_appliances_with_search(self):
        """Create appliances button list and merge it with search widget"""
        self.appliances_content = QWidget()

        """Initialise appliances list layout and add remoteController first room appliances"""
        qvb = QVBoxLayout()
        qvb.setAlignment(Qt.AlignTop)
        for appliance in self.remote_controller.rooms_list[0].stuff:
            button = ApplianceButton(appliance)
            qvb.addWidget(button)
            button.setCheckable(True)

        self.appliances_content.setLayout(qvb)

        """Create scroll area for appliances list"""
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
        """Initialise room list widget"""

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
        """Show all hidden appliances"""

        for i in reversed(range(self.appliances_layout.count())):
            child = self.appliances_layout.itemAt(i)
            if child.widget() is not None and type(child.widget()) == ApplianceButton:
                child.widget().show()

    def __search_appliances(self):
        """Search appliances containing string given by user in search box"""

        pattern = self.search_HBox.itemAt(0).widget().text()
        self.__show_all_appliances()

        for i in reversed(range(self.appliances_layout.count())):
            child = self.appliances_layout.itemAt(i)
            if child.widget() is not None and type(child.widget()) == ApplianceButton:
                if pattern.lower() not in child.widget().text().lower():
                    child.widget().hide()

    def __update_appliances(self):
        """Change appliances list on room change"""

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
        """Initialise menu bar with turn on and turn off all appliances functions"""

        menu = self.menuBar()
        turn_on_off_menu = menu.addMenu("Opcje")

        turn_on_all = QAction("Włącz wszystkie", self)
        turn_on_all.setShortcut("Ctrl+N")
        turn_on_all.triggered.connect(self.__turn_on_all)
        turn_on_off_menu.addAction(turn_on_all)

        turn_off_all = QAction("Wyłącz wszystkie",  self)
        turn_off_all.setShortcut("Ctrl+F")
        turn_off_all.triggered.connect(self.__turn_off_all)
        turn_on_off_menu.addAction(turn_off_all)

        self.setMenuBar(menu)

    def __turn_on_all(self):
        self.__change_state_for_all(True)

    def __turn_off_all(self):
        self.__change_state_for_all(False)

    def __change_state_for_all(self, state):
        """Change state for all not hidden appliances"""

        for i in reversed(range(self.appliances_layout.count())):
            child = self.appliances_layout.itemAt(i)
            if child.widget() is not None and type(child.widget()) == ApplianceButton and not child.widget().isHidden():
                child.widget().change_state(state)

    def __center_window(self):
        """Move gui's window to the center of display"""

        qt_position = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_position.moveCenter(center_point)
        self.move(qt_position.topLeft())


class ApplianceButton(QPushButton):
    """Specialised button class for appliances"""

    def __init__(self, appliance):
        """Initialise buttons attributes"""

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
            return

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

