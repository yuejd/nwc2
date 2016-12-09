FROM ubuntu:latest

MAINTAINER Jiadi Yue <jdyue19@gmail.com>

RUN apt-get update && \
        apt-get install -y python2.7 python-pip python-dev supervisor nginx openssh-server

RUN echo 'root:root' |chpasswd

RUN sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

RUN service ssh start

ADD requirements.txt /tmp/
ADD supervisord.conf /tmp/
ADD nginx_nwc2 /etc/nginx/sites-enabled/

RUN pip install -r /tmp/requirements.txt

RUN echo_supervisord_conf > /etc/supervisord.conf
RUN cat /tmp/supervisord.conf >> /etc/supervisord.conf

EXPOSE 8888

CMD ["python2", "/nwc2/main.py"]

#service nginx start
#supervisord
