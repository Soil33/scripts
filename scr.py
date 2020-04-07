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
tmp_file='/tmp/sql_out'
error_file='/tmp/sql_err'
# you can change only <FIELD_NAME> in 
# '\"number\":'   , '\"', <TELEPHONE NUMBER>   , '\"', ','
# '\"name\":', '\"', <USERNAME>, '\"', ','
# '\"email\":' , '\"', <>, '\"'

 
#query = """
#SELECT CONCAT('[', better_result, ']') AS best_result FROM( 
#	SELECT GROUP_CONCAT('{', my_json, '}' SEPARATOR ',') AS better_result FROM (
#		SELECT CONCAT ( 	
#				'\"phone_number\":'   , '\"', phone_number   , '\"', ',' 
#				'\"name\":', '\"', name, '\"', ','
#				'\"email\":' , '\"', email, '\"'  
#		 ) AS my_json FROM %s
#	 ) AS more_json
#) AS yet_more_json;
#"""%db_name

query = """SELECT phone_number, name, email FROM %s;"""%db_name 








import subprocess
import json
import random
import os
import time

def get_data(username, passwd, query, hostname, port="3306"):
	try:		
		p = subprocess.Popen(['mysql', '-u', username, '-p'+ passwd, '-h', hostname,'-P', port, '-e',  query], 				
				stdout=subprocess.PIPE,	
				stderr=subprocess.PIPE
				)
		stdout, stderr = p.communicate()
	except Exception as e:		
		 return {'stdout':"", 'stderr':e}
	
	
	return {"stdout": stdout, "stderr": stderr}


	
def get_map_from_json(data):
	lines = data.split('\n')
	response = []
	for line in lines[1:-1]:
		line = line.split('\t')
		response.append({
			"phone_number"	: line[0],
			"name"		: line[1],
 			"email"		: line[2]
		})
	return response



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
	if persone['phone_number'] != '' and persone['name'] != '' and not any(person['name'].lower().find(i.lower() ) != -1 for i in ignore_list ):
		name = persone['name'].split('_')
		phone = persone['phone_number']
		login = "%s-%s_%s"%(name[0], name[1][0:4], phone) if len(name) > 1 else "%s_%s"%(name[0], phone)
		persone['login'] =  login
		persone['passwd'] = generate_pass()
		print("ADD\t: %s(%s)"%(persone['name'], login))
	else:
		persone['login'] = False 
		print("IGNOR\t: %s"%persone['name'])
	return persone

def get_str_for_keepass(persons, title):
	kp_str = '"Account","Login Name","Password","Web Site","Comments"\r\n'
	for person in persons:
		if person['login']:

			kp_str += '"%s","%s","%s","%s","%s"\r\n'%(
			title, 
			person['login'], 
			person['passwd'],
			person['email'],
			person['name'])
	return kp_str

def get_str_for_txt(persons):
	txt_str = ''
	for persone in persons:
		if persone['login']:
			txt_str += '[%s](remote)\r\nusername = %s\r\nsecret = %s\r\ncallerid = %s\r\nmailbox = %s\r\n\r\n'%(
				persone['login'],
				persone['login'],
				persone['passwd'],
				persone['phone_number'],
				persone['email']
			)
	return txt_str		

#start
print("- Load data")
data = get_data(username, passwd, query, hostname, port)
if data["stderr"] == '':
	print('- Create map')
	data = get_map_from_json(data['stdout'])
	print('- Add login and password to data')
	data = [add_login(person, ignored_names) for person in data]
	print('- Create output files')
        print("Keepass: ", "OK" if write_to_file(keepass_file, get_str_for_keepass(data, title)) else "ERROR")
	print("TxtFile: ", "OK" if write_to_file(txt_file, get_str_for_txt(data)) else "ERROR")	
	print('- DONE!!!!')
else:
	print (data["stderr"])
