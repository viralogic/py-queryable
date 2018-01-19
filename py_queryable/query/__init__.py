import abc


class IQueryable(object):
    """
    Interface to implement IQueryable. Container to hold expression and provider
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def expression(self):
        """
        Expression tree associated with the instance of IQueryable
        :return: Expression tree associated with IQueryable instance
        """
        return NotImplementedError()

    @abc.abstractproperty
    def provider(self):
        """
        Query provider associated with the data source/data base
        :return: IQueryProvider instance
        """
        return NotImplementedError()
