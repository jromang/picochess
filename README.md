PiFaceCess
=========

Stand alone chess computer based on [Raspberry Pi](http://www.raspberrypi.org/) and [DGT electronic chess board](http://www.dgtprojects.com/site/products/electronic-boards).

With PiFace Support 





Installation 
==========

1.) download and Install  Raspbian
https://www.raspberrypi.org

https://www.raspberrypi.org/downloads/raspbian/

show Installation Guide -> https://www.raspberrypi.org/documentation/installation/installing-images/README.md

---------

2.) Login 
------

ssh pi@Rapbianip

3.)  expand SSD
------

sudo raspi-config

 -> step 1 ( "Expanding FileSystem")

 ( reboot "sudo reboot" -> relogin "ssh pi@Raspianip ")
 

4.) update OS
-------
sudo apt-get update

sudo apt-get upgrade



5.) enable SPI
--------
sudo raspi-config

 -> step 9 ( "Advanced Options")

   -> A6 SPI ( set on enable )

 ( reboot "sudo reboot" -> relogin "ssh pi@Raspianip ")
 

6.) install ClientSoftware
---------

cd /opt

sudo git clone https://github.com/LaMaRiaN/picofacechess.git


sudo /opt/picofacechess/install.sh

reboot -> and play :)

------
