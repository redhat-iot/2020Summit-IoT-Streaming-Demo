from flask import Response
from flask import Flask
from flask import render_template
from flask import send_from_directory


app = Flask(__name__,template_folder='templates')


@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video/<string:file_name>')
def stream(file_name):
    video_dir = './segments'
    return send_from_directory(directory=video_dir, filename=file_name)

 
if __name__ == '__main__':
    
    # Start a thread to build video 
    #build_thread = threading.Thread(target=build_video)
    #build_thread.start()
    app.run(host='0.0.0.0', port=8080,debug=True)

