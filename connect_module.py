import serial
import time

com_port = 'COM4'  
baud_rate = 115200

def create_request(character, module_address ,command):
    """
    Формирует запрос, включая расчет контрольной суммы и добавление CR.
    :return: Сформированная строка запроса.
    """
    # Добавление адреса модуля к команде, если он предоставлен
    if module_address is not None:
        request_string = f"{character}{module_address}{command}"
    else:
        exit()
    
    sum_ascii = sum(ord(char) for char in request_string)
    # Контрольная сумма в шестнадцатеричном формате, ограниченная двумя последними символами
    checksum_hex = hex(sum_ascii)[-2:].upper()
    # Формирование итоговой строки запроса с добавлением контрольной суммы и CR
    final_request = request_string + checksum_hex + "\r"
    print(final_request)
    return final_request


try:
    ser = serial.Serial(com_port, baud_rate, timeout=1)
except Exception as e:
    print(f"Ошибка при открытии порта: {e}")

if ser.is_open:
    try:
        while True:
            command = create_request('-', '2B', '')

            ser.write(command.encode()) 
            time.sleep(0.5)

            response = ser.read_all().decode()
            print(f"Ответ от устройства: {response}")

    except Exception as e:
        print(f"Ошибка при отправке команды: {e}")
    finally:
        ser.close()
else:
    print("Не удалось открыть COM порт.")

