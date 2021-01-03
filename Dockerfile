FROM python:3.7-buster
MAINTAINER Rodrigo Monteiro <rodrigoma@gmail.com>

ENV TIMEZONE=America/Sao_Paulo

RUN apt-get -q update && \
  apt-get install -qy wget

# Copy project
COPY . /opt/comicstreamer
RUN python3 -m pip install -r /opt/comicstreamer/requirements.txt

# Install unrar
RUN wget http://www.rarlab.com/rar/unrarsrc-5.2.6.tar.gz -P /tmp/ && \
  tar xzf /tmp/unrarsrc-5.2.6.tar.gz -C /tmp/ 
WORKDIR /tmp/unrar
RUN make lib && make install-lib
WORKDIR /
RUN rm -r /tmp/unrar*
ENV UNRAR_LIB_PATH /usr/lib/libunrar.so
RUN cp /usr/lib/libunrar.so /opt/comicstreamer/libunrar/libunrar.so

# Volumes needed
VOLUME ["/config","/data"]

EXPOSE 32500
ENTRYPOINT ["/opt/comicstreamer/comicstreamer", "--quiet", "--nobrowser", "--user-dir=/config"]