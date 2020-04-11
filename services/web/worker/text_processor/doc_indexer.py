import os
from text_processor.doc_processor import extract_text
from text_processor.doc_processor import extract_keywords
from whoosh.index import create_in
from whoosh.fields import *


def index_document(document_path, **kwargs):
    index_directory = os.getenv('WHOOSH_INDEX')
    print("The location of the Whoosh index is at: " + index_directory)


    # Step 1.  Extract the text of document located at document_path
    doc_body = extract_text(document_path)

    # Step 2.  Extract the system keywords from the text
    raw_system_tags = extract_keywords(doc_body)
    doc_system_tags = convert_tag_data(raw_system_tags)

    # Step 3.  Get the other meta-data
    doc_title = kwargs.get('title', '')
    doc_user_tags = convert_tag_data(kwargs.get('user_tags', ''))

    # Step 4.  Save the text file as document_path with .txt extension
    write_document_text_with_meta_data(document_path, doc_body, title=doc_title, user_tags=doc_user_tags)


    # Step x.  Index the document text
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


# convert tag data to a comma separated list
def convert_tag_data(tag_data):
    if isinstance(tag_data, list):
        doc_tags = ",".join(tag_data)
    elif isinstance(tag_data, str):
        doc_tags = tag_data
    else:
        doc_tags = ""

    return doc_tags


# process user tags from key word arguments
def process_document_tags(**kwargs):
    raw_user_tags = kwargs.get('user_tags', '')

    if isinstance(raw_user_tags, list):
        doc_user_tags = ",".join(raw_user_tags)
    else:
        doc_user_tags = raw_user_tags

    return doc_user_tags

# Read in optional key word arguments and write the text file with meta-data
def write_document_text_with_meta_data(doc_path, doc_body, **kwargs):

    doc_title = kwargs.get('title', '')
    doc_user_tags = convert_tag_data(kwargs.get('user_tags', ''))
    raw_system_tags = extract_keywords(doc_body)
    doc_system_tags = convert_tag_data(raw_system_tags)

    text_path = compute_text_file_path(doc_path)
    text_file = open(text_path, "w")
    path_line = "path: " + doc_path + "\n"
    text_file.write(path_line)
    title_line = "title: " + doc_title + "\n"
    text_file.write(title_line)
    user_tags_line = "user_tags: " + doc_user_tags + "\n"
    text_file.write(user_tags_line)
    system_tags_line = "system_tags: " + doc_system_tags + "\n"
    text_file.write(system_tags_line)
    text_file.write("\n")
    text_file.write(doc_body)
    text_file.close()

def compute_text_file_path(document_path):
    filename, file_extension = os.path.splitext(document_path)
    base = os.path.basename(filename)
    file_dir = os.path.dirname(document_path)
    text_path = file_dir + "/" + base + ".txt"
    return text_path