import pickle
import os
import pandas as pd
import numpy as np

import sys
sys.path.append('../ModelTrain')

import gensim
from gensim.utils import simple_preprocess
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel, LdaModel
import nltk
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from ModelTrain.ML.ml_util import df_to_html
from ModelTrain import app


def lda(file_path, params):
    print('STARTING LDA')
    values = dict()
    for (param, value) in params.items():
        if(value is not None and value != []):
            if(param == 'beta'):
                values['eta'] = value
            else:
                values[param] = value

   
    df = file_path

    text_df = pd.DataFrame(df[values['text_column']])

    #Stop Words
    stop_words = list(stopwords.words('english'))

    if 'extra_stop_words' in values:
        for word in values['extra_stop_words']:
            stop_words.append(word)
    
    stop_words = set(stop_words)

    #Preprossing
    print('STARTING PREPROCESS')

    processed_df = text_df[values['text_column']].apply(lambda x: preprocess(stop_words, x))
    texts = processed_df.tolist()
    processed_df= processed_df.to_frame()
    

    #ID2WORD and CORPUS BOW
    text_dictionary = Dictionary(processed_df[values['text_column']])
    BoW = [text_dictionary.doc2bow(text) for text in processed_df[values['text_column']]]


    #LDA Model
    print('TRAINING MODEL')


    del values['text_column']

    if 'extra_stop_words' in values:
        del values['extra_stop_words']

    lda_model = LdaModel(corpus=BoW, id2word=text_dictionary, random_state=100, passes=10,
                                    **values)

    filename = 'ldaModel.pkl'
    file_loc = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)

    with open(file_loc, 'wb') as file:
        pickle.dump(lda_model, file)
    
    
    with open(file_loc, 'rb') as file:
        model_object = pickle.load(file)
    
    
    print('GETTING C_V')

    coherence_model = CoherenceModel(model=lda_model,corpus=BoW, texts = texts, 
                                dictionary=text_dictionary,coherence='c_v')
    
    coherence_score = coherence_model.get_coherence()

    #TOPIC MODELING
    corpus_topics = lda_model[BoW]
    corpus_topic_distr= [corpus_topics[i] for i in range(len(corpus_topics))]

    text_df_list=text_df.values.tolist()

    text_n_topic = list(zip(text_df_list, corpus_topic_distr))
    text_n_topic_df = pd.DataFrame(text_n_topic, columns=['Text', 'Topic Distribution'])



    
    model = {
        'name': 'Latent Dirichlet Allocation',
        'score': coherence_score,
        'model_object': model_object,
        'filename': filename,
        'result': text_n_topic_df
        
    }

    return model


def get_lda_extra(model):
    topics = model.print_topics(num_topics=-1, num_words = 5)
    df = pd.DataFrame(topics, columns=['Topic Id', 'Topic'])
    df.set_index('Topic Id', inplace=True)

    print_lda =df_to_html(df, convert_to_df=False)
    return print_lda
   



def tagText(text):
    return nltk.pos_tag(text)

def getPOS(token_tag):
    if token_tag.startswith('J'):
        return wordnet.ADJ
    elif token_tag.startswith('V'):
        return wordnet.VERB
    elif token_tag.startswith('N'):
        return wordnet.NOUN
    elif token_tag.startswith('R'):
        return wordnet.ADV
    else:
        return ''

def lemAndStem(token, POS):
    stemmer = SnowballStemmer("english")
    lemmatizer = WordNetLemmatizer()

    POS = getPOS(POS)
    if POS:
         return stemmer.stem(lemmatizer.lemmatize(token, pos=POS))
    else:
        return stemmer.stem(lemmatizer.lemmatize(token))

def preprocess(stop_words,review):
    processed_review = []
    
    for token in simple_preprocess(review):
        if token not in stop_words and len(token)> 3:
            processed_review.append(token)
    
    tagged_review = tagText(processed_review)

    ready_review = []
    for word_set in tagged_review:
        ready_review.append(lemAndStem(word_set[0], word_set[1]))

    
   
    return ready_review



