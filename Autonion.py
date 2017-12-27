#!/usr/bin/env python
import socket
import os
import time
import sys

def is_connected():
  try:
    host = socket.gethostbyname("www.google.com")
    s = socket.create_connection((host, 80), 2)
    return True
  except:
     pass
  return False

def checkTor():
	if os.path.exists("/var/lib/tor") == True and os.path.exists("/etc/tor/torrc") == True:
		print("Tor is installed")
		return True
	else:
		print("Tor is not installed")
		return False

def checkApache():
	if os.path.exists("/etc/apache2") == True:
		print("Apache2 is installed")
		return True
	else:
		print("Apache2 is not installed")
		return False

def ReadAddr():
	with open("/var/lib/tor/hostname", "r") as file:
		address = file.read()[:-1]
	return address

def GetTor():
	if checkTor() == False:
		print("Installing tor\n")
		os.system("sudo apt-get install tor -y")
		print("")
		if checkTor() == False:
			print("Error: Tor doesn't seem to be installed after installation")
		        exit()
			
def WaitForHost():
	t = 0
	while os.path.exists("/var/lib/tor/hostname") == False:
		time.sleep(1)
		t = t + 1
		if t == 12:
			os.system("sudo service tor restart")
		if t > 60:
			print("Error: The hostname does not seem to appear.")
			exit()

def ConfigApache(address):
	with open("/etc/apache2/sites-enabled/" + address + ".conf", "w") as file:
		file.write("<VirtualHost 127.0.0.1:80>\n")
		file.write("	ServerAdmin webmaster@localhost\n")
		file.write("	DocumentRoot /var/www/" + address + "\n")
		file.write("	ErrorLog ${APACHE_LOG_DIR}/error.log\n")
		file.write("	CustomLog ${APACHE_LOG_DIR}/access.log combined\n")
		file.write("</VirtualHost>")

def Exist(address):
	if os.path.exists("/var/lib/tor/private_key") and os.path.exists("/etc/apache2/sites-enabled/" + address + ".conf") and os.path.exists("/var/www/" + address):
		return True
	else:
		return False

if os.getuid() != 0:
	print("Error: Script must be run as root with root privelages.")
	exit()
print "Checking Internet connection."
if is_connected() == False:
	print("Error: Cannot reach the internet.")
	exit()
print "Internet OK"
if len(sys.argv) > 1:
	if sys.argv[1] == "renew":
		curr = ""
		if os.path.exists("/var/lib/tor/hostname") == True:
			curr = ReadAddr()
			print "Discovered " + curr + ", renewing"
		else:
			print "Error: No existing address found to renew, please run without arguments."
			exit()
		if Exist(curr):
			os.system("sudo rm /var/lib/tor/hostname;sudo rm /var/lib/tor/private_key")
			os.system("sudo service tor restart")
			WaitForHost()
			new = ReadAddr()
			print "Your new web address will be http://" + new
			os.system("sudo mv /etc/apache2/sites-enabled/" + curr + ".conf /etc/apache2/sites-enabled/" + new + ".conf")
			ConfigApache(new)
			os.system("sudo mv /var/www/" + curr + " /var/www/" + new + ";sudo service apache2 restart")
		else:
			print "Previous address was wrongly configured. Try running without arguments"
			exit()
else:
	if os.path.exists("/var/lib/tor/hostname"):
		ad = ReadAddr()
		if Exist(ad):
			c = raw_input("There already seems to be " + ad + ". Would you like to continue? [y/n] ")
			if c == "n":
				exit()
	GetTor()
	print("Configuring the torrc file")
	f = open("/etc/tor/torrc", "r")
	dir = "HiddenServiceDir /var/lib/tor/\n"
	port = "HiddenServicePort 80 127.0.0.1:80\n"
	for line in f:
		if line[:-1] == port[:-1]:
			port = ""
		if line[:-1] == dir[:-1]:
                	dir = ""
	with open("/etc/tor/torrc", "a") as file:
		file.write(dir)
		file.write(port)
	print("Hidden service configured on port 80")
	print("Restaring tor to enable hidden service")
	os.system("sudo service tor restart")
	print("Tor restarted. Checking for hostname")
	WaitForHost()
	address = ReadAddr()
	print("Your web address will appear as http://" + address)
	print(address + " is not reachable yet. Apache web server must be configured.")
	if checkApache() == False:
		print("Installing apache2\n")
		os.system("sudo apt-get install apache2 -y")
		print("")
		if checkApache() == False:
			print("Error: Apache failed to install")
			exit()
	print("Creating Website directory at /var/www/" + address)
	os.system("sudo mkdir /var/www/" + address)
	print("Configuring Apache2")
	ConfigApache(address)
	os.system("service apache2 restart")
	print("Making index.html")
	with open("/var/www/" + address + "/index.html", "w") as file:
        	file.write("<p>This hidden service was autoconfigured by Autonion.<p>\n")
		file.write("<a href='https://github.com/Cabbache/Autonion'>https://github.com/Cabbache/Autonion</a>")
	print("Your hidden service should be reachable at http://" + address + " in a few minutes")
	print("The root directory is at /var/www/" + address)
	print("Done.")
