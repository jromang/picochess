
# Pull base image
FROM resin/rpi-raspbian:jessie
MAINTAINER Dieter Reuter <dieter@hypriot.com>

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    gcc \
    vim \
    git \
    python3-dev \
    python3-pip \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

#CMD cd /opt
# Define working directory

#Pull Code
RUN git clone https://github.com/jromang/picochess
RUN pip3 install -r picochess/requirements.txt
WORKDIR /picochess
CMD git pull && python3 picochess.py

# Define default command
CMD ["bash"]
