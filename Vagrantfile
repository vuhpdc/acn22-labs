# Copyright 2021 Lin Wang

# This code is part of the Advanced Computer Networks (2020) course at Vrije 
# Universiteit Amsterdam.

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.box_version = "20211025.0.0"
  config.ssh.forward_x11 = true
  config.vm.network "forwarded_port", guest: 8880, host: 2200
  config.vm.define "acn21" do |vm|
  end
  ## CPU & RAM
  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--cpuexecutioncap", "100"]
    vb.memory = 4096
    vb.cpus = 2
  end
  # Disk
  config.disksize.size = '30GB'
  config.vm.provision "shell", inline: <<-SHELL
     # Start in /vagrant instead of /home/vagrant
     if ! grep -Fxq "cd /vagrant" /home/vagrant/.bashrc
     then
      echo "cd /vagrant" >> /home/vagrant/.bashrc
     fi
  SHELL
  config.vm.synced_folder ".", "/vagrant"
  config.vm.provision "shell", path: "scripts/root-bootstrap.sh"
  config.vm.provision "shell", privileged: false, path: "scripts/user-bootstrap.sh"

end
