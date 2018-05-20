from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
from aux import dbexec, parseTemplate, getStats, prepareData, handlePOSTdata
from io import BytesIO
import time


def getRAM():
    command = 'free -m'
    result = subprocess.run(command.split(' '), stdout=subprocess.PIPE)
    return result.stdout.decode()


def sysCommand(command):
    result = subprocess.run(command.split(' '), stdout=subprocess.PIPE)
    return result.stdout.decode()


def loadFile(filename):
    fl = open(filename, 'r')
    content = fl.readlines()
    content = ''.join(content)
    fl.close

    return content


class myHandler(BaseHTTPRequestHandler):

    def do_GET(self):

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

            if self.path == '/insights':
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
                    '{entity_options}': named_entities_options
                })

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            message = parseTemplate(
                'layout2.html', {'{page_content}': content})

            self.wfile.write(message.encode())

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # Send the html message
            message = 'The page you are looking for does not exist'
            self.wfile.write(message.encode())

        return

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        parameters = handlePOSTdata(post_data)

        query = 'select * from tbl_articles where topic="{}" and '.format(
            parameters['topic'])
        counter = 0
        for entity in parameters['entities']:
            if counter > 0:
                query += ' OR '
            query += ' named_entities like "%{}%"'.format(
                entity.replace('+', ' '))
            counter += 1

        result = dbexec('select', query)

        if result['success']:
            content = '<ul class="timeline">'
            for myrow in result['data']:
                human_time = time.strftime(
                    "%d-%m-%Y %H:%M:%S", time.gmtime(int(myrow[3])))

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
                    '{body}': parameters['timespan'],
                    '{url}': myrow[2],
                    '{sentiment_color}': sentiment_color

                })
            content += '</ul>'
        else:
            content = 'There was an error processing your data. <br> Please try again'

        message = parseTemplate(
            'layout2.html', {'{page_content}': content})

        self.wfile.write(message.encode())
        # print(post_data)

        # content_length = int(self.headers['Content-Length'])
        # body = self.rfile.read(content_length)
        # self.send_response(200)
        # self.end_headers()
        # response = BytesIO()
        # response.write(b'This is POST request. ')
        # response.write(b'Received: ')
        # response.write(body)
        # self.wfile.write(response.getvalue())

        return


pages = [
    '/',
    '/dashboard',
    '/stats',
    '/insights',
    '/displayinsights'
]


myServer = HTTPServer(('', 8000), myHandler)
myServer.serve_forever()
