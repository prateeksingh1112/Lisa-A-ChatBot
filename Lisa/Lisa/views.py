from django.shortcuts import render , redirect , HttpResponse
import nltk
import wikipedia
import numpy as np
import json
import pandas as pd
import re
from nltk.stem import wordnet # to perform lemmitization
from sklearn.feature_extraction.text import TfidfVectorizer # to perform tfidf
from nltk import pos_tag # for parts of speech
from sklearn.metrics import pairwise_distances # to perfrom cosine similarity
from nltk.corpus import stopwords # for stop words
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import csv
import argparse
import utils
import requests
import random

def index(request):
    return render(request , 'chatbo.html')


def weather(text):
    try:
        BASE_URL = "https://www.metaweather.com/api/"
        LOCATION_SEARCH_URL = BASE_URL + "location/search/"
        WEATHER_INFO_URL = BASE_URL + "location/{}/"


        def get_location_id(query):
            
            # get location id

            r = requests.get(LOCATION_SEARCH_URL, params={'query': query})
            data = r.json()
            if len(data):
                return data[0]['woeid']
        # get_location_id('chennai')

        def get_weather(query,day=1):
            """
            get weather data
            """
            location_id = get_location_id(query)
            if location_id is None:
                return "Location not found."
            r = requests.get(WEATHER_INFO_URL.format(location_id))
            data = r.json()
            result = {}
            result['location'] = data['title']
            result['weather'] = []
            for day_weather in data['consolidated_weather'][:day]:
                result['weather'].append({
                    'date': day_weather['applicable_date'],
                    'min_temp': round(day_weather['min_temp'], 2),
                    'max_temp': round(day_weather['max_temp'], 2),
                    'weather_state_name': day_weather['weather_state_name']
                })
            return result

        data=get_weather(text)
        
        name='Location : '+data['location']
        dat=''
        weaty=''
        mintemp=''
        maxtemp=''
        # d['Location:']=data['location']
        for row in data['weather']:
                dat="Date : "+row['date']
                weaty="Weather Type : "+row['weather_state_name']
                mintemp="Min Temp. : "+ str(row['min_temp'])
                maxtemp="Max Temp. : "+str(row['max_temp'])

        # print([name, dat, weaty,mintemp,maxtemp])
        return [name, dat, weaty,mintemp,maxtemp]      
    except:
        d='We are sorry but right now we cant fetch the weather of given city . Try after some time or enter another city or city from another country.'
        # print(d)
        return d
def movie(text):
    f = open(r"C:\Users\Prateek Singh\Downloads\New Folder\New Folder\data\Complete_data.csv" , encoding='Utf-8')
    csv_f = csv.reader(f)
    Answer = 'Oops !! Sorry , Not Available . You can visit our website for movies'
    if '#movie' in text:
        text = text[1:]
    heading = " ".join(text)
    print(heading)
    link = "http://3.7.171.228/"
    for i in csv_f:
        if heading.lower() in i[0].lower():
            link = "http://3.7.171.228/movi/search?Search=" + heading.replace(" " , '+')
            Answer = "Here's your link"
            break
    return Answer , link , heading



def wiki(text):
    if '#wiki' in text:
        text = text[1:]

    para = wikipedia.summary(" ".join(text))
    para = para[:250] + "......"
    heading = text
    text = "_".join(text)
    link = 'https://en.wikipedia.org/wiki/' + text
    return [para , link , heading]



class General:
    def __init__(self, fileName):
        self.df = pd.read_excel(fileName)
        self.df['lemmatized_text'] = self.df['Context'].apply(self.text_normalization)

        self.stop = stopwords.words('english')

        self.tfidf = TfidfVectorizer()  # intializing tf-id
        self.x_tfidf = self.tfidf.fit_transform(self.df['lemmatized_text']).toarray()

        self.df_tfidf = pd.DataFrame(self.x_tfidf, columns=self.tfidf.get_feature_names())

    def text_normalization(self, text):
        text = str(text).lower()  # text to lower case
        spl_char_text = re.sub(r'[^ a-z]', '', text)  # removing special characters
        tokens = nltk.word_tokenize(spl_char_text)  # word tokenizing
        lema = wordnet.WordNetLemmatizer()  # intializing lemmatization
        tags_list = pos_tag(tokens, tagset=None)  # parts of speech
        lema_words = []  # empty list
        for token, pos_token in tags_list:
            if pos_token.startswith('V'):  # Verb
                pos_val = 'v'
            elif pos_token.startswith('J'):  # Adjective
                pos_val = 'a'
            elif pos_token.startswith('R'):  # Adverb
                pos_val = 'r'
            else:
                pos_val = 'n'  # Noun
            lema_token = lema.lemmatize(token, pos_val)  # performing lemmatization
            lema_words.append(lema_token)  # appending the lemmatized token into a list

        return " ".join(lema_words)  # returns the lemmatized tokens as a sentence

    def chat_tfidf(self, text):
        lemma = self.text_normalization(text)  # calling the function to perform text normalization
        tf = self.tfidf.transform([lemma]).toarray()  # applying tf-idf
        cos = 1 - pairwise_distances(self.df_tfidf, tf, metric='cosine')  # applying cosine similarity
        index_value = cos.argmax()  # getting index value
        if cos.max() < 0.3:
            return "Oops. Sorry about that. I'm still learning."

        return self.df['Text Response'].loc[index_value]

g = General(r'C:\Users\Prateek Singh\Downloads\New Folder\New Folder\data\lisa_mind3.xlsx')


def city_news(url):
    details_list = []
    response = requests.get(url, timeout=10)
    count = 0
    soup = BeautifulSoup(response.content, 'html.parser')
    for link in soup.find_all('a'):
        z = link.text
        p = len(z)
        if p > 60:
            details_list.append(z)
            count += 1
            if count == 6:
                break
    return details_list

def news_india(url):
    details_list = []
    response = requests.get(url, timeout=10)
    c1 = 1
    count = 0
    soup = BeautifulSoup(response.content, 'html.parser')
    for link in soup.find_all('li'):
        z = link.text
        if c1 == 0:

            details_list.append(z)
            count += 1
            if count == 5:
                break
        if z == "UGC news":
            c1 = 0
    return details_list


def entertanment_india(url):
    details_list = []
    response = requests.get(url, timeout=10)
    c1 = 1
    count = 0
    soup = BeautifulSoup(response.content, 'html.parser')
    for link in soup.find_all('a'):
        z = link.text
        if c1 == 0:
            details_list.append(z)
            count += 1
            if count == 6:
                break
        if z == "Videos":
            c1 = 0
    return details_list


def sports_news(url):
    details_list=[]
    response = requests.get(url, timeout=10)
    c1 = 1
    count = 0
    soup = BeautifulSoup(response.content, 'html.parser')
    for link in soup.find_all('li'):
        z = link.text
        if c1 == 0:
            details_list.append(z)
            count += 1
            if count == 10:
                break
        if z == "Others" and c1 == 2:
            c1 = 0
        if z == "NFL":
            c1 = 2
    return details_list


def newws(trick):
    sports_url = "https://timesofindia.indiatimes.com/sports"
    bollywood_url = "https://timesofindia.indiatimes.com/etimes"
    business_url = "https://timesofindia.indiatimes.com/business"
    tec_url = "https://www.gadgetsnow.com/?utm_source=toiweb&utm_medium=referral&utm_campaign=toiweb_hptopnav"
    news_url = "https://timesofindia.indiatimes.com/india"
    mumbai_url = "https://timesofindia.indiatimes.com/city/mumbai"
    delhi_url = "https://timesofindia.indiatimes.com/city/delhi"
    chennai_url = "https://timesofindia.indiatimes.com/city/chennai"
    df= trick
    details_list = []
    c = 0
    count = 0
    height=len(df)
    print(height)
    z= "".join(df.split())
    print(z)
    print(z[9:])

    k=0
    if z == "#news":
        print(z , 'india tv')
        details_list = news_india(news_url)
        k=news_url
        tu= "News"
    if z == '#newsbollywood' :
        details_list = entertanment_india(bollywood_url)
        k=bollywood_url
        tu="Bollywood News"
    if z == "#newssports":
        details_list = sports_news(sports_url)
        k=sports_url
        tu="News Sports"

    if "#newscity" in z:
        k='https://timesofindia.indiatimes.com/city/' + z[9:]
        details_list = city_news(k)
        tu = "News City "+z[9:]
    print(details_list)
    p=z[1:]
    a=details_list[0]
    b=details_list[1]
    c=details_list[2]
    return a, b, c, k, tu


def Lisa(request):
    question = request.GET.get('msg')
    wi=False
    wikip = False
    moviep = False
    ns= False
    Link = ''
    heading = ''
    dat=''
    weaty=''
    mintemp=''
    maxtemp=''
    news_list=''
    l=[]
    h=''
    Answer=""
    a=''
    b=''
    c=''
    if '#wiki' in question:
        question = question.split(" ")
        question = question[1:]
        Answer , Link , heading = wiki(question)
        wikip = True

    elif '#news' in question:
          a,b,c,l,h = newws(question)
          ns=True


    elif '#weather' in question:
        question=question.split(' ')
        question=question[1:]
        result = weather(question) 
        if type(result) != str:
            Answer , dat , weaty ,mintemp, maxtemp = result
            
        else:
            # print(type(result))
            Answer=result
            
        wi=True

          

    elif '#movie' in question:
        question = question.split(" ")
        question = question[1:]
        Answer , Link, heading = movie(question)
        moviep = True




    else:
        Answer = g.chat_tfidf(question)
        print(Answer)


    resp = {
        'wiki' : wikip,
        'movie' : moviep,
        'Answer': Answer,
        'Link' : Link,
        'Heading' : heading,
        'wi' : wi,
        'dat' : dat,
        'weaty': weaty,
        'mintemp': mintemp,
        'maxtemp': maxtemp,
        "ns":ns,
        "news_list": news_list,
        "l": l,
        "h": h,
        'a':a,
        'b':b,
        'c':c,

    }

    response = json.dumps(resp)

    return HttpResponse(response, content_type="application/json")

