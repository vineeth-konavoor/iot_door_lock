from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
import io
import os
import pickle
import RPi.GPIO as GPIO
import time
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

def get_preshared_key():
	prekey="def_123"
	return prekey

def authenticate_with_google():
	# If modifying these scopes, delete the file token.pickle.
	SCOPES = ['https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive.metadata.readonly','https://www.googleapis.com/auth/drive.appdata']



	creds = None
    	# The file token.pickle stores the user's access and refresh tokens, and is
    	# created automatically when the authorization flow completes for the first
    	# time.
	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)
    	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
        	# Save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)
	return creds


def check_request(creds):	
	service = build('drive', 'v3', credentials=creds)

	response = service.files().list(spaces='appDataFolder',fields='nextPageToken, files(id, name)',pageSize=10).execute()
	fil_list,unk = response.get('files', [])

	for file in files:
		if file.get('name')=="cl_auth_request":
			download_file(file.get('id'),"cl_auth_request.req",creds)
			request = service.files().delete(fileId=file_id).execute()
			print ("Deleted request file")
			return True
		else:
			return False


def download_file(id,save_name,creds):	
	service = build('drive', 'v3', credentials=creds)
	file_id=id
	request = service.files().get_media(fileId=file_id)
	fh = io.BytesIO()
	downloader = MediaIoBaseDownload(fh, request)
	done = False
	while done is False:
		status, done = downloader.next_chunk()
	with io.open(save_name,'wb') as f:
		fh.seek(0)
		f.write(fh.read())

def request_authentication(creds):
	service = build('drive', 'v3', credentials=creds)

	
	prekey=get_preshared_key()
	encrypt(prekey,"cl_auth_request.jpg")
	encrypt(prekey,"cl_auth_name.txt")
	metadata={'name':"cl_auth_request.jpg",'parents':['appDataFolder']}
	res1=service.files().create(body=metadata,media_body="cl_auth_request.jpg",fields='id').execute()	


	metadata={'name':"cl_auth_name.txt",'parents':['appDataFolder']}
	res2=service.files().create(body=metadata,media_body="cl_auth_name.txt",fields='id').execute()	


	print ("status of requests=",res1,res2)



def check_authentication(creds):	
	service = build('drive', 'v3', credentials=creds)
	grnd=0
	response = service.files().list(spaces='appDataFolder',fields='nextPageToken, files(id, name)',pageSize=10).execute()
	fil_list = response.get('files', [])
	print (fil_list)
	for file in fil_list:
		print (file.get('name'))
		if file.get('name')=="cl_auth_granted.txt":
			download_file(file.get('id'),"cl_auth_granted.txt",creds)
			file_id=file.get('id')
			print ("Downloaded authentication file")
			grnd=1
		else:
			print("Checking for authentication.")

	if grnd==1:
		request = service.files().delete(fileId=file_id).execute()
		prekey=get_preshared_key()
		decrypt(prekey,"cl_auth_granted.txt")
		print("Deleted Authentication")
		return True
	if grnd==0:
		print("No Authentication")
		return False
def get_pin():
	f=open("cl_auth_granted.txt","r")		
	pin=f.readline()
	if pin!="non":
		f.close()
		f=open("cl_auth_granted.txt","w")
		f.write("non")
		return pin
	else:
		print("No Auth File")


def unlock_door(pin):
    servo_pin = pin
    duty_cycle = 10     # Should be the centre for a SG90

# Configure the Pi to use pin names (i.e. BCM) and allocate I/O
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servo_pin, GPIO.OUT)
    GPIO.setwarnings(False)
# Create PWM channel on the servo pin with a frequency of 50Hz
    pwm_servo = GPIO.PWM(servo_pin, 50)
    pwm_servo.start(duty_cycle)
    pwm_servo.ChangeDutyCycle(duty_cycle)
    buzzer(21,"---",0.15,0.15)
    time.sleep(2)




def lock_door(pin):
    servo_pin = pin
    duty_cycle = 5     # Should be the centre for a SG90

# Configure the Pi to use pin names (i.e. BCM) and allocate I/O
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servo_pin, GPIO.OUT)
    GPIO.setwarnings(False)
# Create PWM channel on the servo pin with a frequency of 50Hz
    pwm_servo = GPIO.PWM(servo_pin, 50)
    pwm_servo.start(duty_cycle)
    pwm_servo.ChangeDutyCycle(duty_cycle)
    buzzer(21,"-",0.25)
    time.sleep(2)
    

def get_keypad_entry(digits):
	
	GPIO.setmode(GPIO.BCM)

	keypad=[['1','2','3','A'],['4','5','6','B'],['7','8','9','C'],['*','0','#','D']]
	col=[5,4,3,2]
	row=[9,8,7,6]
	entry=""
	for i in range(4):
		GPIO.setup(col[i],GPIO.OUT)
		GPIO.output(col[i],1)
	for i in range(4):
		GPIO.setup(row[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)

	try:
		while(len(entry)<digits):
			for j in range(4):
				GPIO.output(col[j],0)
				for i in range(4):
					if GPIO.input(row[i])==0:
						entry=entry+keypad[i][j]
						time.sleep(0.2)
						buzzer(21,'.',0.03)
						while GPIO.input(row[i])==0:
							pass
				GPIO.output(col[j],1)
	finally:
		GPIO.cleanup()
		return entry

def check_encodings(creds):
	service = build('drive', 'v3', credentials=creds)
	grnd=0
	response = service.files().list(spaces='appDataFolder',fields='nextPageToken, files(id, name)',pageSize=10).execute()
	fil_list = response.get('files', [])
	print (fil_list)
	for file in fil_list:
		print (file.get('name'))
		if file.get('name')=="encodings.txt":
			download_file(file.get('id'),"encodings.dat",creds)
			file_id_encs=file.get('id')
			print ("Downloaded encodings file")
			grnd=grnd+1
			print (grnd)
		if file.get('name')=="names.txt":
			download_file(file.get('id'),"names.dat",creds)
			file_id_names=file.get('id')
			print ("Downloaded names file")
			grnd=grnd+1
			print (grnd)
		else:
			print("Checking for encodings and names")
		print (grnd)
	if grnd==2:
		request = service.files().delete(fileId=file_id_encs).execute()
		request = service.files().delete(fileId=file_id_names).execute()
		
		print("Deleted encodings and names from cloud")
		prekey=get_preshared_key()
		decrypt(prekey,"encodings.dat")
		decrypt(prekey,"names.dat")
		print("Decrypted files")
		return True
	if grnd==1:
		request = service.files().delete(fileId=file_id_encs).execute()
		print("Deleted encodings from cloud")
		return None
	if grnd==0:
		print("No new encodings found")
		return False

def buzzer(buzz,code,dit,delay=0.2):
	dash=2*dit
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(buzz,GPIO.OUT)
	for i in range(len(code)):
		if code[i]=='.':
			GPIO.output(buzz,GPIO.HIGH)
			time.sleep(dit)
			GPIO.output(buzz,GPIO.LOW)
			time.sleep(delay)
		if code[i]=='-':
			GPIO.output(buzz,GPIO.HIGH)
			time.sleep(dash)
			GPIO.output(buzz,GPIO.LOW)
			time.sleep(delay)
	GPIO.output(buzz,GPIO.LOW)

def encrypt(password, filename):
	key=getKey(password)
	chunksize = 64*1024
	outputFile="tmp_"+filename
	filesize = str(os.path.getsize(filename)).zfill(16)
	IV = Random.new().read(16)

	encryptor = AES.new(key, AES.MODE_CBC, IV)

	with open(filename, 'rb') as infile:
		with open(outputFile, 'wb') as outfile:
			outfile.write(filesize.encode('utf-8'))
			outfile.write(IV)
			
			while True:
				chunk = infile.read(chunksize)
				
				if len(chunk) == 0:
					break
				elif len(chunk) % 16 != 0:
					chunk += b' ' * (16 - (len(chunk) % 16))

				outfile.write(encryptor.encrypt(chunk))
	outfile.close()
	infile.close()
	os.remove(filename)
	os.rename(outputFile,filename)


def decrypt(password, filename):
	key=getKey(password)
	chunksize = 64*1024
	outputFile="tmp_"+filename
	
	with open(filename, 'rb') as infile:
		filesize = int(infile.read(16))
		IV = infile.read(16)

		decryptor = AES.new(key, AES.MODE_CBC, IV)

		with open(outputFile, 'wb') as outfile:
			while True:
				chunk = infile.read(chunksize)

				if len(chunk) == 0:
					break

				outfile.write(decryptor.decrypt(chunk))
			outfile.truncate(filesize)
	outfile.close()
	infile.close()
	os.remove(filename)
	os.rename(outputFile,filename)

def getKey(password):
	hasher = SHA256.new(password.encode('utf-8'))
	return hasher.digest()
