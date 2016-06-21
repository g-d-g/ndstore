#!/bin/bash

# Installation script for ndstore backend
# Maintainer: Kunal Lillaney <lillaney@jhu.edu>

# update the sys packages and upgrade them
sudo apt-get update && sudo apt-get upgrade -y

# apt-get install mysql packages
echo "mysql-server-5.6 mysql-server/root_password password neur0data" | sudo debconf-set-selections
echo "mysql-server-5.6 mysql-server/root_password_again password neur0data" | sudo debconf-set-selections
sudo apt-get -y install mysql-client-core-5.6 libhdf5-serial-dev mysql-client-5.6

# apt-get install packages
sudo apt-get -y install nginx git bash-completion python-virtualenv libhdf5-dev libxslt1-dev libmemcached-dev g++ libjpeg-dev virtualenvwrapper python-dev mysql-server-5.6 libmysqlclient-dev xfsprogs supervisor rabbitmq-server uwsgi uwsgi-plugin-python liblapack-dev wget memcached libffi-dev libssl-dev  

# create the log directory
sudo mkdir /var/log/ocp
sudo touch /var/log/ocp/ocp.log
sudo chown -R www-data:www-data /var/log/ocp
sudo chmod -R 777 /var/log/ocp/

# add group and user neurodata
sudo addgroup neurodata
sudo useradd -m -p neur0data -g neurodata -s /bin/bash neurodata

# switch user to neurodata and clone the repo with sub-modules
cd /home/neurodata
sudo -u neurodata git clone https://github.com/neurodata/ndstore
cd /home/neurodata/ndstore
sudo git checkout ae-install

# pip install packages
cd /home/neurodata/ndstore/setup/
#sudo pip install -U -r requirements.txt
sudo pip install cython numpy
sudo easy_install -i http://www.turbogears.org/1.5/downloads/current/index TurboGears
sudo easy_install -i http://www.turbogears.org/2.0/downloads/current/PEAK-Rules-0.5a1.dev-r2686.tar.gz PEAK-Rules

sudo pip install -U -r requirements.txt
#sudo pip install django h5py pytest
#sudo pip install pillow posix_ipc boto3 nibabel networkx requests lxml pylibmc blosc django-registration django-celery mysql-python libtiff jsonschema json-spec redis

# switch user to neurodata and make ctypes functions
cd /home/neurodata/ndstore/ocplib
sudo -u neurodata make -f makefile_LINUX

# configure mysql
cd /home/neurodata/ndstore/django/
sudo service mysql start
mysql -u root -pneur0data -i -e "create user 'neurodata'@'localhost' identified by 'neur0data';" && mysql -u root -pneur0data -i -e "grant all privileges on *.* to 'neurodata'@'localhost' with grant option;" && mysql -u neurodata -pneur0data -i -e "CREATE DATABASE neurodjango;"

# configure django setttings
cd /home/neurodata/ndstore/django/OCP/
sudo -u neurodata cp settings.py.example settings.py
sudo -u neurodata cp settings_secret.py.example settings_secret.py

# migrate the database and create the superuser
sudo chmod -R 777 /var/log/neurodata/
cd /home/neurodata/ndstore/django/
sudo -u neurodata python manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('neurodata', 'abc@xyz.com', 'neur0data')" | python manage.py shell
sudo -u neurodata python manage.py collectstatic --noinput

# move the nginx config files and start service
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /home/neurodata/ndstore/setup/ubuntu_config/nginx/default.nginx /etc/nginx/sites-enabled/default
sudo rm /etc/nginx/nginx.conf
sudo ln -s /home/neurodata/ndstore/setup/ubuntu_config/nginx/nginx.conf /etc/nginx/nginx.conf

# move uwsgi config files and start service
sudo rm /etc/uwsgi/apps-available/ocp.ini
sudo ln -s /home/neurodata/ndstore/setup/ubuntu_config/uwsgi/ocp.ini /etc/uwsgi/apps-available/
sudo rm /etc/uwsgi/apps-enabled/ocp.ini
sudo ln -s /home/neurodata/ndstore/setup/ubuntu_config/uwsgi/ocp.ini /etc/uwsgi/apps-enabled/

# move celery config files and start service
sudo rm /etc/supervisor/conf.d/propagate.conf
sudo ln -s /home/neurodata/ndstore/setup/ubuntu_config/celery/propagate.conf /etc/supervisor/conf.d/propagate.conf
sudo rm /etc/supervisor/conf.d/ingest.conf
sudo ln -s /home/neurodata/ndstore/setup/ubuntu_config/celery/ingest.conf /etc/supervisor/conf.d/ingest.conf

# starting all the services
sudo service nginx restart
sudo service uwsgi restart
sudo service supervisor restart
sudo service rabbitmq-server restart
sudo service memcached restart

# running tests
cd /home/neurodata/ndstore/test/
py.test
