FROM ubuntu/apache2:latest

LABEL org.opencontainers.image.authors="Tr0J41n"

RUN apt-get update
RUN apt-get install -y wget procps
RUN apt-get install -y build-essential
RUN apt-get install -y apache2 libapache2-mod-php php-bcmath php-cgi php-mysql php-pgsql php-json php-xml php-curl php-ldap

RUN wget https://www.bacula.org/download/11339/?tmstv=1698612966 -O bacula-gui-13.0.3.tar.gz
RUN tar -xvzf bacula-gui-13.0.3.tar.gz
WORKDIR ./bacula-gui-13.0.3/baculum
RUN mkdir /opt/baculum-files
RUN make build DESTDIR=/opt/baculum-files SAMPLETYPE=deb-template HTTPDNAME=apache2 HTTPDSITECONF=sites-available WWWDIR=/var/www/baculum

RUN cp -R /opt/baculum-files/var/www/baculum/ /var/www/
RUN cp /opt/baculum-files/etc/apache2/sites-available/baculum-web.conf /etc/apache2/sites-available/
RUN cp /opt/baculum-files/etc/baculum/Config-web-apache/baculum.users /var/www/baculum/protected/Web/Config/
RUN cp --remove-destination /opt/baculum-files/usr/share/locale/en/LC_MESSAGES/baculum-web.mo /var/www/baculum/protected/Web/Lang/en/messages.mo
RUN cp --remove-destination /opt/baculum-files/usr/share/locale/pl/LC_MESSAGES/baculum-web.mo /var/www/baculum/protected/Web/Lang/pl/messages.mo
RUN cp --remove-destination /opt/baculum-files/usr/share/locale/pt/LC_MESSAGES/baculum-web.mo /var/www/baculum/protected/Web/Lang/pt/messages.mo
RUN cp --remove-destination /opt/baculum-files/usr/share/locale/ru/LC_MESSAGES/baculum-web.mo /var/www/baculum/protected/Web/Lang/ru/messages.mo

RUN chown -R www-data:www-data /var/www/baculum
RUN a2ensite baculum-web
RUN a2enmod rewrite

EXPOSE 9096

RUN service apache2 restart

ENTRYPOINT [ "apache2-foreground" ]