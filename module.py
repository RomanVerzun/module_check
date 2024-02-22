from PyQt6.QtWidgets import *
from PyQt6.QtCore    import *
from PyQt6.QtGui     import *
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

        self.connect_btn.clicked.connect(self.connect_port)
        self.find_btn.clicked.connect(self.find_address)

    def create_request(self, character, module_address, command):
        if module_address is not None:
            request_string = f"{character}{module_address}{command}"
        else:
            exit()
        sum_ascii = sum(ord(char) for char in request_string)
        checksum_hex = hex(sum_ascii)[-2:].upper()
        return request_string + checksum_hex + '\r'

    def find_address(self):
        for i in range(256):
            if self.connect_port(True):
                break
            else:
                self.address_spinBox.setValue(i)
                QCoreApplication.processEvents()
                time.sleep(0.1)

    def init_values(self):
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

        # Процессорная плата 
        self.board_b  = {'U': '', 'Gm': '', 'D+': '', 'D-': '', 'Gd': '', 'Prg': '', 'IB6': '' ,'IB7': '', 'IB8': '', '+U': ''}
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
        self.address_spinBox.setMaximum(255)

    def connect_port(self, state):
        if state:
            self.connect_btn.setText('Отключить!')
        else:
            self.connect_btn.setText('Соединить!')
            #return

        com_port = self.port_lineEdit.text()
        module_address = hex(self.address_spinBox.value())[-2:].upper()
        print(com_port)
        baud_rate = 115200

        try:
            ser = serial.Serial(com_port, baud_rate, timeout=1)
        except Exception as e:
            print(f"Ошибка при открытии порта: {e}")
        
        if ser.is_open:
            try:
                command = self.create_request('-', module_address, '')

                ser.write(command.encode())
                time.sleep(0.1)

                response = ser.read_all().decode()
                print(f"Ответ от устройства: {response}")
                if response:
                    return response
            except Exception as e:
                print(e)
            finally:
                ser.close()
        else:
            print("Не удалось открыть COM порт")

    

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
                    board[element].setStyleSheet('background-color: #66ffff; color: black')
                elif text == 'output' and button_text != 'U' and button_text != '+U':
                    board[element].setEnabled(True)
                    board[element].setText('R' + button_text)
                    board[element].setStyleSheet('background-color: #66ff66; color: black')
                else:
                    board[element].hide()  # Скрываем кнопку, если значение не 'input' или 'output'

                if text in ['input', 'output']:
                    board[element].show()  # Показываем кнопку только если значение 'input' или 'output'
    
    def init_board(self, board, board_is_connected=True):
        for element in board.keys():
            board[element] = QPushButton(element)
            board[element].setEnabled(False)
            board[element].setStyleSheet('color: black; background-color: white')

            text = board[element].text()
            ch = text[:1]
            if ch == 'I':
                board[element].setStyleSheet('color: black; background-color: #66ffff')
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


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())