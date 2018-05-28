from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
from aux import dbexec, parseTemplate, getStats, prepareData, handlePOSTdata, dateToTimestamp, timestampToDate, filterText, randomFileName
from io import BytesIO
# import time
import urllib.parse
import datetime
import random
from nltk import word_tokenize, FreqDist, NaiveBayesClassifier, classify
import pickle
import configparser


def loadFile(filename):
    fl = open(filename, 'r')
    content = fl.readlines()
    content = ''.join(content)
    fl.close

    return content


def find_features(document, word_features):
    words = set(document)
    features = {}
    for w in word_features:
        features[w] = (w in words)

    return features


class myHandler(BaseHTTPRequestHandler):

    def return404Error(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # Send the html message
        message = parseTemplate('404.html', {'': ''})
        self.wfile.write(message.encode())

    def do_GET(self):

        # serve pickle file
        if '.pickle' in self.path:
            url_components = self.path.split('/')
            filename = url_components[-1]

            self.send_response(200)
            self.send_header('Content-type', 'application/octet-stream')
            self.end_headers()

            binfile = open('webface/training-sets/{}'.format(filename), 'rb')
            content = binfile.read()
            binfile.close

            self.wfile.write(content)
            return

        if self.path in pages:

            content = ''

            if self.path in ('/', '/dashboard'):
                content += loadFile('webface/templates/content-dashboard.html')

            if self.path == '/stats':
                stats = getStats()
                content = parseTemplate('content-stats-general.html',
                                        {
                                            '{total_articles}': stats['total_articles'],
                                            '{sources}': stats['sources'],
                                            '{topics}': stats['topics'],
                                            '{time_span}': '38 days'
                                        }
                                        )

            if self.path in ('/insights', '/buildtrainingset'):

                if self.path == '/insights':
                    action_page = 'displayinsights'

                if self.path == '/buildtrainingset':
                    action_page = 'buildtrainingset'

                data = prepareData()
                topic_options = ''
                for topic in data['topics']:
                    topic_options += '<option value="{}">{}</option>'.format(
                        topic, topic)

                named_entities_options = ''
                for entity in data['named_entities']:
                    named_entities_options += '<option value="{}">{}</option>'.format(
                        entity, entity)

                content = parseTemplate('content-insights-search-form.html', {
                    '{topic_options}': topic_options,
                    '{entity_options}': named_entities_options,
                    '{action_page}': action_page
                })

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            message = parseTemplate(
                'layout2.html', {'{page_content}': content})

            self.wfile.write(message.encode())

        else:
            self.return404Error()

        return

    def do_POST(self):
        if self.path in pages:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            content = ''

            # common actions for /displayinsights and /buildtrainingset
            if self.path in ('/displayinsights', '/buildtrainingset'):
                parameters = handlePOSTdata(post_data)

                timespan = urllib.parse.unquote(
                    parameters['timespan']).replace('+', '')
                date_range = timespan.split('-')
                start_date = dateToTimestamp(date_range[0])
                end_date = dateToTimestamp(date_range[1])

                query = 'select * from tbl_articles where '

                counter = 0
                for entity in parameters['entities']:
                    if counter > 0:
                        query += ' OR '
                    query += ' named_entities like "%{}%"'.format(
                        entity.replace('+', ' '))

                    counter += 1
                if counter > 0:
                    query += ' and '

                query += ' topic="{}" and (timestamp between {} and {})'.format(
                    parameters['topic'], start_date, end_date)
                print(query)
                result = dbexec('select', query)

            # Display insights
            if self.path == '/displayinsights':

                if result['success'] and result['rows_returned'] > 0:
                    content = '<ul class="timeline">'
                    for myrow in result['data']:
                        human_time = timestampToDate(myrow[3])

                        if myrow[9] == 'pos':
                            sentiment_color = 'green'
                        if myrow[9] == 'neg':
                            sentiment_color = 'red'
                        if myrow[9] == 'neu':
                            sentiment_color = 'yellow'

                        content += parseTemplate('content-timeline-item.html', {
                            '{date}': human_time,
                            '{source}': myrow[4],
                            '{title}': myrow[1],
                            '{body}': myrow[6][:300],
                            '{url}': myrow[2],
                            '{sentiment}': myrow[9],
                            '{sentiment_color}': sentiment_color

                        })
                    content += '</ul>'
                else:
                    content = parseTemplate('content-message.html', {
                        '{type}': 'warning',
                        '{message_title}': 'Warning',
                        '{message_text}': 'There are no data for this criteria. <br> Please try again',
                    })

            # Build the training set
            if self.path == '/buildtrainingset':
                if result['success'] and result['rows_returned'] > 0:
                    try:
                        documents = []
                        all_words = []

                        for myrow in result['data']:
                            sentiment = myrow[9]
                            article_words = filterText(myrow[6], False)
                            documents.append([article_words, sentiment])
                            # append to all words
                            for wrd in article_words:
                                all_words.append(wrd)

                        all_words = FreqDist(all_words)
                        word_features = list(all_words.keys())[:3000]
                        featuresets = [(find_features(rev, word_features), category)
                                       for (rev, category) in documents]
                        training_set = featuresets

                        classifier = NaiveBayesClassifier.train(training_set)

                        # save training set to binary file
                        filename = randomFileName() + '.pickle'
                        binaryfile = 'webface/training-sets/{}'.format(
                            filename)
                        save_classifier = open(binaryfile, 'wb')
                        pickle.dump(classifier, save_classifier)
                        save_classifier.close()

                        content = parseTemplate('content-message.html', {
                            '{type}': 'success',
                            '{message_title}': 'Success',
                            '{message_text}': 'Your training set was built sucessfully ! <BR> <BR> Clink <a href="/training-sets/{}" target="_blank">HERE</a> to download the binary file'.format(filename),
                        })

                    except:
                        content = parseTemplate('content-message.html', {
                            '{type}': 'warning',
                            '{message_title}': 'Warning',
                            '{message_text}': 'There was an error building the training set. <br> Please try again',
                        })

                else:
                    content = parseTemplate('content-message.html', {
                        '{type}': 'warning',
                        '{message_title}': 'Warning',
                        '{message_text}': 'There are no data for this criteria. <br> Please try again',
                    })

            message = parseTemplate(
                'layout2.html', {'{page_content}': content})

            self.wfile.write(message.encode())

        else:
            self.return404Error()

        return


pages = [
    '/',
    '/dashboard',
    '/stats',
    '/insights',
    '/displayinsights',
    '/buildtrainingset',
]


configuration = configparser.ConfigParser()
configuration.read('webface/config.ini')
HOST = configuration['SERVER']['host']
PORT = configuration['SERVER']['port']

try:
    print('Starting server on {}:{}'.format(HOST, PORT))
    myServer = HTTPServer((HOST, int(PORT)), myHandler)
    myServer.serve_forever()
except:
    print('Server has stopped')
