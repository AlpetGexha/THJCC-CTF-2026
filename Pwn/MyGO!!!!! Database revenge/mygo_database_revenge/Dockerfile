FROM ubuntu:22.04@sha256:104ae83764a5119017b8e8d6218fa0832b09df65aae7d5a6de29a85d813da2fb  

RUN apt-get update
RUN apt-get -y install xinetd

RUN useradd -m chal
USER chal
WORKDIR /home/chal

CMD ["/usr/sbin/xinetd", "-dontfork"]
