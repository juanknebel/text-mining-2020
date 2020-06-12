from nltk import word_tokenize, sent_tokenize
import nltk
from nltk.corpus import stopwords
from gensim import corpora
import logging


nltk.download('stopwords')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

handler = logging.FileHandler('nltk.log')
format = logging.Formatter('%(asctime)s  %(name)s%(levelname)s: %(message)s')
handler.setFormatter(format)
logger.addHandler(handler)


def tokenize(one_document, stop_words=stopwords.words('english')):
  one_document = one_document.lower()
  
  return [
    word for word in word_tokenize(one_document) if word not in stop_words
    and word.isalpha() and len(word) > 1
    ]


def create_dictionary(all_texts, no_below, no_above):
  dictionary = corpora.Dictionary(all_texts)
  logger.info(f"Lenght of the dictionary {len(dictionary)}")
  dictionary.filter_extremes(no_below=no_below, no_above=no_above)
  logger.info(f"Lenght of the dictionary {len(dictionary)} filter by no_below {no_below} and no_above {no_above}")
  return dictionary


def prepare_documents(list_of_documents, stop_words=stopwords.words('english'), no_below=10, no_above=0.5):
  texts = [tokenize(a_doc, stop_words) for a_doc in list_of_documents]
  dictionary = create_dictionary(texts, no_below, no_above)
  corpus = [dictionary.doc2bow(text) for text in texts]

  return texts, dictionary, corpus
