import os
from text_processor.doc_processor import extract_text
from text_processor.doc_processor import extract_keywords
from whoosh.index import create_in
from whoosh.fields import *


def index_document(document_path):
    index_directory = os.getenv('WHOOSH_INDEX')
    print("The location of the Whoosh index is at: " + index_directory)


    # Step 1.  Extract the text of document located at document_path

    text = extract_text(document_path)
    # print("Here is the text of the document:")
    # print(text)

    filename, file_extension = os.path.splitext(document_path)
    base = os.path.basename(filename)
    file_dir = os.path.dirname(document_path)
    text_path = file_dir + "/" + base + ".txt"
    text_file = open(text_path, "w")
    num_chars_written = text_file.write(text)
    text_file.close()


    # Step 2.  Save the text file as document_path with .txt extension
    filename, file_extension = os.path.splitext(document_path)


    # Step 3.  Index the document text
    #           - text
    #           - keywords
    #           - path
    #           - tags


#  This function only needs to be called one time to initialize the Whoosh 'household' index
def initialize_household_index():
    index_directory = os.getenv('WHOOSH_INDEX')
    print("Here is the location of the WHOOSH_INDEX:  " + index_directory)
    if not os.path.exists(index_directory):
        print("Directory:  " + index_directory + "did not exist")
        schema = Schema(title=TEXT, path=ID(stored=True), body=TEXT, system_tags=KEYWORD, user_tags=KEYWORD)
        ix = create_in(index_directory, schema, indexname="household")


