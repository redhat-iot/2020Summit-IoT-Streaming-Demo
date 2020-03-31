FROM fedora:31

MAINTAINER Andrew Stoycos "astoycos@redhat.com"

RUN dnf -y update 

RUN dnf -y install git python python-pip

#RUN git clone https://github.com/tensorflow/models.git

RUN pip install --upgrade pip

RUN pip install tensorflow==1.15

RUN pip install opencv-python

RUN pip install Cython

RUN pip install contextlib2

RUN pip install lxml

RUN pip install flask

RUN pip install matplotlib

RUN pip install pillow

RUN pip install kncloudevents

RUN pip install Boto3

RUN pip install imageio

RUN pip install requests

##Install ffmpeg 
RUN cd 

RUN dnf -y install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm

RUN dnf -y install ffmpeg

RUN ffmpeg -version

COPY app/analysis.py ./app/analysis.py

COPY app/mscoco_complete_label_map.pbtxt ./app/mscoco_complete_label_map.pbtxt

COPY app/models/ ./models/

RUN dnf -y install protobuf-compiler python-lxml make

RUN git clone https://github.com/cocodataset/cocoapi.git

RUN dnf -y install gcc python3-devel

RUN cd cocoapi/PythonAPI && make && cp -r pycocotools ../../models/research/

RUN cd models/research && protoc object_detection/protos/*.proto --python_out=. && export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim && python object_detection/builders/model_builder_test.py && python setup.py build && sudo python setup.py install


COPY listener/ ./listener/ 

COPY startScript.sh .

RUN chmod 777 startScript.sh
RUN chmod 777 listener/listener.py
RUN chmod 777 app/analysis.py

#EXPOSE 8080
EXPOSE 8000
EXPOSE 8501

RUN chmod 777 app/

RUN pip install object_detection
RUN pip install imageio-ffmpeg
RUN cd

RUN ls

ENTRYPOINT ["/bin/bash","startScript.sh"]]