import google_test_surya
import read_faces_loop
import RPi.GPIO as GPIO
import sys
print("Import Finished")
try:
	GPIO.cleanup()
	while(True):
		print("Checking Keypress")
		key=google_test_surya.get_keypad_entry(1)
		if key=='A':
			read_faces_loop.read_faces_loop()
		if key=='D':
			google_test_surya.lock_door(17)
		if key=='B':
			sys.exit()
except KeyboardInterrupt:
	print("Terminating...")
