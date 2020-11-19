# base image
FROM ubuntu:18.04
 
RUN apt-get update
RUN apt-get -y install python3.7
RUN apt-get -y install python3-pip
RUN apt-get -y install tesseract-ocr
RUN apt-get -y install libmysqlclient-dev
RUN apt-get -y install enchant
RUN apt-get install -y libsm6 libxext6 libxrender-dev
RUN apt-get install -y libmagickwand-dev
RUN apt-get update && apt-get -y install poppler-utils && apt-get clean

ENV LANG C.UTF-8

# add requirements
COPY ./requirements.txt /usr/src/app/requirements.txt

# set working directory
WORKDIR /usr/src/app

# install requirements
RUN pip3 install -r requirements.txt
# RUN python3 -m spacy download en_core_web_md

# add app
COPY . /usr/src/app

#ENTRYPOINT ["python3","-W","ignore","wsgi.py"]
