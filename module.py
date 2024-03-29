from PyQt6.QtWidgets import *
from PyQt6.QtCore    import *
from PyQt6.QtGui     import *
import relays as rel
import sys
import serial
import time


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.init_values()
        self.create_left_panel()
        self.create_main_widget()
        self.initUI()
        self.timer = QTimer(self)
        QCoreApplication.processEvents()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.connect_port)

        self.state = rel.MASK_R

        self.event_button()
    
    def relay_a1(self):
        if self.board_a['A1'].isChecked():
            self.state = self.state & rel.RELAY_A01
        else:
            self.state = self.state | (~rel.RELAY_A01 & 0xFFFF)

    def relay_a2(self):
        if self.board_a['A2'].isChecked():
            self.state = self.state & rel.RELAY_A02
        else:
            self.state = self.state | (~rel.RELAY_A02 & 0xFFFF)

    def relay_a3(self):
        if self.board_a['A3'].isChecked():
            self.state = self.state & rel.RELAY_A03
        else:
            self.state = self.state | (~rel.RELAY_A03 & 0xFFFF)

    def relay_a4(self):
        if self.board_a['A4'].isChecked():
            self.state = self.state & rel.RELAY_A04
        else:
            self.state = self.state | (~rel.RELAY_A04 & 0xFFFF)

    def relay_a5(self):
        if self.board_a['A5'].isChecked():
            self.state = self.state & rel.RELAY_A05
        else:
            self.state = self.state | (~rel.RELAY_A05 & 0xFFFF)

    def relay_a6(self):
        if self.board_a['A6'].isChecked():
            self.state = self.state & rel.RELAY_A06
        else:
            self.state = self.state | (~rel.RELAY_A06 & 0xFFFF)

    def relay_a7(self):
        if self.board_a['A7'].isChecked():
            self.state = self.state & rel.RELAY_A07
        else:
            self.state = self.state | (~rel.RELAY_A07 & 0xFFFF)

    def relay_a8(self):
        if self.board_a['A8'].isChecked():
            self.state = self.state & rel.RELAY_A08
        else:
            self.state = self.state | (~rel.RELAY_A08 & 0xFFFF)

    def test_relays(self):
        formatted_state = "{:04X}".format(self.state)
        module_address = "{:02X}".format(self.address_spinBox.value()).upper()
        com_port = self.port_lineEdit.text() or 'COM4'
        command = self.set_pins_states(module_address, formatted_state)
        print(command)
        with serial.Serial(com_port, 115200, timeout=1) as ser:
            if ser.is_open:
                ser.write(command.encode())
                time.sleep(0.1)
                response = ser.read_all().decode()

    def set_pins_states(self, module_id, data):
        command_string = f"+{module_id}{data}"
        checksum = self.calculate_checksum_correct(command_string)
        final_command = f"{command_string}{checksum}\r"
        print(final_command)
        return final_command.upper()  

    def calculate_checksum_correct(self, command):
        checksum = sum(ord(c) for c in command) & 0xFF  # Применяем маску 0xFF
        return f"{checksum:02X}"

    def display_input(self, data):
        hex_string = data[1:]
        binary_data = ''.join(format(int(c, 16), '04b') for c in hex_string)

        activeInput = "red"
        inactiveInput = "green"
        
        if self.down_board.currentText() == 'input':
            for i, pos in enumerate(['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8'], start=16):
                color = activeInput if binary_data[23 - (i - 16)] == "0" else inactiveInput
                self.board_a[pos].setStyleSheet(f'color: "black"; background-color: {color}')

            for i in range(8):
                index = 15 - i 
                pos = f'F{i + 1}'
                color = activeInput if binary_data[index] == "0" else inactiveInput
                self.board_f[pos].setStyleSheet(f'color: "black"; background-color: {color}')

        if self.upper_board.currentText() == 'input':
            for i in range(5):
                index = 39 - i 
                pos = f'C{i + 1}'
                color = activeInput if binary_data[index] == "0" else inactiveInput
                self.board_c[pos].setStyleSheet(f'color: "black"; background-color: {color}')

            indexes_d = [0, 1, 30, 31, 5, 4, 3, 2]  
            for i, pos in enumerate(['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8']):
                color = activeInput if binary_data[indexes_d[i]] == "0" else inactiveInput
                self.board_d[pos].setStyleSheet(f'color: "black"; background-color: {color}')

        for i, pos in enumerate(['IB8', 'IB7', 'IB6'], start=31):
            color = activeInput if binary_data[i+1] == "0" else inactiveInput
            self.board_b[pos].setStyleSheet(f'color: "black"; background-color: {color}')

        indexes_e = [29, 28, 27, 26, 25, 24, 7, 6] 
        for i, pos in enumerate(['IE1', 'IE2', 'IE3', 'IE4', 'IE5', 'IE6', 'IE7', 'IE8']):
            color = activeInput if binary_data[indexes_e[i]] == "0" else inactiveInput
            self.board_e[pos].setStyleSheet(f'color: "black"; background-color: {color}')


    def create_request(self, character, module_address, command):
        if module_address is None:
            raise ValueError("Module address cannn be None")
        request_string = f"{character}{module_address}{command}"
        sum_ascii = sum(ord(char) for char in request_string)
        checksum_hex = hex(sum_ascii)[-2:].upper()
        return request_string + checksum_hex + '\r'

    def find_address(self):
        SLEEP_DURATION = 0.2
        for i in range(self.MAX_ADDRESSES):
            self.address_spinBox.setValue(i)
            QCoreApplication.processEvents()
            if self.connect_port():
                exit()
            time.sleep(SLEEP_DURATION)

    def init_values(self):
        self.MAX_ADDRESSES = 256

        self.upper_board_lb = QLabel('Верхняя плата:')
        self.down_board_lb  = QLabel('Нижняя плата:')
        self.port_lb        = QLabel('Порт:')
        self.address_lb     = QLabel('Адрес модуля:')
        self.connect_btn    = QPushButton('Соединить!')
        self.find_btn       = QPushButton('Автопоиск')
        self.test_btn       = QPushButton('Тестирование')
        self.upper_board    = QComboBox()
        self.down_board     = QComboBox()

        self.upper_board.addItems(['', 'input', 'output'])
        self.down_board.addItems (['', 'input', 'output'])
        self.connect_btn.setCheckable(True)

        self.test_btn.setEnabled(False)

        # Процессорная плата 
        self.board_b  = {'U': '', 'Gm': '',  'D+': '',  'D-': '',  'Gd': '',  'Prg': '', 'IB6': '' ,'IB7': '', 'IB8': '', '+U': ''}
        self.board_e  = {'U': '', 'IE1': '', 'IE2': '', 'IE3': '', 'IE4': '', 'IE5': '', 'IE6': '', 'IE7': '', 'IE8': '', '+U': ''}

        # Нижняя плата модуля
        self.board_a = {'U': '', 'A1': '', 'A2': '', 'A3': '', 'A4': '', 'A5': '', 'A6': '','A7': '', 'A8': '', '+U': ''}
        self.board_f = {'U': '', 'F1': '', 'F2': '', 'F3': '', 'F4': '', 'F5': '', 'F6': '','F7': '', 'F8': '', '+U': ''}

        # Верхняя плата модуля
        self.board_c = {'U': '', 'C1': '', 'C2': '', 'C3': '', 'C4': '', 'C5': '', 'C6': '','C7': '', 'C8': '', '+U': ''}
        self.board_d = {'U': '', 'D1': '', 'D2': '', 'D3': '', 'D4': '', 'D5': '', 'D6': '','D7': '', 'D8': '', '+U': ''}
 
        self.init_board(self.board_b)
        self.init_board(self.board_e)

        self.init_board(self.board_a, board_is_connected=False)
        self.init_board(self.board_f, board_is_connected=False)
        self.init_board(self.board_c, board_is_connected=False)
        self.init_board(self.board_d, board_is_connected=False)

        self.upper_board.currentTextChanged.connect(self.board_changed)
        self.upper_board.setObjectName("upper_board")
        self.down_board.currentTextChanged.connect(self.board_changed)
        self.down_board.setObjectName("down_board")

        self.port_lineEdit   = QLineEdit('')
        self.address_spinBox = QSpinBox()
        self.address_spinBox.setMaximum(self.MAX_ADDRESSES)


    def connect_port(self):
        if self.connect_btn.isChecked() :
            self.connect_btn.setText('Соединить!')
            self.test_btn.setEnabled(False)
            return
        else:
            self.connect_btn.setText('Отключить!')
            self.test_btn.setEnabled(True)

        com_port = self.port_lineEdit.text() or 'COM4'
        module_address = "{:02X}".format(self.address_spinBox.value()).upper()


        baud_rate = 115200

        try:
            with serial.Serial(com_port, baud_rate, timeout=1) as ser:
                if ser.is_open:
                    self.handle_serial_connection(ser, module_address)
        except Exception as e:
            self.test_btn.setEnabled(False)
            QMessageBox.information(self, 'Warning', f'Ошибка при открытии COM порта: {e}')
            self.connect_btn.setChecked(False)
    
    def handle_serial_connection(self, ser, module_address):
        self.command = self.create_request('-', module_address, '')
        ser.write(self.command.encode())
        time.sleep(0.1)

        response = ser.read_all().decode()
        if not response:
            self.test_btn.setEnabled(False)
            return
        else:
            #print("response", response)
            ...
        
        data, checksum = response[:-3], response[-3:-1]
        if self.checksum_verification(data, checksum) == 0:
            self.display_input(data)
            self.timer.start()
        else:
            self.timer.stop()
            QMessageBox.information(self, 'Checksum', 'Ошибка контрольной суммы модуля')
    
    def checksum_verification(self, data, checksum):
        total = sum(ord(char) for char in data)
        hex_number = hex(total)[2:]
        correct_checksum = hex_number[-2:].upper()
        return 0 if correct_checksum == checksum else -1

    def board_changed(self, text):
        tmp = self.sender()
        if tmp.objectName() == 'upper_board':
            boards = [self.board_c, self.board_d]
        elif tmp.objectName() == 'down_board':
            boards = [self.board_a, self.board_f]

        for board in boards:
            for element in board.keys():
                button_text = board[element].text()  # Используем другое имя переменной для текста кнопки
                # Удаляем первый символ если он 'R' или 'I', предотвращаем добавление повторяющегося префикса
                if button_text.startswith('R') or button_text.startswith('I'):
                    button_text = button_text[1:]  # Удаляем первый символ

                # Обновляем текст, добавляя нужный префикс
                if text == 'input' and button_text  != 'U' and button_text != '+U':
                    board[element].setEnabled(False)
                    board[element].setText('I' + button_text)
                    board[element].setStyleSheet('background-color: green; color: black')
                elif text == 'output' and button_text != 'U' and button_text != '+U':
                    board[element].setEnabled(True)
                    board[element].setText('R' + button_text)
                    board[element].setStyleSheet('background-color: #6666FF; color: black')
                else:
                    board[element].hide()  # Скрываем кнопку, если значение не 'input' или 'output'

                if text in ['input', 'output']:
                    board[element].show()  # Показываем кнопку только если значение 'input' или 'output'
    
    def init_board(self, board, board_is_connected=True):
        for element in board.keys():
            board[element] = QPushButton(element)
            board[element].setEnabled(False)
            board[element].setCheckable(True)
            board[element].setStyleSheet('color: black; background-color: white')

            text = board[element].text()
            ch = text[:1]
            if ch == 'I':
                board[element].setStyleSheet('color: black; background-color: green')
            elif ch == 'U' or ch == '+':
                board[element].setStyleSheet('color: black; background-color: yellow')
            else:
                board[element].setStyleSheet('color: black; background-color: gray')

            if board_is_connected == False:
                board[element].hide()

    def initUI(self):
        self.monitor = QHBoxLayout()
        self.monitor.addLayout(self.left_layout)
        self.monitor.addLayout(self.main_layout)
        self.setLayout(self.monitor)

    def create_left_panel(self):
        self.left_layout = QVBoxLayout()
        widgets = [
            self.upper_board_lb, self.upper_board, 
            self.down_board_lb, self.down_board, 
            self.port_lb, self.port_lineEdit, 
            self.connect_btn,
            self.address_lb, self.address_spinBox, 
            self.find_btn, self.test_btn
        ]
        for widget in widgets:
            self.left_layout.addWidget(widget)

    def create_main_widget(self):
        self.main_layout = QVBoxLayout()
        # Список плат для итерации
        self.boards = [self.board_a, self.board_b, self.board_c, self.board_d, self.board_e, self.board_f]
        for board in self.boards:
            row = QHBoxLayout()
            for key in board.keys():
                row.addWidget(board[key])
            self.main_layout.addLayout(row)
    
    def event_button(self):
        self.connect_btn.clicked.connect(self.connect_port)
        self.find_btn.clicked.connect(self.find_address)
        self.test_btn.clicked.connect(self.test_relays)
        self.board_a['A1'].clicked.connect(self.relay_a1)
        self.board_a['A2'].clicked.connect(self.relay_a2)
        self.board_a['A3'].clicked.connect(self.relay_a3)
        self.board_a['A4'].clicked.connect(self.relay_a4)
        self.board_a['A5'].clicked.connect(self.relay_a5)
        self.board_a['A6'].clicked.connect(self.relay_a6)
        self.board_a['A7'].clicked.connect(self.relay_a7)
        self.board_a['A8'].clicked.connect(self.relay_a8)


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())