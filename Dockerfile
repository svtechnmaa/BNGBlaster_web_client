FROM python:3.10.12-slim

LABEL org.opencontainers.image.source=https://github.com/svtechnmaa/BNGBlaster_web_client.git

LABEL maintainer "linhnt-hub"

WORKDIR /BNGBlaster_web_client
ENV BNGBLASTER_CONFIG="/root/default_variable.yml"

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends libssl3 libncurses6 libjansson4 libc6-dev make dpkg-dev git openssh-client iputils-ping vim sqlite3 net-tools sudo wget \
    && apt-get clean all \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists/* \
    && wget https://github.com/rtbrick/bngblaster/releases/download/0.9.5/bngblaster-0.9.5-ubuntu-22.04_amd64.deb \
    && sudo dpkg -i bngblaster-0.9.5-ubuntu-22.04_amd64.deb

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt --no-cache-dir

COPY default_variable.yml /root/default_variable.yml 

COPY entrypoint.sh /root/entrypoint.sh
RUN ["chmod", "+x", "/root/entrypoint.sh"]

COPY . .

# RUN rm -rf /BNGBlaster_web_client
EXPOSE 8505
ENTRYPOINT [ "/root/entrypoint.sh" ]
CMD ["/bin/bash"]
