from ..expressions import LambdaExpression
from ..expressions import operators
from ..expressions import unary
from ..expressions import sort
from ..entity.proxy import DynamicModelProxy
from py_linq import Enumerable
from py_linq.exceptions import NoElementsError, NoMatchingElement, MoreThanOneMatchingElement


class Queryable(object):
    __class_type__ = None

    def __init__(self, expression, query_provider):
        self.__exp = expression
        self.__provider = query_provider

    def __iter__(self):
        # Get type determined by select expression
        select = self.expression.find(SelectExpression)
        if select is None:
            raise Exception(u"Queryable expression does not contain a SelectExpression")
        num_cols = len(self.type.inspect_columns())
        result_type = self.type if select.func is None else LambdaExpression.parse(self.type, select.func).body.type

        cursor = self.provider.db_provider.connection.cursor()
        cursor.execute(self.sql)
        for r in cursor:
            # if returning just one column
            if len(r) == 1:
                yield r[0]
            # if returning more than one column
            else:
                if result_type == type(list):
                    yield Enumerable(r).select(lambda x: x[0]).to_list()
                elif result_type == type(tuple):
                    yield tuple(Enumerable(r).select(lambda x: x[0]).to_list())
                elif result_type == type(dict):
                    result = {}
                    for i in range(0, len(r), 1):
                        result.__setattr__(cursor.description[i][0], r[i])
                    yield result
                elif result_type == self.type and len(r) == num_cols:
                    proxy = DynamicModelProxy(self.type)
                    for i in range(0, len(r), 1):
                        proxy.__setattr__(cursor.description[i][0], r[i])
                    yield proxy
                else:
                    raise Exception(
                        u"""Casting not supported.
                        Please consider using a tuple or dict or list in lambda expression of select"""
                    )

    @property
    def provider(self):
        return self.__provider

    @property
    def type(self):
        return self.expression.type

    @property
    def expression(self):
        return self.__exp

    @property
    def sql(self):
        return self.provider.provider_visitor.visit(self.expression)

    def select(self, func):
        return Queryable(UnaryExpression(self.type, SelectExpression(self.type, func), self.expression), self.provider)

    def count(self):
        query = Queryable(unary.CountExpression(self.type, self.expression), self.provider)
        return self.provider.db_provider.execute_scalar(query.sql)

    def take(self, limit):
        if isinstance(self.__exp, unary.SkipExpression):
            self.expression.exp.op.limit = limit
            return self
        else:
            return Queryable(unary.TakeExpression(self.type, self.expression, limit), self.provider)

    def skip(self, offset):
        if not isinstance(self.expression, unary.TakeExpression):
            self.__exp = unary.TakeExpression(self.type, self.expression, -1)
        return Queryable(unary.SkipExpression(self.type, self.expression, offset), self.provider)

    def max(self, func=None):
        query = Queryable(unary.MaxExpression(self.type, self.expression, func), self.provider)
        return self.provider.db_provider.execute_scalar(query.sql)

    def min(self, func=None):
        query = Queryable(unary.MinExpression(self.type, self.expression, func), self.provider)
        return self.provider.db_provider.execute_scalar(query.sql)

    def sum(self, func=None):
        query = Queryable(unary.SumExpression(self.type, self.expression, func), self.provider)
        return self.provider.db_provider.execute_scalar(query.sql)

    def average(self, func=None):
        query = Queryable(unary.AvgExpression(self.type, self.expression, func), self.provider)
        return self.provider.db_provider.execute_scalar(query.sql)

    def any(self, func=None):
        return self.count() > 0 if func is None else self.where(func).count() > 0
    
    def all(self, func=None):
        if func is None:
            return True
        count = self.count()
        return self.where(func).count() == count

    def first(self):
        return self.take(1).as_enumerable().first()

    def first_or_default(self):
        try:
            return self.first()
        except NoElementsError:
            return None

    def order_by(self, func):
        return OrderedQueryable(
            unary.OrderByExpression(self.type, func, self.expression),
            self.provider
        )

    def order_by_descending(self, func):
        return OrderedQueryable(
            sort.OrderByDescendingExpression(self.type, func, self.expression),
            self.provider
        )

    def where(self, func):
        return Queryable(
            unary.WhereExpression(self.type, func, self.expression), self.provider)

    def single(self, func=None):
        result = self.where(func).to_list() if func is not None else self.to_list()
        count = len(result)
        if count == 0:
            raise NoMatchingElement(u"No matching elements could be found")
        if count > 1:
            raise MoreThanOneMatchingElement(u"More than one matching element found")
        return result[0]

    def single_or_default(self, func=None):
        try:
            return self.single(func)
        except NoMatchingElement:
            return None

    def as_enumerable(self):
        return Enumerable(self)

    def to_list(self):
        return self.as_enumerable().to_list()


class OrderedQueryable(Queryable):
    def __init__(self, expression, query_provider):
        super(OrderedQueryable, self).__init__(expression, query_provider)

    def then_by(self, func):
        return OrderedQueryable(
            unary.ThenByExpression(self.type, func, self.expression),
            self.provider
        )

    def then_by_descending(self, func):
        return OrderedQueryable(
            sort.ThenByDescendingExpression(self.type, func, self.expression),
            self.provider
        )
