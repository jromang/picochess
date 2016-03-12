# expand over  raspi-conf (expand)
# add SPI  over raspi-conf

echo .
echo "install system update"
echo "y/n"
read updateOS

if (( $updateOS == "y" )); then
    echo "system update"
    sudo apt-get update
    sudo apt-get -y upgrade
   
    echo .
    echo "reboot system"
    echo "y/n"
    read startreboot

    if (( $startreboot == "y" )); then
        reboot
        quit
    fi
fi


echo "install needet software"

sudo apt-get -y install groff


echo "get source from repositories"

cd /opt

sudo git clone https://github.com/marianled/dgtnix.git
sudo chown -R  pi:pi dgtnix
sudo git clone https://github.com/marianled/dgtdrv.git
sudo chown -R  pi:pi dgtdrv
sudo git clone https://github.com/marianled/picofacechess.git
sudo chown -R  pi:pi picofacechess


echo "install board driver"

cd /opt/dgtnix/
sh ./configure
sudo make
sudo make check
sudo make install

cd /opt/dgtdrv/
sudo make
