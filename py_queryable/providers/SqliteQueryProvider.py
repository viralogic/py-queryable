from ..query.Queryable import Queryable
from ..providers import IQueryProvider
from ..visitors.sql import SqlVisitor


class SqliteQueryProvider(IQueryProvider):

    def __init__(self, db_provider):
        self.__provider = db_provider
        self.__visitor = SqlVisitor()

    @property
    def db_provider(self):
        return self.__provider

    @property
    def provider_visitor(self):
        return self.__visitor

    def createQuery(self, expression):
        """
        Create Queryable instance from given expression
        :param expression: An AST expression instance
        :return: Queryable
        """
        return Queryable(expression, self)

    def execute(self, expression):
        """
        Executes the SQL using the instance's db_provider
        :param expression: An AST expression instance
        :return: db_provider cursor object
        """
        cursor = self.db_provider.connection.cursor()
        queryable = self.createQuery(expression)
        cursor.execute(queryable.sql)
        return cursor
