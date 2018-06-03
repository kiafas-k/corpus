import newspaper
from aux import createSummary, filterText, getSentiment, NE_extract, dbexec, removeQuotes
import time
import MySQLdb
import configparser
import sys
import os
from dbal import dbal

# init dbase
configuration = configparser.ConfigParser()
configuration.read('parser/config.ini')

dbase = dbal(
    {
        'host': configuration['DATABASE']['host'],
        'username': configuration['DATABASE']['username'],
        'password': configuration['DATABASE']['password'],
        'database': configuration['DATABASE']['database'],
        'charset': configuration['DATABASE']['charset']
    }
)


path_prefix = ''
if len(sys.argv) > 1:
    os.chdir(sys.argv[1])


# load pos neg words
fl = open('parser/negative-words.txt', 'r')
lines = fl.readlines()
fl.close

words_neg = []


for wrd in lines:
    words_neg.append(wrd.replace('\n', ''))

fl = open('parser/positive-words.txt', 'r')
lines = fl.readlines()
fl.close

words_pos = []


for wrd in lines:
    words_pos.append(wrd.replace('\n', ''))


# load sources
query = 'select * from tbl_sources where active=1 order by id'
result = dbase.select(query)
sources = result.data

for src in sources:
    print('scanning source [{}]'.format(src[1]))

    # download articles
    paper = newspaper.build(
        src[1], memoize_articles=True)

    print('Paper size : {}'.format(paper.size()))

    for article in paper.articles:

        # if isinstance(article.title, str) and len(article.title) > 1:
        try:
            article.download()
            article.parse()

            title = article.title
            url = article.url
            timestamp = int(time.time())
            source = src[1]
            keywords = ''
            text = article.text
            named_entities = ';'.join(NE_extract(article.text))
            topic = src[2]

            sentiment = 'neu'
            sentiment_analysis = getSentiment(
                article.text, words_pos, words_neg)
            if sentiment_analysis['positive_percentage'] > sentiment_analysis['negative_percentage']:
                sentiment = 'pos'
            else:
                sentiment = 'neg'

            if sentiment_analysis['text_size'] > 0:

                result = dbase.insert(
                    {
                        'field_names': ['title', 'url', 'timestamp', 'source', 'keywords', 'text', 'named_entities', 'topic', 'sentiment'],
                        'field_values': [title, url, timestamp, source, keywords, text, named_entities, topic, sentiment],
                        'table_name': 'tbl_articles'
                    }
                )

                if result.success == False:
                    print(
                        'Failed to insert {} - ({})'.format(article.title, article.url))
                    print(result.summary())

        except:
            print('failed to store {}'.format(article.title))
