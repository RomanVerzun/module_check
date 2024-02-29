import serial
import time


MASK_R  = 0b1111111111111111
RELAY01 = 0b1111111111111110
RELAY02 = 0b1111111111111101
RELAY03 = 0b1111111111111011
RELAY04 = 0b1111111111110111
RELAY05 = 0b1111111111101111
RELAY06 = 0b1111111111011111
RELAY07 = 0b1111111110111111
RELAY08 = 0b1111111101111111
RELAY09 = 0b1111111011111111
RELAY10 = 0b1111110111111111
RELAY11 = 0b1111101111111111
RELAY12 = 0b1111011111111111
RELAY13 = 0b1110111111111111
RELAY14 = 0b1101111111111111
RELAY15 = 0b1011111111111111
RELAY16 = 0b0111111111111111



def calculate_checksum_correct(command):
    checksum = sum(ord(c) for c in command) & 0xFF  # Применяем маску 0xFF
    return f"{checksum:02X}"

def set_relays_states(module_id, data):
    command_string = f"+{module_id}{data}"
    checksum = calculate_checksum_correct(command_string)
    final_command = f"{command_string}{checksum}\r"
    return final_command.upper()  


state = MASK_R & RELAY16
formatted_state = "{:04X}".format(state)

command = set_relays_states("08", formatted_state)
print(command)

with serial.Serial('COM4', 115200, timeout=1) as ser:
    if ser.is_open:
        ser.write(command.encode())
        time.sleep(0.1)
        response = ser.read_all().decode()
        print(response)