__author__ = 'ViraLogic Software'

import abc


class ProviderConfig(object):
    """
    Class that holds parameters for database connection provider
    """
    def __init__(self, host, user, password, db_uri):
        self.host = host
        self.user = user
        self.password = password
        self.db_uri = db_uri


class UriParserBase(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, connection_uri):
        """
        Constructor
        :param connection_uri: uri for database, similar in form to sqlalchemy
        (http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html)
        :return: void
        """
        self.connection_uri = connection_uri

    @abc.abstractmethod
    def parse_uri(self):
        """
        Parses the connection uri to set host, user, password, and database uri
        :return: return ProviderConfig instance
        """
        raise NotImplementedError()


class SqliteUriParser(UriParserBase):
    """
    Implementation of UriParserBase for Sqlite
    """
    def parse_uri(self):
        return ProviderConfig(u'', u'', u'', self.connection_uri.split(':')[1])




