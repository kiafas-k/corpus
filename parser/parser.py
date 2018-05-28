import newspaper
from aux import createSummary, filterText, getSentiment, NE_extract, dbexec, removeQuotes
import time
import MySQLdb
import configparser
import sys
import os


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
sources = dbexec('select', query)

for src in sources['data']:
    print('scanning source [{}]'.format(src[1]))

    # download articles
    paper = newspaper.build(
        src[1], memoize_articles=True)

    print('Paper size : {}'.format(paper.size()))

    for article in paper.articles:

        # if isinstance(article.title, str) and len(article.title) > 1:

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

        try:
            if sentiment_analysis['text_size'] > 0:
                configuration = configparser.ConfigParser()
                configuration.read('parser/config.ini')

                db = MySQLdb.connect(
                    configuration['DATABASE']['host'], configuration['DATABASE']['username'], configuration['DATABASE']['password'], configuration['DATABASE']['database'],)
                db.set_character_set('utf8')
                cursor = db.cursor()

                text = removeQuotes(text)
                text = str(db.escape_string(text))
                text = text[2: - 2]

                title = removeQuotes(title)
                title = str(db.escape_string(title))
                title = title[2: -2]

                query = '''insert into tbl_articles (title,url,timestamp,source,keywords,text,named_entities,topic,sentiment) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

                cursor.execute(query, (title, url, timestamp, source,
                                       keywords, text, named_entities, topic, sentiment))
                db.commit()
                db.close()

        except:
            print('failed to store {}'.format(article.title))
