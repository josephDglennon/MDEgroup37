
import serial
import time

arduinoData = serial.Serial('com4', 9600)
time.sleep(1)
while True:
    while (arduinoData.inWaiting() == 0):
        pass
    dataPacket = arduinoData.readline()
    dataPacket= str(dataPacket, 'utf-8')
    print(dataPacket)

    