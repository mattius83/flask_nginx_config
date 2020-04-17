import os
from text_processor.doc_processor import extract_text
from text_processor.doc_processor import extract_keywords
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh import qparser



def remove_document(index_dir, document_path):
    writer = index_dir.writer()
    writer.delete_by_term('path', document_path)
    writer.commit()


def has_document_been_indexed(index_dir, document_path):

    with index_dir.searcher() as searcher:
        parser = qparser.QueryParser("path", schema=index_dir.schema)
        query = parser.parse(document_path)
        results = searcher.search(query)
        if len(results) > 0:
            return True
        else:
            return False


def index_document(document_path, **kwargs):


    # Step 1.  Extract the text of document located at document_path
    print("Extracting Text from " + document_path)
    extracted_text = extract_text(document_path)
    doc_body = extracted_text.casefold()


    # Step 2.  Extract the system keywords from the text
    print("Extracting keywords from " + document_path)
    raw_system_tags = extract_keywords(doc_body)
    doc_system_tags = convert_tag_data(raw_system_tags)

    # Step 3.  Get the other meta-data
    print("Getting Meta-data")
    doc_title = kwargs.get('title', '')
    doc_user_tags = convert_tag_data(kwargs.get('user_tags', ''))

    # Step 4.  Save the text file as document_path with .txt extension
    print("Making Text File Copy of: " + document_path)
    write_document_text_with_meta_data(document_path, doc_body, title=doc_title, user_tags=doc_user_tags)

    # Step 5.  Index the document text using WHOOSH, if path already indexed, remove it and re-index
    print("Indexing " + document_path + " via Whoosh")
    index_directory = os.getenv('WHOOSH_INDEX')
    index_pointer = open_dir(index_directory)
    writer = index_pointer.writer()
    if has_document_been_indexed(index_pointer,document_path ):
        writer.delete_by_term('path', document_path)
    writer.add_document(title=doc_title, path=document_path, body=doc_body, system_tags=doc_system_tags, user_tags=doc_user_tags)
    writer.commit()


#  This function only needs to be called one time to initialize the Whoosh 'household' index
def initialize_household_index():
    index_directory = os.getenv('WHOOSH_INDEX')
    print("Here is the location of the WHOOSH_INDEX:  " + index_directory)
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), body=TEXT, system_tags=KEYWORD(lowercase=True, commas=True), user_tags=KEYWORD(lowercase=True, commas=True))
    ix = create_in(index_directory, schema)


# convert tag data to a comma separated list
def convert_tag_data(tag_data):
    if isinstance(tag_data, list):
        doc_tags = ",".join(tag_data)
    elif isinstance(tag_data, str):
        doc_tags = tag_data
    else:
        doc_tags = ""

    return doc_tags


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