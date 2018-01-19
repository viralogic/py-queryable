import abc


class IExpressionVisitor(object):

    def visit(self, expression):
        name = expression.__class__.__name__
        return getattr(self, u"visit_{0}".format(name))(expression)

    @abc.abstractmethod
    def visit_UnaryExpression(self, expression):
        raise NotImplementedError()

    @abc.abstractmethod
    def visit_SelectExpression(self, expression):
        raise NotImplementedError()

    @abc.abstractmethod
    def visit_TableExpression(self, expression):
        raise NotImplementedError()

    @abc.abstractmethod
    def visit_WhereExpression(self, expression):
        raise NotImplementedError()

    @abc.abstractmethod
    def visit_CountExpression(self, expression):
        raise NotImplementedError()

    @abc.abstractmethod
    def visit_TakeExpression(self, expression):
        raise NotImplementedError()

    @abc.abstractmethod
    def visit_SkipExpression(self, expression):
        raise NotImplementedError()




