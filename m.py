import serial
import time

def calculate_checksum_correct(command):
    checksum = sum(ord(c) for c in command) & 0xFF  # Применяем маску 0xFF
    return f"{checksum:02X}"

def create_dcon_command_correct(module_id, data):
    command_string = f"+{module_id}{data}"
    checksum = calculate_checksum_correct(command_string)
    final_command = f"{command_string}{checksum}\r"
    return final_command.upper()  # Преобразуем результат к верхнему регистру согласно примечанию

example_command_correct = create_dcon_command_correct("08", "0000")



print(example_command_correct)
with serial.Serial('COM4', 115200, timeout=1) as ser:
    if ser.is_open:
        command = example_command_correct
        ser.write(command.encode())
        time.sleep(0.1)
        response = ser.read_all().decode()
        print(response)
