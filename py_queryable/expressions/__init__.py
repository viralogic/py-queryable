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
        translator = SqlLambdaTranslator(T)
        translator.generic_visit(tree)
        return tree


class Expression(object):
    __class_type__ = None

    def __init__(self, T):
        if not hasattr(T, u"__table_name__"):
            raise AttributeError(u"{0} does not appear to be derived from Model".format(T.__class__.__name__))
        self.__class_type__ = T
        self.visited = False

    def __eq__(self, other):
        return self.type == other.type and self.__repr__() == other.__repr__()

    @property
    def type(self):
        return self.__class_type__

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
        q = deque(self.children)
        while len(q) > 0:
            node = q.popleft()
            if type(node) == expression:
                return node
            for n in node.children:
                q.append(n)
        return None


class UnaryExpression(Expression):
    def __init__(self, T, op_exp, exp):
        super(UnaryExpression, self).__init__(T)
        self.op = op_exp
        self.exp = exp

    def visit(self, visitor):
        return visitor.visit_UnaryExpression(self)

    @property
    def children(self):
        return [self.op, self.exp]

    def __repr__(self):
        return u"{0}(op={1}, exp={2})".format(self.__class__.__name__, self.op.__repr__(), self.exp.__repr__())

class BinaryExpression(object):
    def __init__(self, left_exp, op_exp, right_exp):
        self.left = left_exp
        self.op = op_exp
        self.right = right_exp

    def visit(self, visitor):
        return visitor.visit_BinaryExpression(self)

    @property
    def children(self):
        return [self.left, self.op, self.right]

    def __repr__(self):
        return u"{0}(left={1}, op={2}, right={3})".format(
            self.__class__.__name__,
            self.left.__repr__(),
            self.op.__repr__(),
            self.right.__repr__())


class SelectExpression(Expression):

    def __init__(self, T, func=None):
        super(SelectExpression, self).__init__(T)
        self.func = func

    def visit(self, visitor):
        return visitor.visit_SelectExpression(self)

    @property
    def children(self):
        return []

    def __repr__(self):
        t = LambdaExpression.parse(self.type, self.func)
        return u"Select(func={0})".format(ast.dump(t))


class TableExpression(Expression):

    def __init__(self, T):
        super(TableExpression, self).__init__(T)

    def visit(self, visitor):
        return visitor.visit_TableExpression(self)

    @property
    def children(self):
        return []

    def __repr__(self):
        return u"Table(table_name={0})".format(self.type.table_name)


class Operator(Expression):
    def __init__(self, T):
        super(Operator, self).__init__(T)

    @abc.abstractmethod
    def visit(self, visitor):
        return NotImplementedError()

    @property
    def children(self):
        return []

    def __repr__(self):
        return u"{0}(T={1})".format(self.__class__.__name__, self.type.__class__.__name__)

class LambdaOperator(Operator):
    def __init__(self, T, func):
        super(LambdaOperator, self).__init__(T)
        self.func = func

    @abc.abstractmethod
    def visit(self, visitor):
        return NotImplementedError()

    def __repr__(self):
        return u"{0}(T={1}, func={2})".format(
            self.__class__.__name__,
            self.type.__class__.__name__,
            ast.dump(LambdaExpression.parse(self.type, self.func))
        )