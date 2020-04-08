import os





def index_document():
    index_directory = os.getenv('WHOOSH_INDEX')
    print("The location of the Whoosh index is at: " + index_directory)
