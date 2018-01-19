__author__ = 'Bruce.Fenske'

import inspect
from .column_types import Column
from ..exceptions import InvalidArgumentError


class ColumnProxy(object):
    def __init__(self, column, value):
        if not isinstance(column, Column):
            raise InvalidArgumentError(u"column argument is not an instance of Column")
        self._column = column
        self._value = value

    @property
    def column(self):
        return self._column

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if type(value) != self.column.column_type:
            raise InvalidArgumentError(
                u"{0} does not equal {1}:{2}".format(value, self.column.column_type, self.column.column_name)
            )
        self._value = value

    def value_for_sql(self):
        if self.column.column_type == unicode:
            return u"'{0}'".format(self.value)
        return self.value


class DynamicModelProxy(object):
    _column_proxies = {}

    def __init__(self, model):
        """
        Instantiates a proxy class of a given model. This proxy class auto-adds attributes from the model and
        instantiates a column proxy object for each attribute. The value for each attribute is set as well.
        :param model: A child class of a py_queryable.entity.model.Model
        :return:
        """
        self._model = model
        self._column_proxies = {}
        self._add_model_columns()

    def __setattr__(self, key, value):
        if key in self.columns:
            self.columns[key].value = value
        super(DynamicModelProxy, self).__setattr__(key, value)

    @staticmethod
    def create_proxy_from_model_instance(instance):
        """
        Creates a proxy model from an data model instance
        :param instance: an instance of a py_queryable.entity.model class
        :return: DynamicModelProxy instance
        """
        proxy = DynamicModelProxy(instance.__class__)
        for k, v in proxy.columns.iteritems():
            if k in instance.__dict__:
                proxy.__setattr__(k, instance.__dict__[k])
        return proxy

    @property
    def model(self):
        return self._model

    @property
    def columns(self):
        return self._column_proxies

    def _add_model_columns(self):
        columns = [
            (unicode(name), col) for name, col in inspect.getmembers(self.model)
            if isinstance(col, Column)
        ]
        for name, col in columns:
            proxy = ColumnProxy(col, None)
            self.columns.setdefault(name, proxy)
            self.__dict__.setdefault(name, proxy.value)

    def column_name(self, key):
        try:
            column_proxy = self.columns[key]
        except KeyError:
            raise InvalidArgumentError(u"No such column with key of {0}".format(key))
        return column_proxy.column.column_name if column_proxy.column.column_name else key

    @property
    def primary_key(self):
        primary_key = filter(lambda x: x[1].column.is_primary_key, self.columns.iteritems())
        if len(primary_key) == 0:
            return None
        if len(primary_key) > 1:
            raise InvalidArgumentError(
                u"There can only be 1 primary key associated with {0}".format(self.model.table_name())
            )
        return primary_key

    @property
    def primary_key_name(self):
        return None if self.primary_key is None else self.column_name(self.primary_key[0][0])

    @property
    def primary_key_value(self):
        return None if self.primary_key is None else self.primary_key[0][1].value
