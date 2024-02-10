FROM rockylinux:9.2.20230513 as base

LABEL org.opencontainers.image.authors="Tr0J41n"

ARG POSTGRESPASSWORD
ARG POSTGRESUSER
ARG POSTGRESDATABASE
ARG POSTGRESHOSTADDR
ARG POSTGRESPORT
ARG GCSBUCKET
ARG GCSACCESSKEY
ARG GCSSECRETKEY
ARG GCSREGION

ENV PGPASSWORD=${POSTGRESPASSWORD}
ENV PGHOSTADDR=${POSTGRESHOSTADDR}
ENV PGPORT=${POSTGRESPORT}
ENV PGUSER=${POSTGRESUSER}

# Install Dependencies 
## 18M + (3.2M + 5M) + 1.0G
RUN yum upgrade -y
RUN yum install -y epel-release wget procps
RUN yum group install -y "Development Tools"
RUN yum install -y postgresql-devel docker openldap-devel libs3-devel libcurl-devel libxml2-devel openssl-devel postgresql

WORKDIR /opt/

RUN wget https://www.bacula.org/downloads/libs3-20200523.tar.gz
RUN tar -xvzf libs3-20200523.tar.gz
WORKDIR ./libs3-20200523
RUN chmod +rx GNUmakefile
RUN sed -i "s/ \-Werror / /g" GNUmakefile
RUN make clean && make && make install

WORKDIR ./..

RUN wget https://www.bacula.org/download/11345/?tmstv=1697064943 -O bacula-13.0.3.tar.gz
RUN tar -xvzf bacula-13.0.3.tar.gz
WORKDIR ./bacula-13.0.3
RUN ./configure \
    --prefix=/opt/bacula \
    --with-working-dir=/opt/bacula/working \
    --with-pid-dir=/opt/bacula/working \
    --with-scriptdir=/opt/bacula/scripts \
    --with-plugindir=/opt/bacula/plugins \
    --libdir=/opt/bacula/lib \
    --with-postgresql \
    --enable-docker-plugin \
    --enable-ldap-bpam \
    --enable-cdp-plugin \
    --enable-kubernetes-plugin \
    --enable-smartalloc \
    --with-ldap

RUN make clean && make && make install
RUN mkdir /opt/bacula/etc/modified/

# RUN wget https://www.bacula.org/download/11339/?tmstv=1698612966 -O bacula-gui-13.0.3.tar.gz
# RUN tar -xvzf bacula-gui-13.0.3.tar.gz
# WORKDIR ./bacula-gui-13.0.3/baculum
# RUN mkdir /opt/bacula/baculum-files
# RUN make build DESTDIR=/opt/bacula/baculum-files WWWDIR=/var/www/baculum

WORKDIR /root/
COPY configurator.py ./configurator.py
RUN chmod +rx ./configurator.py
RUN python3 ./configurator.py --dbuser ${PGUSER} --dbpassword ${PGPASSWORD} --dbhost ${PGHOSTADDR} --dbport ${PGPORT} --gcsbucket ${GCSBUCKET} --gcsaccesskey ${GCSACCESSKEY} --gcssecretkey ${GCSSECRETKEY} --gcsregion ${GCSREGION}

# RUN /opt/bacula/scripts/drop_postgresql_database
RUN /opt/bacula/scripts/create_postgresql_database -w
RUN /opt/bacula/scripts/make_postgresql_tables
RUN /opt/bacula/scripts/grant_postgresql_privileges

# ENTRYPOINT [ "tail", "-f", "/dev/null"]
