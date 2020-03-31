FROM fedora:31

MAINTAINER Andrew Stoycos "astoycos@redhat.com"

RUN dnf -y update 

RUN dnf -y install git python python-pip

RUN pip install --upgrade pip

RUN pip install flask

RUN pip install Boto3

RUN pip install requests

##Install ffmpeg 
RUN cd 

RUN dnf -y install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm

RUN dnf -y install ffmpeg

RUN ffmpeg -version

COPY update.py .

COPY serving.py .

COPY startScript.sh .

COPY segments/ ./segments 

COPY templates/ ./templates

RUN chmod 777 startScript.sh
RUN chmod 777 update.py
RUN chmod 777 serving.py
RUN chmod 777 segments/
RUN chmod 777 .


EXPOSE 8080
EXPOSE 8000

ENTRYPOINT ["/bin/bash","startScript.sh"]