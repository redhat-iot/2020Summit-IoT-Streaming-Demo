import boto3
import botocore
import os
import subprocess
import sys

import time
import threading


s3_endpoint_url = <Ceph Endpoint> 
s3_access_key_id = <Ceph Access Key ID>
s3_secret_access_key = <Ceph Secret Access Key> 
s3_bucket = 'MyBucket'

s3 = boto3.client('s3',
    '',
    use_ssl = False,
    verify = False,
    endpoint_url = s3_endpoint_url,
    aws_access_key_id = s3_access_key_id,
    aws_secret_access_key = s3_secret_access_key,
    )
s3r = boto3.resource('s3',
    '',
    use_ssl = False,
    verify = False,
    endpoint_url = s3_endpoint_url,
    aws_access_key_id = s3_access_key_id,
    aws_secret_access_key = s3_secret_access_key,)



def build_video(): 
    
    my_bucket = s3r.Bucket(name=s3_bucket)

    if not os.path.exists("segments"):
      os.mkdir("segments")
    ffmpeg_log = open('segments/ffmpeg_log.txt', 'w')
    print(my_bucket.objects.all())
    for my_bucket_object in my_bucket.objects.all():
        print("Getting Segment from Ceph: ",my_bucket_object.key)
        
        s3.download_file(s3_bucket,my_bucket_object.key,"segments/"+my_bucket_object.key)
        os.system("ffmpeg -i segments/"+my_bucket_object.key+" -s 640x360 -hls_flags delete_segments+append_list+omit_endlist -hls_list_size 30 -f hls segments/out.m3u8")
        s3.delete_object(Bucket=s3_bucket,Key=my_bucket_object.key)
        os.remove("segments/"+my_bucket_object.key)


if __name__ == '__main__':

    while(True):
        build_video()
        time.sleep(5)
