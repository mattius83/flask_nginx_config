from flask import Flask, jsonify, request, render_template, current_app
import os

import urllib.request
from werkzeug.utils import secure_filename
from rq import Queue
from rq.job import Job
from worker.worker import conn
import project.searcher




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
    #job = q.enqueue_call('text_processor.perform_job', [30], description="delay by 30 seconds", meta={'path':'/blah/blah/blah'})
    kw = {"title": "Sample File", "user_tags": ["red", "green", "blue"]}
    job = q.enqueue_call('text_processor.doc_indexer.index_document', ['/usr/local/household/sample.pdf'], kwargs=kw)
    current_app.logger.error("Added a job to the queue: " + str(job))
    return jsonify(status="Added a job to the queue to index a document: " + str(job.id))

@application.route("/search")
def search_docs():
    search_term = request.args.get('q')
    results = searcher.search_documents_by_term(search_term)
    return jsonify(data=results)


@application.route("/upload", methods=["POST"])
def upload_file():
    if request.method == 'POST':

        title = request.form.get('title', None)
        year = str(request.form.get('year', None))
        category = request.form.get('category', None)
        user_tags = request.form.get('tags', None)


        current_app.logger.error("Here is the title: " + title)
        current_app.logger.error("Here is the user_tags: " + user_tags)

        if year is None or len(year) == 0 or category is None or len(category) == 0:
            return jsonify(status="error", message="year and category must be provided in request")

        if 'file' not in request.files:
            return jsonify(status="error", message="file not provided in request")

        file = request.files['file']
        if file.filename =='':
            return jsonify(status="error", message="filename may not be blank")

        if not file:
            return jsonify(status="error", message="file was empty")
        if  not allowed_file(file.filename):
            return jsonify(status="error", message="file needs to be of type .txt or .pdf")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            subdirectory = application.config['UPLOAD_FOLDER'] + "/" +  year + "/" + category + "/"
            if not os.path.isdir(subdirectory):
                mode = 0o755
                os.makedirs(subdirectory, mode)
            document_path = os.path.join(subdirectory, filename)
            file.save(document_path)

            # place an job on the queue to index
            positional_arg_list = [document_path]
            max_timeout_in_minutes = 10
            max_timeout_in_seconds = max_timeout_in_minutes * 60
            kw = {"title": title, "user_tags": user_tags}
            job = q.enqueue_call('text_processor.doc_indexer.index_document', positional_arg_list, timeout=max_timeout_in_seconds, kwargs=kw)
            current_app.logger.error("Added a job to the queue: " + str(job))
            return jsonify(status="ok", message="file uploaded successfully")
