from pyfirmata import Arduino 
from time import sleep 

# Connecting to the board 
board = Arduino('COM4') 

# initializing the LEDs 
led1 = board.get_pin('d:13:o') 
led2 = board.get_pin('d:12:o') 
led3 = board.get_pin('d:11:o') 
led4 = board.get_pin('d:10:o') 

# wait for 1s at every count value 
wait = 1

# initialise all to False (off) 
val_1 = val_2 = val_3 = val_4 = False

# led4 is the least significant bit and led1 is the most significant bit 
while True: # this is an infinite loop which won't end untill the terminal is killed 
	for ____ in range(2): 
		for ___ in range(2): 
			for __ in range(2): 
				for _ in range(2): 
					sleep(wait) 
					# Updating the values and printing them 
					led1.write(val_1) 
					led2.write(val_2) 
					led3.write(val_3) 
					led4.write(val_4) 
					print(int(val_1), int(val_2), int(val_3), int(val_4)) 

					val_4 = not val_4 
				val_3 = not val_3 
			val_2 = not val_2 
		val_1 = not val_1 
	print("\n\n") 
