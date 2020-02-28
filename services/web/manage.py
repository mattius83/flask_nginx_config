from flask.cli import FlaskGroup
from project import application

cli = FlaskGroup(application)

if __name__ == "__main__":
    # cli()
    application.run(host='0.0.0.0', port=5000)
