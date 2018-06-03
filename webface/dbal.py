import MySQLdb


class dbresult(object):

    def __init__(self):
        self.success = True
        self.data = ()
        self.rows_affected = 0
        self.info = '--'
        self.last_id = 0

    def summary(self):
        summary = ''
        summary += 'Success : {}\n'.format(self.success)
        summary += 'Rows Affected : {}\n'.format(self.rows_affected)
        summary += 'Info :{}\n'.format(self.info)
        summary += 'Last Id : {}\n'.format(self.last_id)

        return summary


class dbal(object):
    ''' Configuration object is a dict :
    conf = {
        'host' : '',
        'username' : '',
        'password' : '',
        'database' : '',
        'charset' : ''
    }
'''

    def __init__(self, configuration):
        self.host = configuration['host']
        self.username = configuration['username']
        self.password = configuration['password']
        self.database = configuration['database']
        self.charset = configuration['charset']
        self.db = None

    def test(self):
        result = True
        try:
            self.db = MySQLdb.connect(self.host, self.username,
                                      self.password, self.database)
            self.db.set_character_set(self.charset)
        except:
            result = False

        self.db.close()
        return result

    def _connect(self):
        self.db = MySQLdb.connect(self.host, self.username,
                                  self.password, self.database)
        self.db.set_character_set(self.charset)
        self.cursor = self.db.cursor()

    def _close(self):
        self.db.close()

    def select(self, query):

        dbres = dbresult()

        try:
            self._connect()
            self.cursor.execute(query)
            dbres.data = self.cursor.fetchall()
            dbres.rows_affected = self.cursor.rowcount
            self._close()
        except (self.db.Error, self.db.Warning) as e:
            dbres.success = False
            dbres.info = str(e)

        return dbres

    def insert(self, params):
        # This function requires a list of parameters in the form of :
        #    params = {
        #        'field_names' : list of field names of table,
        #        'field_values' : list of values respectively
        #        'table_name' : name of the table
        #    }

        dbres = dbresult()

        if len(params['field_names']) != len(params['field_values']):
            dbres.success = False
            dbres.info = 'Fields and values do not match'
            return dbres

        try:
            fields = ','.join(params['field_names'])

            value_slots = ''
            for slt in range(0, len(params['field_values'])):
                value_slots += '%s,'
                slt = slt

            query = '''insert into {} ({}) values ({})'''.format(
                params['table_name'], fields, value_slots[:-1])

            self._connect()
            self.cursor.execute(query, params['field_values'])
            self.db.commit()

            dbres.rows_affected = self.cursor.rowcount
            dbres.last_id = self.cursor.lastrowid

            self._close()

        except (self.db.Error, self.db.Warning) as e:
            dbres.success = False
            dbres.info = str(e)

        return dbres

    def update(self, params):
        # This function requires a list of parameters in the form of :
        #    params = {
        #        'field_names' : list of field names of table,
        #        'field_values' : list of values respectively
        #        'table_name' : name of the table
        #        'conditions' : conditions
        #    }

        dbres = dbresult()

        if len(params['field_names']) != len(params['field_values']):
            dbres.success = False
            dbres.info = 'Fields and values do not match'
            return dbres

        try:

            valstr = ' '
            for val in params['field_names']:
                valstr += '{}=%s,'.format(val)

            query = '''update {} set {} where {}'''.format(
                params['table_name'], valstr[:-1], params['conditions'])

            self._connect()
            self.cursor.execute(query, params['field_values'])
            self.db.commit()

            dbres.rows_affected = self.cursor.rowcount

            self._close()

        except (self.db.Error, self.db.Warning) as e:
            dbres.success = False
            dbres.info = str(e)

        return dbres

    def delete(self, params):
        # This function requires a list of parameters in the form of :
        #    params = {
        #        'table_name' : name of the table
        #        'conditions' : conditions
        #    }

        dbres = dbresult()

        try:
            query = 'delete from {} where {}'.format(
                params['table_name'], params['conditions'])
            self._connect()
            self.cursor.execute(query)
            self.db.commit()
            dbres.rows_affected = self.cursor.rowcount
            self._close()

        except (self.db.Error, self.db.Warning) as e:
            dbres.success = False
            dbres.info = str(e)

        return dbres
