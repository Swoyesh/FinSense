import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')
# nltk.download('omw-1.4')
# nltk.download('averaged_perceptron_tagger')

from nltk.tokenize import word_tokenize
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def textPreprocessing(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    text = word_tokenize(text)
    return text

# def stopwordRemoval(text):
#     text = [word for word in text if word not in stop_words]
#     return text

def lemmatization(text):
    text = [lemmatizer.lemmatize(word) for word in text]
    return text

def posTagging(text):
    text = nltk.pos_tag(text)
    text = [word for word, tag in text if tag.startswith('N') or tag.startswith('V')]   
    return text

def cleanTextPipeline(text):
    text = textPreprocessing(text)
    # text = stopwordRemoval(text)
    text = lemmatization(text)
    text = posTagging(text)
    text = ' '.join(text)
    return text