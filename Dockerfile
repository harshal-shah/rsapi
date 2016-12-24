FROM python:2.7
MAINTAINER Harshal Shah
ADD . /rsapi
RUN pip install -r /rsapi/requirements.txt
WORKDIR /rsapi
CMD python rsapi.py