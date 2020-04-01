import os
import sys
import logging
import base64 

from cloudevents.sdk.event import v02
from cloudevents.sdk import marshaller
import io
import http.server
from socketserver import ThreadingMixIn
import threading
import json 

# Basic multithreaded Python server which acts as a ls
# Cloud Event Listener to write HLS Streaming video to .m3u8 file 

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def run_event(event):
    
    os.chdir("../app")
    f = open("index.m3u8","w")
    logging.info("Creating index.m3u8 file")

    ######Uncomment If running on local 
    #data = json.loads(event.Data())
    #f.write(base64.b64decode(data['records'][0]['value']).decode("utf-8"))
    
    f.write(base64.b64decode(event.Data()).decode("utf-8"))
    logging.info("Writing to index.m3u8 file")
    f.close() 
    

def start_receiver():
        """Start listening to HTTP requests

        :param func: the callback to call upon a cloudevents request
        :type func: cloudevent -> none
        """
        m = marshaller.NewDefaultHTTPMarshaller()

        class BaseHttp(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                content_type = self.headers.get('Content-Type')
                content_len = int(self.headers.get('Content-Length'))
                headers = dict(self.headers)
                data = self.rfile.read(content_len)
                data = data.decode('utf-8')

                event = v02.Event()
                event = m.FromRequest(event, headers, data, str)
                run_event(event)
                self.send_response(204)
                self.end_headers()
                
                return

        class ThreadedCEServer(ThreadingMixIn,http.server.HTTPServer):
            "Deal with concurrent requests in a different thread"

        server = ThreadedCEServer(('', 8000), BaseHttp)
        print ('Starting server on port 8000, use <Ctrl-C> to stop')
        try:
            server.serve_forever() 
        except:
            server.server_close()

if __name__ == '__main__':
    start_receiver()