import MySQLdb


def dbexec(operation_type, query):

    result = {
        'success': True,
        'data': (),
        'rows_returned': 0,

    }

    if not operation_type in['insert', 'update', 'delete', 'select']:
        result['success'] = False
    else:
        db = MySQLdb.connect("10.0.0.108", "viper", "d9180pa", "articles",)
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
    # try:
    fl = open('webface/templates/' + filename, 'r')
    content = fl.readlines()
    content = ''.join(content)
    fl.close

    placeholders = pagedata.keys()
    for placeholder in placeholders:
        content = content.replace(placeholder, str(pagedata[placeholder]))
    # except:
        # content = 'Error parsing template'

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
    else:
        sources = 'N/A'

    stats['sources'] = sources

    return(stats)
