import face_recognition
import cv2
import numpy as np
import time
import pickle
import os
import google_test_surya
import getpass	

def read_faces_loop():
	google_test_surya.buzzer(21,"-",0.4)
	flag=""
	num_matches=0
	num_no_matches=0
	print("Authenticating with google")
	creds=google_test_surya.authenticate_with_google()
	print("Authenticating with google")
	print("Checking for new encodings")
	check_encs=google_test_surya.check_encodings(creds)
	print ("New Encodings Found =",check_encs)
	print("Going to start camera")
	video=cv2.VideoCapture(0)
	print(video)
	print("started camera")
	enc_file=open("encodings.dat","rb")
	face_encodings=pickle.load(enc_file)
	enc_file.close()
	name_file=open("names.dat","rb")
	names=pickle.load(name_file)
	name_file.close()
	print("Files Closed")
	while flag!="MATCHED_FACULTY":
		unk, capture=video.read()
		rgb_capture = capture[:, :, ::-1]
		capture_locations=face_recognition.face_locations(rgb_capture)
		capture_encodings=face_recognition.face_encodings(rgb_capture)
		if capture_locations!=[]:
			for i in range(len(face_encodings)):
				match=match=face_recognition.compare_faces(face_encodings[i],capture_encodings,tolerance=0.5)
				if match[0]:
					detected_person = names[i].replace(".jpg","")
					print (detected_person)
					flag="MATCHED_FACULTY"
					google_test_surya.buzzer(21,"-",0.4)

		else:
			print("No one in the frame")
			google_test_surya.buzzer(21,".",0.01)

	if flag=="MATCHED_FACULTY":
		cv2.imwrite("cl_auth_request.jpg",capture)
		f=open("cl_auth_name.txt","w")
		f.write(detected_person)
		f.close()
		google_test_surya.request_authentication(creds)
		print ("Request Sent")


	flag=""
	
	chck=google_test_surya.check_authentication(creds)
	while chck==False:
        	chck=google_test_surya.check_authentication(creds)
        	print (chck)
	if chck==True:
		actual_pin=google_test_surya.get_pin()
		flag="GOT PIN"
	if flag=="GOT PIN":
		print ("Enter PIN : ")
		google_test_surya.buzzer(21,"...",0.1,0.1)
		pin_entered=google_test_surya.get_keypad_entry(4)
		print(pin_entered)
	if pin_entered==actual_pin:
	    	print ("Pin Matched. Door Opening")
	    	google_test_surya.unlock_door(17)
	else:
		print("Wrong Pin. Terminating")
		google_test_surya.buzzer(21,".....",0.2,0.1)

