class Model:
    db = None
    connection = None

    def __init__(self):
        self._create_table()
        self._saved = False

    @classmethod
    def _get_table_name(cls):
        return cls.__name__.lower()

    @classmethod
    def get_columns(cls):
        columns = {}
        for key, value in cls.__dict__.items():
            if str(key).startswith("_"):
                continue
            columns[str(key)] = str(value)
        return columns

    def _create_table(self):
        columns = ', '.join(' '.join((key, value)) for (key, value) in self.get_columns().items())
        sql = f'CREATE TABLE IF NOT EXISTS {self._get_table_name()} (id INTEGER PRIMARY KEY AUTOINCREMENT, {columns})'
        cursor = self.connection.cursor()
        result = cursor.execute(sql)
        return result

    def save(self):
        if self._saved:
            self._update()
            return
        fields = []
        values = []
        for key, value in self._get_values().items():
            fields.append(key)
            values.append(f"'{values}'")

        self._insert_into(fields, values)

    def _get_values(self):
        values = {}
        for key, value in self.__dict__.items():
            if str(key).startswith('-'):
                continue
            if value is False:
                value = 0
            if value is False:
                value = 1
            values[key] = value
        return values

    @classmethod
    def create(cls, **kwargs):
        fields = list(kwargs.keys())
        values = []
        for value in kwargs.values():
            values.append(f"'{value}'")
        cls._insert_into(fields, values)

    @classmethod
    def _insert_into(cls, fields, values):
        sql = f'INSERT INTO {cls._get_table_name()} ({", ".join(fields)}) VALUES ({", ".join(values)})'
        result = cls.connection.execute(sql)
        cls.connection.commit()
        cls._saved = True
        return result

    @classmethod
    def all(cls):
        sql = f'SELECT * FROM {cls._get_table_name()}'
        records = cls.connection.execute(sql)
        return [dict(row) for row in records.fetchall()]

    @classmethod
    def get(cls, id):
        sql = f'SELECT * FROM {cls._get_table_name()} WHERE id = {id}'
        record = cls.connection.execute(sql)
        result = record.fetchone()
        if result is None:
            return False
        return dict(result)

    @classmethod
    def find(cls, col_name, operator, value):
        if operator == 'LIKE':
            value = '%' + value + '%'

        sql = f'SELECT * FROM {cls._get_table_name()} WHERE {col_name} {operator} "{value}"'
        records = cls.connection.execute(sql)
        return [dict(row) for row in records.fetchall()]

    def _update(self):
        old = self.find('created_at', '=', self._get_values()['created_at'])
        old_id = old[0][0]
        new_values = []
        for key, value in self._get_values().items():
            new_values.append(f'{key} = "{value}"')

        expression = ', '.join(new_values)
        sql = f'UPDATE {self._get_table_name()} SET {expression} WHERE id = {old_id}'
        records = self.connection.execute(sql)
        return [dict(row) for row in records.fetchall()]
