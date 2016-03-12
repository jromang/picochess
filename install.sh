# expand over  raspi-conf (expand)
# add SPI  over raspi-conf


echo "install needet software"

sudo apt-get -y install groff espeak python{,3}-pifacecad python3-configobj
sudo apt-get -y install python3-dev libmysqlclient-dev 
sudo apt-get -y install pychess stockfish python3-espeak


cd /opt/picofacechess
sudo pip3 install --upgrade -r requirements.txt


echo "get source from repositories"

sudo cp /opt/picofacechess/install/picochess.ini /opt/picofacechess/picochess.ini

cd /opt

sudo git clone https://github.com/marianled/dgtnix.git
sudo chown -R  pi:pi dgtnix
sudo git clone https://github.com/marianled/dgtdrv.git
sudo chown -R  pi:pi dgtdrv
#sudo git clone https://github.com/marianled/picofacechess.git
sudo chown -R  pi:pi picofacechess

echo "install board driver"

cd /opt/dgtnix/
sh ./configure
sudo make
sudo make check
sudo make install

cd /opt/dgtdrv/
sudo make

cd /opt/picofacechess
sudo cp /opt/picofacechess/install/picochess.init /etc/init.d/picochess
sudo chmod +x /etc/init.d/picochess 
sudo update-rc.d picochess defaults 98 02
