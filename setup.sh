sudo apt-get update
sudo apt-get -y install python3.7
sudo apt-get -y install python3-pip
sudo apt-get -y install tesseract-ocr
sudo apt-get -y install libmysqlclient-dev
sudo apt-get -y install enchant
sudo apt-get install -y libsm6 libxext6 libxrender-dev
sudo apt-get install -y libmagickwand-dev libopencv-dev
sudo apt-get install poppler-utils
sudo apt-get update && apt-get -y install poppler-utils && apt-get clean
sudo apt install -y docker-compose nodejs gcc enchant
sudo apt install build-essential libpoppler-cpp-dev pkg-config python3-dev

sudo apt install -y nginx
sudo ufw allow 'Nginx Full'
sudo service nginx start
sudo ufw allow ssh
sudo ufw --force enable

pip3 install -r requirements.txt

