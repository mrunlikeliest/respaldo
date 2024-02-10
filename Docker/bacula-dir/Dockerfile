FROM rockylinux:9.2.20230513

LABEL org.opencontainers.image.authors="Tr0J41n"

# Install Dependencies
RUN yum upgrade -y && \
    yum install -y epel-release wget procps && \
    yum install -y libpq lzo-devel

EXPOSE 9101

ENTRYPOINT [ "/opt/bacula/sbin/bacula-dir"]
CMD [ "-dt", "-d200","-f", "-c", "/opt/bacula/etc/modified/bacula-dir.conf" ]