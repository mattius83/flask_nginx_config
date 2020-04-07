import PyPDF2
import textract
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk


def extract_text(doc_path):

    nltk.download('punkt')
    nltk.download('stopwords')

    pdfFileObj = open(doc_path, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    num_pages = pdfReader.numPages
    count = 0
    text = ""

    while count < num_pages:
        pageObj = pdfReader.getPage(count)
        count = count + 1
        text = text + pageObj.extractText()

    if len(text) == 0:
        raw_text = textract.process(doc_path, method='tesseract', language='eng')
        text = raw_text.decode("utf-8")

    return text

def extract_keywords(text):
    tokens = word_tokenize(text)
    punctuations = ['?', '(', ')', ';', ',', ':', '[', ']', '@', '|', '&', '=', '>', '<', '{', '}', '+', '-', '_', '*', '^', '%', '$', '#', '!']
    stop_words = stopwords.words('english')

    keywords = [ word for word in tokens if not word in stop_words and not word in punctuations ]
    unique_keywords = list(set(keywords))

    return unique_keywords

