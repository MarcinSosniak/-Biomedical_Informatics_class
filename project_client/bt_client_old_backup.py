import serial
import time
import numpy as np
import  matplotlib.pyplot as plt

ser=serial.Serial()
ser.baudrate = 115200
ser.port = 'COM3'
ser.open()
tmp_line = []
points = []
time_stamps =[]
new_point = 0.0
new_time_stamp = time.time()
new_data = False



while True:
    char = ser.read(1)

    if(char == b'\n'):
        line = b''.join(tmp_line).decode("ASCII")
        # print(line)
        tmp_line = []
        s_line = line.split()
        current_time = time.time()
        current_val = float(s_line[1])
        print(current_val)
        points.append(current_val)
        time_stamps.append(current_time)


    else:
        tmp_line.append(char)

