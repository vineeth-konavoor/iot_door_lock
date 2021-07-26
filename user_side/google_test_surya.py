from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
import io
import os
import pickle
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random


def get_preshared_key():
	prekey="def_123"
	return prekey


def authenticate_with_google():
	SCOPES = ['https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive.metadata.readonly','https://www.googleapis.com/auth/drive.appdata']



	creds = None
    	
	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)
    	
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
        	
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)
	return creds


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
		f.close()



def check_request(creds):	
	service = build('drive', 'v3', credentials=creds)
	k=0
	response = service.files().list(spaces='appDataFolder',fields='nextPageToken, files(id, name)',pageSize=10).execute()
	fil_list = response.get('files', [])
	
	if len(fil_list)!=0:
		print (fil_list)
		print (len(fil_list))
		k=0
		for fil in fil_list:
			print (fil.get('name'))
			if fil.get('name')=="cl_auth_request.jpg":
				print ("Found request file jpg")				
				download_file(fil.get('id'),"cl_auth_request.jpg",creds)
				jpg_id=fil.get('id')
				k=k+1
			if fil.get('name')=="cl_auth_name.txt":
				print ("Found request file txt")
				download_file(fil.get('id'),"cl_auth_name.txt",creds)
				txt_id=fil.get('id')
				k=k+1
			else:
				print("Checking for Requests")
				
		
	else:
		print("No Files")
	if k==2:
		
		request = service.files().delete(fileId=jpg_id).execute()
		request = service.files().delete(fileId=txt_id).execute()
		print ("Deleted request files")
		prekey=get_preshared_key()
		decrypt(prekey,"cl_auth_request.jpg")
		decrypt(prekey,"cl_auth_name.txt")
		return True
	else:
		return False	
def flush_all(creds):
	service = build('drive', 'v3', credentials=creds)
	k=0
	response = service.files().list(spaces='appDataFolder',fields='nextPageToken, files(id, name)',pageSize=10).execute()
	fil_list = response.get('files', [])
	
	if len(fil_list)!=0:
		print (fil_list)
		print (len(fil_list))
		
		for fil in fil_list:
			print ("Deleting",fil.get('name'))
			file_id=fil.get('id')
			request = service.files().delete(fileId=file_id).execute()
			print("Deleted")
	else:
		print("Nothing To Flush")
def request_authentication(creds):
	service = build('drive', 'v3', credentials=creds)

	

	metadata={'name':"cl_auth_request.jpg",'parents':['appDataFolder']}


	res=service.files().create(body=metadata,media_body="cl_auth_request.jpg",fields='id').execute()


def grand_authentication(creds):
	service = build('drive', 'v3', credentials=creds)

	prekey=get_preshared_key()
	encrypt(prekey,"cl_auth_granted.txt")
	
	metadata={'name':"cl_auth_granted.txt",'parents':['appDataFolder']}


	res=service.files().create(body=metadata,media_body="cl_auth_granted.txt",fields='id').execute()
	print (res)

	
def upload_file(file_name,creds):
	service = build('drive', 'v3', credentials=creds)	
	metadata={'name':file_name,'parents':['appDataFolder']}


	res=service.files().create(body=metadata,media_body=file_name,fields='id').execute()
	print (res)

def update_encodings_on_door(creds):
	prekey=get_preshared_key()
	encrypt(prekey,"encodings.dat")
	encrypt(prekey,"names.dat")
	os.rename("encodings.dat","encodings.txt")
	os.rename("names.dat","names.txt")
	
	upload_file("encodings.txt",creds)
	upload_file("names.txt",creds)
	os.rename("encodings.txt","encodings.dat")
	os.rename("names.txt","names.dat")
	decrypt(prekey,"encodings.dat")
	decrypt(prekey,"names.dat")
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

#user side main………………

		import hod_side_loop

try:
	while(True):
		hod_side_loop.hod_side_loop()
except KeyboardInterrupt:
	print("Terminating")
