from py_linq import Enumerable
from ..exceptions import InvalidArgumentError


class Column(object):

    def __init__(
            self,
            column_type,
            column_name=None,
            foreign_key=None,
            is_primary_key=False,
            is_nullable=True,
            is_unique=False
    ):
        self._column_name = unicode(column_name) if column_name is not None else None
        self._column_type = column_type
        self._foreign_key = foreign_key
        self._is_primary_key = is_primary_key
        self._is_nullable = is_nullable
        self._is_unique = is_unique

    @property
    def column_type(self):
        return self._column_type

    @property
    def column_name(self):
        if self._column_name is None or self._column_name == u'' or len(self._column_name) == 0:
            return None
        return self._column_name

    @property
    def foreign_key(self):
        return self._foreign_key

    @property
    def is_primary_key(self):
        return self._is_primary_key

    @property
    def is_nullable(self):
        return self._is_nullable

    @property
    def is_unique(self):
        return self._is_unique


class PrimaryKey(Column):
    def __init__(self, column_type, column_name=None):
        super(PrimaryKey, self).__init__(
            column_type,
            column_name,
            foreign_key=None,
            is_primary_key=True,
            is_nullable=False,
            is_unique=False
        )


class ForeignKey(Column):
    def __init__(self, model, column_name=None, is_nullable=True, is_unique=False):
        pk_column = Enumerable(model.inspect_columns()).single_or_default(lambda c: c[1].is_primary_key)
        if pk_column is None:
            raise InvalidArgumentError(u"No primary key found for {0}".format(model.table_name()))
        self._pk_column = pk_column[1]
        super(ForeignKey, self).__init__(
            self._pk_column.column_type,
            column_name, foreign_key=model,
            is_primary_key=False,
            is_nullable=is_nullable,
            is_unique=is_unique
        )

    @property
    def foreign_column(self):
        return self._pk_column
