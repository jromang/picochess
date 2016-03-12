PiFaceCess
=========

Stand alone chess computer based on [Raspberry Pi](http://www.raspberrypi.org/) and [DGT electronic chess board](http://www.dgtprojects.com/site/products/electronic-boards).

With PiFace Support 





Installation 
==========

download Raspbian
https://www.raspberrypi.org

https://www.raspberrypi.org/downloads/raspbian/

show Installation Guide -> https://www.raspberrypi.org/documentation/installation/installing-images/README.md

---------

ssh pi@Rapbianip

# expand SSD
------

sudo raspi-config

 -> step 1 ( "Expanding FileSystem")

 ( reboot "sudo reboot" -> relogin "ssh pi@Raspianip ")
 

# update OS
-------
sudo apt-get update

sudo apt-get upgrade



# enable SPI
--------
sudo raspi-config

 -> step 9 ( "Advanced Options")

   -> A6 SPI ( set on enable )

 ( reboot "sudo reboot" -> relogin "ssh pi@Raspianip ")
 

# install ClientSoftware
---------

cd /opt

sudo git clone https://github.com/marianled/picofacechess.git


sudo /opt/picofacechess/install.sh

reboot -> and play :)

------
