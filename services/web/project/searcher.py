from flask import current_app
import os
from whoosh.index import open_dir
from whoosh import qparser

def search_documents_by_term(search_terms):

    index_directory = os.getenv('WHOOSH_INDEX')
    ix = open_dir(index_directory)

    with ix.searcher() as searcher:
        og = qparser.OrGroup.factory(0.9)  # documents containing more of words should score higher
        mparser = qparser.MultifieldParser(["title", "body", "user_tags"], schema=ix.schema, group=og)
        query = mparser.parse(search_terms)
        results = searcher.search(query)
        doc_results = []

        for hit in results:
            item = {}
            item['title'] = hit['title']
            item['path'] = hit['path']
            doc_results.append(item)

    return doc_results