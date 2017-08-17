# Autonion
Automatically creates your onion site

### How it works ###
The script modifies your torrc file in /etc/tor/torrc to generate your onion address and private key in /var/lib/tor.
Then it runs your onion site on apache2 web server on 127.0.0.1:80. The torrc file is configured to redirect requests
from the onion port 80 to 127.0.0.1:80.

### Usage ###
This script is compatible with linux. It is written in python so you must have python installed.
To execute ----->> **python Autonion.py**, this should setup everything and if you want to generate
a new random address do **python Autonion.py renew**. Your website content should not be lost when
renewing.

The script was only tested on kali linux.
