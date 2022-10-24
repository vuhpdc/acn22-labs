#!/bin/bash
# Copyright 2021 Lin Wang

# This code is part of the Advanced Network Programming course at 
# Vrije Universiteit Amsterdam.

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# always run in no error conditions, otherwise it is very hard to follow in the log trace what command might have failed
set -e

cd ~

# clean up in case someone re-do
HOME_DIR=`eval echo ~$USER`
ACN_ENV="$HOME_DIR/acn21-env"
if [[ -d "$ACN_ENV" ]]
then
    echo "$ACN_ENV directory is already there (previous run?), delete and go ahead? Press ENTER for yes, or ctrl+c to stop it here."
    read
    rm -rf $ACN_ENV
fi

# Install generic packages and toolchains
sudo apt-get update

KERNEL=$(uname -r)
# DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade
sudo apt-get install -y --no-install-recommends \
  autoconf \
  automake \
  bison \
  build-essential \
  ca-certificates \
  cmake \
  cpp \
  curl \
  flex \
  git \
  libboost-dev \
  libboost-filesystem-dev \
  libboost-iostreams1.65-dev \
  libboost-program-options-dev \
  libboost-system-dev \
  libboost-test-dev \
  libboost-thread-dev \
  libc6-dev \
  libevent-dev \
  libffi-dev \
  libfl-dev \
  libgc-dev \
  libgc1c2 \
  libgflags-dev \
  libgmp-dev \
  libgmp10 \
  libgmpxx4ldbl \
  libjudy-dev \
  libpcap-dev \
  libreadline7 \
  libreadline-dev \
  libtool \
  libssl1.0-dev \
  linux-headers-$KERNEL\
  make \
  pkg-config \
  python \
  python-dev \
  python-ipaddr \
  python-pip \
  python-psutil \
  python-scapy \
  python-setuptools \
  tcpdump \
  unzip \
  vim \
  wget \
  xcscope-el \
  xterm 

# Navigate to the home directory and create p4-env dir and enter it
mkdir -p $ACN_ENV
cd $ACN_ENV

sudo apt-get install -y git

# Mininet
git clone https://github.com/mininet/mininet mininet
sudo ./mininet/util/install.sh -nwv

# Python libraries
pip install networkx
pip install matplotlib
