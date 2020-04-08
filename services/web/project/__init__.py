from flask import Flask, jsonify, request, render_template, current_app
import os

import urllib.request
from werkzeug.utils import secure_filename
from rq import Queue
from rq.job import Job
from worker.worker import conn




# Application level configuration

ALLOWED_EXTENSIONS = set(['txt', 'pdf'])
# UPLOAD_FOLDER='/usr/local/uploaded_files'
UPLOAD_FOLDER='/usr/local/household'

application = Flask(__name__, static_url_path='')
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
q = Queue(connection=conn)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS




@application.route("/")
def home_page():
    return render_template('index.html')
    # return jsonify(hello="world")
    # return app.send_static_file('index.html')
    # current_path = str(os.getcwd())
    # return jsonify(status="ok", message="current directory: " + current_path)

@application.route("/health")
def application_health():
    return jsonify(application="MJT Personal Document Management", online=True)

@application.route("/test_add_queue")
def test_add_queue():
    job = q.enqueue_call('text_processor.perform_job', [30], description="delay by 30 seconds", meta={'path':'/blah/blah/blah'})
    current_app.logger.error("Added a job to the queue: " + str(job))
    return jsonify(status="Added a job to the queue to sleep for 30 seconds: " + str(job.id))


@application.route("/upload", methods=["POST"])
def upload_file():
    if request.method == 'POST':

        title = request.form.get('title', None)
        year = str(request.form.get('year', None))
        category = request.form.get('category', None)

        if year is None or len(year) == 0 or category is None or len(category) == 0:
            return jsonify(status="error", message="year and category must be provided in request")

        if 'file' not in request.files:
            return jsonify(status="error", message="file not provided in request")

        file = request.files['file']
        if file.filename =='':
            return jsonify(status="error", message="filename may not be blank")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            subdirectory = application.config['UPLOAD_FOLDER'] + "/" +  year + "/" + category + "/"
            if not os.path.isdir(subdirectory):
                mode = 0o755
                os.makedirs(subdirectory, mode)
            file.save(os.path.join(subdirectory, filename))
            return jsonify(status="ok", message="file uploaded successfully")
        if not file:
            return jsonify(status="error", message="file was empty")
        if  not allowed_file(file.filename):
            return jsonify(status="error", message="file needs to be of type .txt or .pdf")
