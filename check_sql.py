#!/usr/bin/python

username = 'admin'
passwd = 'admin'
hostname = '192.168.88.46'
port = '3306' # if the port is not standard
db_name = 'admin.telephones_numbers' #database.table
pass_length = 14 # password length
ignored_names = ['INSIDER'] # names witch names that are ignored. example ['name1', 'name2',]
title = 'asterisk' # title only for keepass to fill in the required field
keepass_file = "import_to_keepas.txt" # path to the generated keepath file 
txt_file = 'users.txt' # path to the generated txt file

# you can change only <FIELD_NAME> in 
# '\"number\":'   , '\"', <TELEPHONE NUMBER>   , '\"', ','
# '\"name\":', '\"', <USERNAME>, '\"', ','
# '\"email\":' , '\"', <E-MAIL>, '\"'

 
query = """
SELECT CONCAT('[', better_result, ']') AS best_result FROM( 
	SELECT GROUP_CONCAT('{', my_json, '}' SEPARATOR ',') AS better_result FROM (
		SELECT CONCAT ( 	
				'\"phone_number\":'   , '\"', phone_number   , '\"', ',' 
				'\"name\":', '\"', name, '\"', ','
				'\"email\":' , '\"', email, '\"'  
		 ) AS my_json FROM %s
	 ) AS more_json
) AS yet_more_json;
"""%db_name









import subprocess
import json
import random

def get_data(username, passwd, query, hostname, port="3306"):
	try:
		result = subprocess.Popen(['mysql', '-u', username, '-p'+ passwd, '-h', hostname,'-P', port, '-e',  query], 				
				stdout=subprocess.PIPE,	
				stderr=subprocess.PIPE)
		result.wait()
		stdout, stderr = result.communicate()
	except Exception as e:		
		stdout, stderr = "", "ERROR can't execute mysql commands"
	
	print(stdout, stderr)
	return {"stdout": stdout, "stderr": stderr }

v = get_data(username, passwd, query, hostname, port)

"""	
def get_map_from_json(data):
	return json.loads(data.split('\n')[1])



def generate_pass(length=pass_length):
	s = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	return "".join(random.sample(s, length))


def write_to_file(path, s):
	try:
		f = open(path, "w")
		f.write(str(s))
		f.close()
		return True
	except Exception as e:
		print("can't to write text", e)
		return False		


def add_login(persone, ignore_list):
	if persone['phone_number'] != '' and persone['name'] != '' and not any(person['name'].lower() == i.lower() for i in ignore_list ):
		persone['login'] =  "" + persone['name'].split('_')[0] + "_" + persone['phone_number']
		persone['passwd'] = generate_pass()
	else:
		persone['login'] = False 
	return persone

def get_str_for_keepass(persons, title):
	kp_str = '"Account","Login Name","Password","Web Site","Comments"\r\n'
	for person in persons:
		if person['login']:
			kp_str += '"{}","{}","{}","{}","{}"\r\n'.format(
			title, 
			person['login'], 
			person['passwd'],
			person['email'],
			person['name']+" " 
			+person['phone_number'] )
	return kp_str

def get_str_for_txt(persons):
	txt_str = ''
	for persone in persons:
		if persone['login']:
			txt_str += '[{}](remote)\r\nusername = {}\r\nsecret = {}\r\ncallerid = {}\r\n\r\n'.format(
				persone['login'],
				persone['login'],
				persone['passwd'],
				persone['phone_number']
			)
	return txt_str		

#start
data = get_data(username, passwd, query, hostname, port)
if data["stderr"] == '':
	data = get_map_from_json(data['stdout'])
	data = [add_login(person, ignored_names) for person in data]
        print("Keepass: ", "OK" if write_to_file(keepass_file, get_str_for_keepass(data, title)) else "ERROR")
	print("TxtFile: ", "OK" if write_to_file(txt_file, get_str_for_txt(data)) else "ERROR")
else:
	print (data["stderr"])
"""