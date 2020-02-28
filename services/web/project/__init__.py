from flask import Flask, jsonify, request, render_template, current_app
import os
import urllib.request
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['txt', 'pdf'])
UPLOAD_FOLDER='/usr/src/app/uploaded_files'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS
application = Flask(__name__, static_url_path='')
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

@application.route("/upload", methods=["POST"])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify(status="error", message="file not provided in request")

        file = request.files['file']
        if file.filename =='':
            return jsonify(status="error", message="filename may not be blank")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
            return jsonify(status="ok", message="file uploaded successfully")
        if not file:
            return jsonify(status="error", message="file was empty")
        if  not allowed_file(file.filename):
            return jsonify(status="error", message="file needs to be of type .txt or .pdf")
