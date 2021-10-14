from flask import Flask, request
import logging
import os
import requests
import shutil
import urllib.request
from app_utils import generate_encryption_key, copy_file
import backup
from cryptography.fernet import Fernet

logging.basicConfig(filename='storage_operations.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
 
app = Flask(__name__)

key = generate_encryption_key()
print(key)


@app.route('/persistData', methods=['GET'])
def persistData():
	# app.logger.info('Info level log')
	url = request.args.get("url")
	dest_folder = 'data'
	dest_list = ['data/replica-' + str(i) for i in range(1, 4)]
	for dest_folder in dest_list:
		if not os.path.exists(dest_folder):
			os.makedirs(dest_folder)
		filename = url.split('/')[-1].replace(" ", "_")
		file_path = os.path.join(dest_folder, filename+'.jpeg')

		r = requests.get(url, stream=True)
		if r.ok:
			print("saving to", os.path.abspath(file_path))
			# Download the file from `url` and save it locally to `file_path`:
			with urllib.request.urlopen(url) as response, open(file_path, 'wb') as out_file:
				shutil.copyfileobj(response, out_file)
			msg="Downloaded"	
		else:  # HTTP status code 4XX/5XX
			print("Download failed: status code {}".format(r.status_code))
			msg= str(r.status_code)
	return msg


@app.route('/removeData', methods=['GET'])
def removeData():
	filename = request.args.get("filename")
	folders_list = os.listdir('data')
	msg={}
	for dest_folder in folders_list:
		filepath = os.path.join('data', dest_folder, filename)
		if os.path.exists(filepath):
			os.remove(filepath)
			msg[dest_folder] = filename+ " removed"
		else:
			msg[dest_folder]=filename+ " doesn't exist"
	return msg


@app.route('/addReplica', methods=['GET'])
def addReplica():
	count = request.args.get("count")
	try:
		copy_file(file_pattern="./data/replica-", count=int(count))
		msg="added"
	except Exception as e:
		msg=str(e)
	
	return msg


@app.route('/removeReplica', methods=['GET'])
def removeReplica():
	count = int(request.args.get("count"))

	list_files = os.listdir('data')
	len_folder = len(list_files)
	if len_folder > count:
		delete_list = ['data/' + str(i) for i in list_files[-count:]]
		for dest_folder in delete_list:
			shutil.rmtree(dest_folder)
		msg = "Deleted " 
	elif len_folder == count:
		reponse = requests.get(url = 'http://localhost:5000/createBackup')
		delete_list = ['data/' + str(i) for i in list_files[-count:]]
		print(list_files[count+1:])
		print(delete_list)
		for dest_folder in delete_list:
			shutil.rmtree(dest_folder)
			print(dest_folder)
		msg = "Back up taken before deletion as Count of replicas to be deleted ==  # of replicas in data"
	else:
		msg = "Count of replicas to be deleted Greater than # of replicas in /data"
	return msg 


@app.route('/encryptData', methods=['GET'])
def encryptData():
	key1 = request.args.get("key")
	fernet = Fernet(key1)
	folder_path_list = [str('data/' + file_name)
	                        for file_name in os.listdir('data')]
	for replica_path in folder_path_list:
		for filename in os.listdir(replica_path):
			if filename.endswith(".jpeg"):
				file_path = replica_path + '/' + filename
				print("encrypting file :", file_path)
				with open(file_path, 'rb') as file:
					original = file.read()
					encrypted = fernet.encrypt(original)
				with open(file_path, 'wb') as encrypted_file:
					encrypted_file.write(encrypted)
			else:
				continue
	msg = "Encrypted"
	return 



@app.route('/decryptData', methods=['GET'])
def decryptData():
	key1 = request.args.get("key")
	fernet = Fernet(key1)
	folder_path_list = [str('data/' + file_name)
	                        for file_name in os.listdir('data')]
	for replica_path in folder_path_list:
		for filename in os.listdir(replica_path):
			if filename.endswith(".jpeg"):
				file_path = replica_path + '/' + filename
				print("decrypting file :", file_path)
				with open(file_path, 'rb') as enc_file:
					encrypted = enc_file.read()
				decrypted = fernet.decrypt(encrypted)
				with open(file_path, 'wb') as dec_file:
					dec_file.write(decrypted)
			else:
				continue
	msg = "Decrypted"
	return msg

@app.route('/createBackup', methods=['GET'])
def createBackup():
	src = 'data'
	dst = 'backup'
	try:
		for item in os.listdir(src):
			s = os.path.join(src, item) #replica-1/300.jpeg,301.jpeg
			d = os.path.join(dst, item)
			if os.path.exists(d):
				try:
					shutil.rmtree(d)
				except Exception as e:
					msg=str(e)
					os.unlink(d)
			if os.path.isdir(s):
				shutil.copytree(s, d)
		msg="back up taken"
	except Exception as e:
		msg=str(e)
		app.logger.error(msg)

	return 	msg		


if __name__=='__main__':
	app.logger.info('Info level log')
	app.run(host= 'localhost' ,debug=True)
	

