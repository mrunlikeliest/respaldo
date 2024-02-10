#!/bin/bash

cp -R /opt/bacula/baculum-files/var/www/baculum/ /var/www/
cp /opt/bacula/baculum-files/etc/httpd/conf.d/baculum-api.conf /etc/httpd/conf.d/
cp /opt/bacula/baculum-files/etc/baculum/Config-api-apache/baculum.users /var/www/baculum/protected/API/Config/

cp --remove-destination /opt/bacula/baculum-files/usr/share/locale/en/LC_MESSAGES/baculum-api.mo /var/www/baculum/protected/API/Lang/en/messages.mo
cp --remove-destination /opt/bacula/baculum-files/usr/share/locale/pl/LC_MESSAGES/baculum-api.mo /var/www/baculum/protected/API/Lang/pl/messages.mo
cp --remove-destination /opt/bacula/baculum-files/usr/share/locale/pt/LC_MESSAGES/baculum-api.mo /var/www/baculum/protected/API/Lang/pt/messages.mo
cp --remove-destination /opt/bacula/baculum-files/usr/share/locale/ru/LC_MESSAGES/baculum-api.mo /var/www/baculum/protected/API/Lang/ru/messages.mo

chown -R apache:apache /var/www/baculum

# systemctl restart httpd

httpd -DFOREGROUND