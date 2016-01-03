
# Pull base image
FROM resin/rpi-raspbian
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
ADD . /picochess

WORKDIR /picochess
RUN pip3 install -r requirements.txt

# Define default command
CMD ["bash"]
