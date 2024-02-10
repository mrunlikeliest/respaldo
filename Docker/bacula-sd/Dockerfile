FROM rockylinux:9.2.20230513

LABEL org.opencontainers.image.authors="Tr0J41n"

# Install Dependencies
RUN yum upgrade -y && \
    yum install -y epel-release wget procps
RUN yum group install -y "Development Tools"
RUN yum install -y libs3-devel libcurl-devel libxml2-devel openssl-devel

WORKDIR /opt/

RUN wget https://www.bacula.org/downloads/libs3-20200523.tar.gz
RUN tar -xvzf libs3-20200523.tar.gz
WORKDIR ./libs3-20200523
RUN chmod +rx GNUmakefile
RUN sed -i "s/ \-Werror / /g" GNUmakefile
RUN make clean && make && make install

EXPOSE 9103

ENTRYPOINT [ "/opt/bacula/sbin/bacula-sd"]
CMD [ "-dt", "-d200","-f", "-c", "/opt/bacula/etc/modified/bacula-sd.conf" ]