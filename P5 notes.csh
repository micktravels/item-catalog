#!/bin/bash
# These commands to be run by root

#  Setup new user "grader"
#  Password Authentication is already disabled
#  First - create RSA key pair locally.  Passphrase = "Udacity Rules"

adduser grader		# password = Udacity123
echo "grader ALL=(ALL) ALL" > /etc/sudoers.d/grader

cd /home/grader
mkdir .ssh
cd .ssh

# Copy public key into authorized_keys

chown grader authorized_keys
chmod 644 !$
cd ..
chown grader .ssh
chgrp grader .ssh
chmod 700 .ssh
cd ~/.ssh
mv authorized_keys temp-authorized_keys  # save the pub key file, but get it out of the way

exit


##############
#
#  These commands to be run by grader once account is sudoed by process above
#
##############

# Update all currently installed packages

sudo apt-get update
sudo apt-get upgrade
sudo apt-get autoremove

# Change the ssh port from 22 to 2200

sudo nano /etc/ssh/sshd_config
sudo service ssh restart

sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow www
sudo ufw allow ntp
sudo ufw allow 2200/tcp
sudo ufw deny 22/tcp
sudo ufw enable
sudo ufw status

sudo reboot			# probably a necessary vestige from the updgrades, but gets rid of a message at login

#  Install and configure Apache to serve a Python mod_wsgi application

sudo apt-get install apache2
# verify it's working by http:<IP address>

sudo apt-get install libapache2-mod-wsgi

# edit /etc/apache2/sites-available/000-default.conf to add the following line just above </VirtualHost>
# WSGIScriptAlias / /var/www/html/myapp.wsgi
sudo apache2ctl restart

# create /var/www/html/myapp.wsgi
# verify it's working by http:<IP address>

sudo nano /etc/hosts 
# first line should read something like "127.0.0.1 localhost </etc/hostname contents>""
# to get rid of the stupid "unable to resolve host XYZ" error every time you try to sudo something

#  Install and configure PostgreSQL
sudo apt-get install postgresql
sudo apt-get install python-psycopg2

#  good help here - https://www.digitalocean.com/community/tutorials/how-to-secure-postgresql-on-an-ubuntu-vps
#  Automatically disallows remote connections - verified by seeing 127.0.0.1 in the /etc/postgresql/9.3/main/pg_hba.conf file

sudo su - postgres
createuser -d -S -R -P catalog
# -P password prompt:  password needs to go into all 3 catalog python files
createdb -U catalog catalog

# verify by doing:
psql
	>> \du
	# list of users and roles appears
	>> CREATE DATABASE catalog     # do this if the createdb command above doesn't work
	>> \l
	# list of databases.  Should see catalog there!
	>> \q
exit		# get out of the postgres user account

# Install git, clone and set up your Catalog App project (from your GitHub repository from earlier in the Nanodegree program)
#   so that it functions correctly when visiting your server’s IP address in a browser.

sudo apt-get install python-flask-sqlalchemy	# verify with "from flask import Flask" within python
cd ~
git clone git://github.com/micktravels/item-catalog

### Edit python files to account for sqlite -> postgresql change.  This means:
###     add "import psycopg2" at the top of each file
###     engine = create_engine('postgresql+psycopg2://catalog:Adm9ZHtw52pcGDGeWmZY@localhost/catalog')
###     shorten descriptions in afewitems.py - can't be more than 250 characters 8-(
###		adjust app.run(host='0.0.0.0', port=8000) to real host name and port=80
### 	open('client_secrets.json', 'r') needs full pathname:  open('/var/www/html/client_secrets.json', 'r')

# item-catalog needs a few more packages to run:  seasurf, oauth2
sudo apt-get install python-setuptools
sudo easy_install flask-seasurf
sudo apt-get install python-oauth2
easy_install --upgrade google-api-python-client

# copy item catalog files to apache directory
cd /var/www/html
sudo cp -r ~/item-catalog/* .

# point wsgi to the application
sudo rm myapp.wsgi

# apply new myapp.wsgi file cobbled together from various sources.
# I still have no idea how anyone figured this part out.  I think I got a lot from these sites:
#    http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/#creating-a-wsgi-file
#    http://flask.pocoo.org/snippets/99/
#    https://discussions.udacity.com/t/client-secret-json-not-found-error/34070
#    https://discussions.udacity.com/t/cannot-import-from-another-python-file/35988

	#!/usr/bin/python
	import sys
	import logging
	logging.basicConfig(stream=sys.stderr)
	sys.path.insert(0,"/var/www/html")
	from application import app as application

	application.secret_key = 'super_secret_key'

http://ec2-52-26-20-173.us-west-2.compute.amazonaws.com
