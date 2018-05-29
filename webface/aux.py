import MySQLdb
import configparser
import time
import datetime
from nltk import PorterStemmer, word_tokenize
from nltk.corpus import stopwords
import random


def dbexec(operation_type, query):
    configuration = configparser.ConfigParser()
    configuration.read('webface/config.ini')

    result = {
        'success': True,
        'data': (),
        'rows_returned': 0,

    }

    if not operation_type in['insert', 'update', 'delete', 'select']:
        result['success'] = False
    else:
        db = MySQLdb.connect(
            configuration['DATABASE']['host'], configuration['DATABASE']['username'], configuration['DATABASE']['password'], configuration['DATABASE']['database'],)
        db.set_character_set('utf8')
        cursor = db.cursor()

        try:
            if operation_type == 'select':
                cursor.execute(query)
                result['data'] = cursor.fetchall()
                result['rows_returned'] = cursor.rowcount

            if operation_type == 'insert':
                cursor.execute(db.escape_string(query))
                db.commit()

        except:
            result['success'] = False

        db.close()

    return result


def parseTemplate(filename, pagedata):
    try:
        fl = open('webface/templates/' + filename, 'r')
        content = fl.readlines()
        content = ''.join(content)
        fl.close

        placeholders = pagedata.keys()
        for placeholder in placeholders:
            content = content.replace(placeholder, str(pagedata[placeholder]))
    except:
        content = 'Error parsing template'

    return content


def getStats():

    stats = {}

    # count total articles
    query = 'select count(id) from tbl_articles'
    result = dbexec('select', query)
    if result['success']:
        total_articles = result['data'][0][0]
    else:
        total_articles = 'N/A'

    stats['total_articles'] = total_articles

    # get sources
    query = 'select distinct source from tbl_articles'
    result = dbexec('select', query)
    if result['success']:
        sources = result['rows_returned']
        sources_list = []
        for myrow in result['data']:
            sources_list.append(myrow[0])
        sources_full = '<br>'.join(sources_list)
    else:
        sources = 'N/A'
        sources_full = ''

    stats['sources'] = sources
    stats['sources_full'] = sources_full

    # get topics
    query = 'select distinct topic from tbl_articles'
    result = dbexec('select', query)
    if result['success']:
        topics = result['rows_returned']
        topics_list = []
        for myrow in result['data']:
            topics_list.append(myrow[0])
        topics_full = '<br>'.join(topics_list)
    else:
        topics = 'N/A'
        topics_full = ''

    stats['topics'] = topics
    stats['topics_full'] = topics_full

    return(stats)


def prepareData():

    data = {}

    # get timespan
    timespan = {}
    query = 'select max(timestamp) as newest, min(timestamp) as oldest from tbl_articles'
    result = dbexec('select', query)
    timespan['newest'] = result['data'][0][0]
    timespan['oldest'] = result['data'][0][1]
    data['timespan'] = timespan

    # get named entities
    named_entities = []
    query = 'select named_entities from tbl_articles order by id'
    result = dbexec('select', query)
    for myrow in result['data']:
        row_entities = myrow[0].split(';')
        for entity in row_entities:
            named_entities.append(entity)

    named_entities.sort()
    unique_entities = set(named_entities)

    data['named_entities'] = unique_entities

    # get topics
    topics = []
    query = 'select distinct topic from tbl_articles'
    result = dbexec('select', query)
    for myrow in result['data']:
        topics.append(myrow[0])

    data['topics'] = topics

    return data


def handlePOSTdata(request_data):

    data = {
        'topic': '',
        'entities': [],
        'timespan': '---'
    }

    txt_data = request_data.decode()
    components = txt_data.split('&')
    for component in components:
        parts = component.split('=')
        if 'topic' in parts[0]:
            data['topic'] = parts[1]

        if 'entities' in parts[0]:
            data['entities'].append(parts[1])

        if 'timespan' in parts[0]:
            data['timespan'] = parts[1]

    return data


def dateToTimestamp(date_string):
    date_elements = date_string.split('/')
    timestamp = datetime.datetime(int(date_elements[2]), int(
        date_elements[1]), int(date_elements[0]), 0, 0).timestamp()

    return int(timestamp)


def timestampToDate(timestamp):
    human_time = time.strftime(
        "%d-%m-%Y %H:%M:%S", time.gmtime(int(timestamp)))

    return human_time


def filterText(text, stemmed=False):
    if stemmed:
        porter = PorterStemmer()

    # remove stopwords and useless words
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)

    valuable_words = []
    for wrd in words:
        if len(wrd) > 3 and not wrd in stop_words:
            if stemmed:
                valuable_words.append(porter.stem(wrd.lower()))
            else:
                valuable_words.append(wrd.lower())

    return valuable_words


def randomFileName():
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
               'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

    filename = ''

    while len(filename) <= 30:
        filename += letters[random.randint(0, len(letters) - 1)]

    return filename
