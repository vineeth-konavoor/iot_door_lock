import face_recognition
import cv2
import numpy as np
import time
import pickle
import os
import getpass
import google_test_surya
def hod_side_loop():
	flag=0
	video=cv2.VideoCapture(0)
	pass1=getpass.getpass("Enter HOD Passowrd : ")
	pass2=getpass.getpass("Re-enter HOD Passowrd : ")
	if os.path.exists("hod_pass.dat"):
		if pass1==pass2:
			google_test_surya.decrypt(pass1,"hod_pass.dat")
			pass_file=open("hod_pass.dat","rb")
			password_actual=pickle.load(pass_file)
			pass_file.close()
			google_test_surya.encrypt(password_actual,"hod_pass.dat")
		else:
			print("Passwords donot match!")
			exit()
	else:
		print ("HOD Password Database missing")

	if os.path.exists("names.dat"):
		google_test_surya.decrypt(password_actual,"names.dat")
		name_file=open("names.dat","rb")
		names=pickle.load(name_file)
		name_file.close()
		google_test_surya.encrypt(password_actual,"names.dat")
	else:
		print ("Names Database missing")
	if os.path.exists("pins.dat"):
		google_test_surya.decrypt(password_actual,"pins.dat")
		pin_file=open("pins.dat","rb")
		pins=pickle.load(pin_file)
		pin_file.close()
		google_test_surya.encrypt(password_actual,"pins.dat")
	else:
		print ("PIN Database missing")
	if os.path.exists("hod_encodings.dat"):
		google_test_surya.decrypt(password_actual,"hod_encodings.dat")
		enc_file=open("hod_encodings.dat","rb")
		hod_face_encodings=pickle.load(enc_file)
		enc_file.close()
		google_test_surya.encrypt(password_actual,"hod_encodings.dat")
	else:
		print ("HOD Face Database missing")



	
	

	creds=google_test_surya.authenticate_with_google()
	prekey=google_test_surya.get_preshared_key()
	auth_req=False
	while(auth_req!=True):
		auth_req=google_test_surya.check_request(creds)
		print (auth_req)
		print("main program")
	if auth_req==True:
		print ("Request Accepted")
		num_matches=0	
		for i in range(30):
			unk, capture=video.read()
			rgb_capture = capture[:, :, ::-1]
			capture_locations=face_recognition.face_locations(rgb_capture)
			capture_encodings=face_recognition.face_encodings(rgb_capture)
			#print (capture_locations)
			print("Waiting For HOD...")
			if capture_locations!=[]:
				match=face_recognition.compare_faces(hod_face_encodings,capture_encodings,tolerance=0.5)
				if match[0]:
					num_matches=num_matches+1
					if num_matches==5:
						print ("HOD Identified")
						num_matches=0
						flag=1
						break
					else :
						print("Waiting For HOD")	


	if flag==1:
		tries=0
		if tries<3:
			req_txt=open("cl_auth_name.txt","r")
			req_name=req_txt.readline()
			req_txt.close()
			print("Requested person = ",req_name)
			password_entered=getpass.getpass("Enter Passowrd : ")
			if (password_entered==password_actual):
				print("Password Correct! \n Sending Authorization to Door...")
				grnd_file=open("cl_auth_granted.txt","w")
					
				for p in range(len(names)):
					if names[p]==req_name:
						grnd_file.write(str(pins[p]))
				grnd_file.close()
				
				google_test_surya.grand_authentication(creds)
				print("Sent auth file")
				grnd_file=open("cl_auth_granted.txt","w")
				grnd_file.write("")
			else:
				print("Incorrect Password, Try again")
				tries=tries+1
		else:
			print("Three Consecutive Incorrect Password. Terminating Request")
