import abc
import meta
import ast
from collections import deque
from ..visitors.lambda_visitors import SqlLambdaTranslator


class LambdaExpression(object):

    """
    Parses a python lambda expression and returns a modified tree that contains
    appropriate sql syntax
    """
    @staticmethod
    def parse(T, func):
        tree = meta.decompiler.decompile_func(func)
        translator = SqlLambdaTranslator()
        translator.generic_visit(tree)
        return tree


class Expression(object):
    def __init__(self):
        self.visited = False
        self.class_type = None

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()

    @property
    def type(self):
        if self.class_type is None:
            t = self.find(TableExpression)
            if t is None:
                raise Exception("Cannot find TableExpression in {0}".format(self.exp.__repr__()))
            self.class_type = t.type
        return self.class_type

    @abc.abstractmethod
    def visit(self, visitor):
        raise NotImplementedError()

    @abc.abstractproperty
    def children(self):
        raise NotImplementedError()

    def find(self, expression):
        """
        Finds first matching expression using breadth first search
        :param expression: An expression type
        :return: First expression that matches given expression else None
        """
        if isinstance(self, expression):
            return expression
        q = deque(self.children)
        while len(q) > 0:
            node = q.popleft()
            if isinstance(node, expression):
                return node
            for n in node.children:
                q.append(n)
        return None


class TableExpression(Expression):
    def __init__(self, T):
        super(TableExpression, self).__init__()
        if not hasattr(T, u"__table_name__"):
            raise AttributeError(u"{0} does not appear to be derived from Model".format(T.__class__.__name__))
        self.class_type = T

    def visit(self, visitor):
        return visitor.visit_TableExpression(self)

    @property
    def children(self):
        return []

    def __repr__(self):
        return u"Table(table_name={0})".format(self.type.table_name)


class UnaryExpression(Expression):
    def __init__(self, exp):
        super(UnaryExpression, self).__init__()
        self.exp = exp

    def visit(self, visitor):
        return visitor.visit(self)

    @property
    def children(self):
        return [self.exp]

    def __repr__(self):
        return u"{0}(exp={1})".format(self.__class__.__name__, self.exp.__repr__())
