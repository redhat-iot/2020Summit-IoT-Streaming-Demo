import pathlib
import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import cv2
import subprocess
import time
import base64
import json 
import imageio

from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils
# 
#  
#from models.research.object_detection.utils import ops as utils_ops
#from models.research.object_detection.utils import visualization_utils  # nopep8
#from models.research.object_detection.utils import label_map_util  # nopep8

import datetime
import time
import cv2
import requests
from io import BytesIO

import boto3
import botocore


s3_endpoint_url = #<Ceph URL>
s3_access_key_id = #<Ceph Access Key> 
s3_secret_access_key = #<Ceph Secred Access Key> 
s3_bucket = 'MyBucket'

tf_url = #<TensorFlow serving's Pod URL> 

def get_category_index():
  """ Transforms label map into category index for visualization.

      Returns:
          category_index: The category index corresponding to the given
              label map.
  """
  label_map = label_map_util.load_labelmap("app/mscoco_complete_label_map.pbtxt")
  categories = label_map_util.convert_label_map_to_categories(
                  label_map,
                  max_num_classes=90,
                  use_display_name=True)
  category_index = label_map_util.create_category_index(categories)
  return category_index

def run_inference_for_single_image(ts_url, image,i):
  
  pngim = Image.fromarray(image)
  
  f = BytesIO()

  pngim.save(f, format="PNG")

  input64 = base64.b64encode(f.getvalue())
  input_string = input64.decode("utf-8")

  # Wraps bitstring in JSON and POSTs, then waits for response
  instance = [{"b64": input_string}]
  data = json.dumps({"instances": instance})

  #Send frame to Tensorflow Serving for inference
  print("POSTing image . Awaiting response...")
  print(ts_url)

  json_response = requests.post(ts_url, data=data)
  print("Response received.")

  # Write output to a .txt file
  #output_file = output_dir + "/text/output" + str(i) + ".txt"
  #with open(output_file, "w") as out:
      #out.write(json_response.text)

  # Extracts the inference results
  response = json.loads(json_response.text)
  response = response["predictions"][0]

  # Visualizes inferred image
  return show_inference(f.getvalue(), response,i)

  

#Overlays the results from image analysis onto frame
def show_inference(input_image, response, i):
  """ Decodes JSON data and converts it to a bounding box overlay
        on the input image, then saves the image to a directory.

    Args:
        input_image: The string representing the input image.
        response: The list of response dictionaries from the server.
        i: An integer used in iteration over input images.
  """

  # Processes response for visualization
  detection_boxes = response["detection_boxes"]
  detection_classes = response["detection_classes"]
  detection_scores = response["detection_scores"]

  # Converts image bitstring to uint8 tensor
  input_bytes = tf.reshape(input_image, [])
  image = tf.image.decode_jpeg(input_bytes, channels=3)

  # Gets value of image tensor
  with tf.Session() as sess:
      image = image.eval()

  # Overlays bounding boxes and labels on image
  visualization_utils.visualize_boxes_and_labels_on_image_array(
      image,
      np.asarray(detection_boxes, dtype=np.float32),
      np.asarray(detection_classes, dtype=np.uint8),
      scores=np.asarray(detection_scores, dtype=np.float32),
      category_index=get_category_index(),
      use_normalized_coordinates=True,
      line_thickness=2)

  #Returns image for cocatination into video 
  return(image)
  #visualization_utils.save_image_array_as_png(image, output_file)



#Function to read in frames and do analysis as long as video sream is active 
def generate():
  s3 = boto3.client('s3',
                  '',
                  use_ssl = False,
                  verify = False,
                  endpoint_url = s3_endpoint_url,
                  aws_access_key_id = s3_access_key_id,
                  aws_secret_access_key = s3_secret_access_key,
                  )
  
  ffmpeg_log = open('app/ffmpeg_log.txt', 'w')
  # Make sure video stream is current 
  print("Removing stale stream file")
  try: 
    os.remove("app/index.m3u8")
    os.remove("app/out.mkv")
  except:
    print("No Video file present")   

  #Make sure livestream is avaliable                                                               
  print("Waiting until livesteam is received...")
  while not os.path.exists("app/index.m3u8"):
    time.sleep(1)
  print("Livestream received")

  #Convert M3u8 into .mkv for frame by frame analysis since OpneCV Loses frames when using Playlist files 
  video_digest = subprocess.Popen(['ffmpeg','-protocol_whitelist','file,http,https,tcp,tls', '-i', 'app/index.m3u8','-c','copy','-bsf:a','aac_adtstoasc','app/out.mkv'],stdout=ffmpeg_log,stderr=ffmpeg_log)
  # Give 10s for ffmpeg to process livestream into OpenCV readable input
  time.sleep(3)
  
  os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "protocol_whitelist;file,tcp,https,tls"
  cap = cv2.VideoCapture("app/out.mkv")
  
  # Get current width of frame
  #width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float

  # Get current height of frame
  #height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) # float

  #fourcc = cv2.VideoWriter_fourcc(*'X264')
  
  ##Another method for Writing Video from frames 
  #video_writer = cv2.VideoWriter('video.mp4',fourcc,30.0,(int(width),int(height))  )
  
  #Frame count 
  i = 0
  #Segment count
  j = 0
  ##Video writed to make MKV segments from Individual analyzed frames 
  video_writer = imageio.get_writer('app/segments/video-%d.mkv'%j,fps=3)

  #While incoming video is received from IoT Device Simulator
  while(cap.isOpened()): 
    
    # Capture frames 
    ret, tempframe = cap.read()
    if ret == True: 
      #Run inference on video Frame    
      #cv2.imshow('Frame',tempframe)
      #Cut down framerate to 15 fps 
      if (i%5 == 0):
        #Every 3 seconds Send Chunk of video
        if(i == 90):
          video_writer.close()
          i=0
          #s3.upload_file("app/out.m3u8", s3_bucket, "out.m3u8")
          #Upload video Chunk(.mkv) to Ceph at the Specified bucket 
          s3.upload_file("app/segments/video-%d.mkv"%j, s3_bucket, "video-%d.mkv"%j)
          j = j+1
          video_writer = imageio.get_writer('app/segments/video-%d.mkv'%j,fps=3)
        #(flag, encodedImage) = cv2.imencode(".jpg", out_frame)
        else:
          video_writer.append_data(run_inference_for_single_image(tf_url, tempframe,i))
          i = i + 1
      else:
        i = i + 1
        continue
      
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
  #Clear variables before closing module 
  j = 0
  i = 0
  video_writer.close()
  video_digest.kill()
 

if __name__ == '__main__':
  # construct the argument parser and parse command line arguments
  #Load model 
  print("Writing Log file")
  generate()

