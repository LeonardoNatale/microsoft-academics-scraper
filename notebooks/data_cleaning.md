```python
# imports
from typing import List
import sqlite3
import os
import pandas as pd
pd.set_option('display.max_columns', 200000)
import re
import numpy as np
import random
import re
import seaborn as sns
import matplotlib.pyplot as plt
import sklearn
import contractions
import unidecode
from word2number import w2n
import nltk
from nltk import word_tokenize
from nltk import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from gensim.models import Word2Vec

from collections import Counter
from itertools import chain 
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
```

Couldn't install polyglot, which is good for detecting mixed languages within a text, so went for TextBlob as of today:

```python
#!brew install icu4c
#!brew link icu4c --force
#!ICU_VERSION=<BREW_ICU_VERSION> CFLAGS=-I/usr/local/opt/icu4c/include LDFLAGS=-L/usr/local/opt/icu4c/lib pip install pyicu
#!pip3.7 install pycld2
#from polyglot.detect import Detector
from textblob import TextBlob # for now
```

### Helper functions for your corpus

```python
def basic_cleaning(series):
    """
    Removes punctuation, trailing whitespaces, and decapitalize the text in your series. 
    """
    # Expand contractions
    new_series = series.apply(lambda x: contractions.fix(x))
    # Clean html
    new_series = new_series.apply(lambda x: re.sub(re.compile('<.*?>'), '', x))
    # Clean numbers
    new_series = new_series.apply(lambda x: clean_numbers(word_to_number(x)))
    # Expand local abbreviations
    new_series = new_series.apply(lambda x: expand_text_acronyms(x))
    # Decapitalize letters and remove accents
    new_series = new_series.apply(lambda x: remove_accented_chars(str(x).lower()))
    # Remove the first occurrence of abstract
    mask = (new_series.str.split(expand=True).iloc[:,0] == "abstract")
    new_series[mask] = new_series[mask].str.replace("abstract","",1)
    # Remove punctuation
    new_series = new_series.str.replace('[^\w\s#-$€£%]','')
    # Strip trailing whitespace
    new_series = new_series.str.strip(" ")
    return new_series

def remove_accented_chars(text):
    """remove accented characters from text, e.g. café"""
    text = unidecode.unidecode(text)
    return text

## Clean numbers
def word_to_number(x):
    x = [w.split(("-")) for w in x.split()]
    x = [" ".join(sublist) for sublist in x]
    for word in x:
        index = x.index(word)
        try: 
            new_word = w2n.word_to_num(word)
            x[index] = str(new_word)
        except:
            word = word
    x = " ".join(x)
    return x

def clean_numbers(x):
    if bool(re.search(r'\d', x)):
        x = re.sub('[0-9]{5,}', '#####', x)
        x = re.sub('[0-9]{4}', '####', x)
        x = re.sub('[0-9]{3}', '###', x)
        x = re.sub('[0-9]{2}', '##', x)
        x = re.sub('[0-9]{1}', '#', x)
    return x


# Expand acronyms
def expand_text_acronyms(text):
    abbreviation_dict = {}
    sw = set(stopwords.words('english'))
    for match in re.finditer("\(+[A-Z]{1}[^\d)]*\)", text): # find words with at least two capital letters within parentheses 
        start, end = match.span()
        acronym = match.group()
        abbreviation_dict[acronym] = get_expansion(text, acronym, start, sw)
        acronym2 = re.search("\([A-Z]{2}[^a-z]\)",acronym) # clean the acronym
        if acronym2: 
            abbreviation_dict[acronym2.group()] = abbreviation_dict[acronym]
    return replace_all(text, abbreviation_dict)

def get_expansion(text, acronym, start, stopwords):
    truncated_text =  ([w for w in text[:start].split() if not w in stopwords])
    stripped_acronym = acronym.replace("(","").replace(")","")
    candidate_expansion = truncated_text[-len(stripped_acronym)-1:]
    i=0
    w1, w2 = stripped_acronym, candidate_expansion[i]
    while not_same_first_letter(w1, w2):
        i = i+1
        try: 
            w2 = candidate_expansion[i]
        except:
            return " ".join(candidate_expansion).lower()
    return " ".join(candidate_expansion[i:]).lower()

def not_same_first_letter(w1, w2):
    if w1[0].lower() == w2[0].lower():
        return False
    else:
        return True

def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(" "+i+" "," ") # remove abbreviations once they occurred
        text = text.replace(i.replace("(","").replace(")",""), j)
    return text


def tokenize_filter_text(text, custom_stop_words):
    """
    Makes tokens out of your text. 
    """
    # Define stopwords
    stop_words = set(stopwords.words('english')) 
    ## Add personalised stop words
    stop_words |= set(custom_stop_words)
    # Filter the sentence
    word_tokens = word_tokenize(text) 
    filtered_text = [w for w in word_tokens if not w in stop_words] 
    return filtered_text

def tokenize_filter(series, custom_stop_words):
    """
    Tokenises your series.
    """
    return series.apply(lambda x: " ".join(tokenize_filter_text(x, custom_stop_words)))


def stem_tokens(tokens):
    """
    Stems your tokens by keeping only the word root. 
    """
    porter = PorterStemmer()
    tokens = tokens.apply(lambda x: x.split())
    return tokens.apply(lambda x: " ".join([porter.stem(x[i]) for i in range(len(x))]))


def detect_languages(text):
    return TextBlob(text).detect_language()
    #return Detector(text).languages


def generate_tfidf_dataframe(corpus):
    """
    Generates the tf-idf dataframe and matrix from the corpus. 
    """
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(corpus)
    my_word_mapping = {}
    for i, feature in enumerate(vectorizer.get_feature_names()):
        my_word_mapping[i] = feature
    df = pd.DataFrame(matrix.todense())
    df.columns = df.columns.map(my_word_mapping)
    # Replace 0s by NaNs because 0 means the word does not appear within the document
    df = df.replace(0,np.NaN)
    return df, matrix
```

For now, we only clean acronyms within abstracts where the acronym was introduced within brackets. 

```python
#def merge_dicos(merge_dico, dico_list):
#    """
#    Merge a list of dictionaries into one, keeping multiple values per key.
#    """
#    for dico in dico_list:
#        for key,value in dico.items():
#            if merge_dico.get(key,None):
#                merge_dico[key].append(value.lower())
#            else:
#                merge_dico[key] = [value.lower()]
#    for key, value in merge_dico.items(): 
#        merge_dico[key] = list(dict.fromkeys(value))
#    return merge_dico
```

This is the sciencedirect cleaner, hopefully it can be generalised to become our base cleaner. 


Note that we still have to find how we treat number within our corpus: should they be part of our vocabulary, or ignored? How do we link them to units? 

```python
class BaseCleaner():
    def __init__(self, df):
        self.df = df
        self.text_colnames = ["title", "abstract"]
        self.date_colnames = ["publication_date"]
        self.stopwords = dict.fromkeys(self.text_colnames)
        for col in self.text_colnames:
            self.stopwords[col] = [] 
    
    def _drop_abstract_nas(self):
        # Keep papers with abstracts only
        self.df = self.df[self.df['abstract'].notna()].copy()
    
    def _label_languages(self):
        self.df["languages"] = self.df["abstract"].apply(lambda x: detect_languages(x))
    
    def _to_datetime(self, add_year=True):
        for col in self.date_colnames:
            self.df[col] = pd.to_datetime(self.df[col])
            if add_year == True:
                self.df[col+"_year"] = self.df[col].dt.year
        
    def _add_custom_stopwords(self, custom_stopwords):
        for col in self.text_colnames:
            self.stopwords[col].extend(custom_stopwords) # for now, we enter no stopwords
    
    def add_clean_tokenised_stemmed(self, drop_initial=False):
        for colname in self.text_colnames: 
            self.df["clean_"+str(colname)] = basic_cleaning(self.df[str(colname)])
            self.df["tokenized_"+str(colname)] = tokenize_filter(self.df["clean_"+str(colname)], self.stopwords[colname])
            self.df["stemmed_"+str(colname)] = stem_tokens(self.df["tokenized_"+str(colname)])
            if drop_initial == True:
                self.df = self.df.drop(columns=self.text_colnames)

    def vectorize_corpus(self, colname):
        vectorizer = TfidfVectorizer()
        self.tf_idf_matrix = vectorizer.fit_transform(self.df[colname])
        self.my_dict = {}
        for i, feature in enumerate(vectorizer.get_feature_names()):
            self.my_dict[feature] = i
```

### Data pre-processing


Only run this cell once, or you will change directory twice: 

```python
## Uncomment this cell and run it only once
#import os
#os.chdir("../")
```

Now load your dataset:

```python
path = "notebooks/data/"
sd_papers = pd.read_csv(path+"sciencedirect/papers.csv").rename(columns={"id":"paper_id"})
springer_papers = pd.read_csv(path+"springer/papers.csv").rename(columns={"id":"paper_id"})
microsoft_papers = pd.read_csv(path+"microsoft_academics/papers.csv").rename(columns={"id":"paper_id"})
```

We concatenate our papers: 

```python
springer_papers["database"] = "springer"
microsoft_papers["database"] = "microsoft"
df = sd_papers.append(springer_papers).append(microsoft_papers).reset_index()
columns = ["database", "title", "publication_date", "abstract", "doi", "url"]
df = df.loc[:, columns]
```

```python
sd_cleaner = BaseCleaner(df)
sd_cleaner. _drop_abstract_nas()
sd_cleaner._to_datetime(add_year=True)
#sd_cleaner._label_languages()
sd_cleaner.add_clean_tokenised_stemmed(drop_initial=False)
```

```python
df = sd_cleaner.df
df.head()
```

Here, you can check whether the text cleaning was effective by retrieving random abstracts:

```python
i = random.randint(0,len(df))
print(df.iloc[i]["abstract"])
print("################")
print(df.iloc[i]["clean_abstract"])
```

We now vectorize the corpus. 

```python
sd_cleaner.vectorize_corpus("clean_abstract")
sd_cleaner.tf_idf_matrix
```

During basic cleaning, we expanded all usual abbreviations. We now define a list of domain-specific abbreviations to expand. 


Stopwords: we leave them aside for now, as they are useful wihtin BERT models.  
We define a methodology to identify stopwords in our research paper bodies. 
To identify those, we will leverage overall word frequency and the TF-IDF matrix. 
First, let us identify the most frequent word roots within our corpus.


Using the tf-IDF matrix to eliminate stopwords, as a baseline: 

```python
tf_idf_df, tf_idf_matrix = generate_tfidf_dataframe(df["tokenized_abstract"])
tf_idf_matrix
```

Still to be completed / amended: 

```python
def define_stopwords(tf_idf_df, threshold):
    means = tf_idf_df.mean(axis=0)
    plt.hist(means)
    custom_stopwords = list(means[means<threshold].index)
    print(f"{len(custom_stopwords)*100/len(means.index):.1f}% words are stopwords with an {threshold} threshold.")
    print(f"This represents {len(custom_stopwords)} stopwords.")
    return list(custom_stopwords)
```

```python
thresholds = [0.02, 0.045, 0.05, 0.06, 0.07]
for threshold in thresholds:
    custom_stopwords = define_stopwords(tf_idf_df, threshold)
```

We choose a threshold of 0.04 so that approximately 5% of our words are stopwords. 

```python
threshold = 0.07
custom_stop_words = define_stopwords(tf_idf_df, threshold)
sd_cleaner._add_custom_stopwords(custom_stop_words)
sd_cleaner.add_clean_tokenised_stemmed(drop_initial=False)
```

```python
sd_cleaner.vectorize_corpus("tokenized_abstract")
sd_cleaner.tf_idf_matrix
```

Let's have a look at a basic word2vec embedding using python's gensim library

```python
def get_word2vec_format(series):
    """
    Returns a list of tokenized abstracts.
    """
    return [text.split() for text in list(series)]

def filter_vocab(model, search_strings):
    """
    Returns a list of words whose first letters match your strings.
    """
    vocab = list(model.wv.vocab.keys())
    filtered_vocab = []
    for search_string in search_strings:
        filtered_vocab.extend(list(filter(lambda x: x[0:len(search_string)]==search_string, vocab)))
    return filtered_vocab
```

First, format your abstracts to feed into the word2vec model:

```python
tokenized_docs = get_word2vec_format(df["stemmed_abstract"])
```

Then, train your model. 

```python
model = Word2Vec(
    tokenized_docs, 
    size=100, # size of the word embedding
    window=5, # context words to take into account
    workers=10,
    min_count=5, # minimum occurrence of the word in your dataset
    iter=5, # number of epochs over the corpus
)
```

```python
vocabulary = model.wv.vocab
word_vectors = model.wv
```

We now define a list of words to search for similarity against within our corpus.

```python
w1 = filter_vocab(model, ["pov", "health", "hung", "edu", "gend", "wat", "energ", "infra", "indus", "commu", "citi", "peac"])
print(w1)
```

```python
words_to_pop = ["watermelon", "peach", "energiewend"]
for word in words_to_pop:
    w1.pop(w1.index(word))
```

```python
print(w1)
```

```python
w2 = []
```

```python
word_vectors.most_similar(
    positive=w1,
    negative=w2, 
    topn=20)
```

```python
word_vectors
```

```python
word_vectors.similarity("poverti", w1)
```

#### Querying the db

```python
## Uncomment this cell and run it only once
#import os
#os.chdir("../")
```

```python
from models.base import get_session

def merge_dfs(left, middle, right):
    """
    Retrieves papers and their corresponding searchstrings based on the DB tables.
    """
    df_merged = middle.merge(
        right, 
        on=["right_id"], 
        how='left',  
        sort=False).merge(
        left, 
        on = ["left_id"], 
        how="right",)
    return df_merged
```

```python
session = get_session()
```

```python
#paper_query = "SELECT * FROM PAPER"
#searchstring_query =  "SELECT * FROM SEARCHSTRING"
#has_searchstring_query = "SELECT * FROM PAPERHASSEARCHSTRING"
#paper_tag_query = "SELECT * FROM PAPERTAG"
#paper_has_tag_query = "SELECT * FROM PAPERHASTAG"
#author_writes_paper_query = "SELECT * FROM AUTHORWRITESPAPER"
#paper_author_query = "SELECT * FROM PAPERAUTHOR"
#db_query =  "SELECT * FROM RESEARCHDB"
#paper_isin_db_query =  "SELECT * FROM PAPERISINDB"

# Table objects
#papers = pd.read_sql(paper_query, session.bind).rename(columns={"id":"left_id"})
#search_strings = pd.read_sql(searchstring_query, session.bind).rename(columns={"id":"right_id", "name":"searchstring"})
#tags = pd.read_sql(paper_tag_query, session.bind).rename(columns={"id":"right_id", "name":"tag"})
#authors = pd.read_sql(paper_author_query, session.bind).rename(columns={"id":"right_id", "name":"author"})
#databases = pd.read_sql(db_query, session.bind).rename(columns={"id":"right_id", "name":"database"})

# Intermediate tables
#paper_has_search_string = pd.read_sql(has_searchstring_query, session.bind).rename(columns={"paper_id":"left_id", "search_string_id":"right_id"})
#paper_has_tag = pd.read_sql(paper_has_tag_query, session.bind).rename(columns={"paper_id":"left_id", "tag_id":"right_id"})
#author_writes_paper = pd.read_sql(author_writes_paper_query, session.bind).rename(columns={"paper_id":"left_id", "author_id":"right_id"})
#paper_isin_db = pd.read_sql(paper_isin_db_query, session.bind).rename(columns={"paper_id":"left_id", "db_id":"right_id"})

#a = merge_dfs(papers,paper_has_search_string,search_strings).drop(columns=["right_id"])
#b = merge_dfs(a, paper_has_tag, tags).drop(columns=["right_id"])
#c = merge_dfs(b, author_writes_paper, authors).drop(columns=["right_id"])
#d = merge_dfs(c, paper_isin_db, databases).drop(columns=["right_id"]).rename(columns={"left_id":"paper_id"})

## Save full dataframe with duplicate records
#d.to_csv("notebooks/paper_data/sciencedirect_paper.csv")

##Also save only the papers without duplicates: 

#columns = ["paper_id", 'database', 'author', 'tag', 'searchstring','pub_year_filter', 'title', 'publication_date', 'pub_type',
#       'content_type', 'abstract', 'full_text', 'citation_count', 'doi','url']
#n = len(set(d["paper_id"].values))
#df = pd.DataFrame(np.zeros((n,len(columns))), columns=columns)
#
#columns.remove("paper_id")
#
#for i in np.arange(n):
#    paper_id = i+1
#   mask = (d.paper_id == paper_id)
#   df.iloc[i,0] = paper_id
#    for col in columns: 
#        col_index = columns.index(col)+1
#        df.iloc[i,col_index] = ",".join([str(elem) for elem in list(dict.fromkeys((list(d[mask][col]))))])

```

```python
#df.to_csv("notebooks/data/sciencedirect/papers.csv")
```
