from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
from aux import dbexec, parseTemplate, getStats


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

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # content = content.replace('\n', "<BR>")
            # template = loadFile('/var/www/parser/template.html')
            message = parseTemplate(
                'layout1.html', {'{page_content}': content})
            # message = template.replace('{content}', content)
            self.wfile.write(message.encode())

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # Send the html message
            message = 'The page you are looking for does not exist'
            self.wfile.write(message.encode())

        return


pages = [
    '/',
    '/dashboard',
    '/stats',
    '/insights'
]


myServer = HTTPServer(('', 8000), myHandler)
myServer.serve_forever()
