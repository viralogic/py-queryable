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


class CountOperator(Operator):
    def __init__(self, T):
        super(CountOperator, self).__init__(T)

    def visit(self, visitor):
        return visitor.visit_CountOperator(self)


class CountExpression(UnaryExpression):

    def __init__(self, T, exp):
        super(CountExpression, self).__init__(T, CountOperator(T), exp)

    def visit(self, visitor):
        return visitor.visit_CountExpression(self)


class TakeOperator(Operator):
    def __init__(self, T, limit):
        super(TakeOperator, self).__init__(T)
        self.limit = limit

    def visit(self, visitor):
        return visitor.visit_TakeOperator(self)


class TakeExpression(UnaryExpression):
    def __init__(self, T, exp, limit):
        super(TakeExpression, self).__init__(T, TakeOperator(T, limit), exp)

    def visit(self, visitor):
        return visitor.visit_TakeExpression(self)


class SkipOperator(Operator):
    def __init__(self, T, skip):
        super(SkipOperator, self).__init__(T)
        self.skip = skip

    def visit(self, visitor):
        return visitor.visit_SkipOperator(self)


class SkipExpression(UnaryExpression):
    def __init__(self, T, exp, skip):
        super(SkipExpression, self).__init__(T, SkipOperator(T, skip), exp)

    def visit(self, visitor):
        return visitor.visit_SkipExpression(self)


class MaxOperator(Operator):
    def __init__(self, T, func):
        super(MaxOperator, self).__init__(T)
        self.func = func

    def visit(self, visitor):
        return visitor.visit_MaxOperator(self)

    def __repr__(self):
        return u"MaxOp(T={0}, func={1})".format(
            self.type.__class__.__name__,
            ast.dump(LambdaExpression.parse(self.type, self.func))
        )


class MinOperator(Operator):
    def __init__(self, T, func):
        super(MinOperator, self).__init__(T)
        self.func = func

    def visit(self, visitor):
        return visitor.visit_MinOperator(self)

    def __repr__(self):
        return u"MinOp(T={0}, func={1})".format(
            self.type.__class__.__name__,
            ast.dump(LambdaExpression.parse(self.type, self.func))
        )


class MaxExpression(UnaryExpression):
    def __init__(self, T, exp, func=None):
        if func is None:
            select = exp.find(SelectExpression)
            if select is None or select.func is None:
                raise AttributeError(
                    u"Max expression with no lambda function must be preceded by a select with a lambda expression"
                )
            func = select.func
        super(MaxExpression, self).__init__(
            T,
            MaxOperator(T, func),
            exp
        )

    def visit(self, visitor):
        return visitor.visit_MaxExpression(self)

    def __repr__(self):
        return u"Max(T={0}, op={1}, exp={2})".format(
            self.type.__class__.__name__,
            self.op.__repr__(),
            self.exp.__repr__()
        )

class MinExpression(UnaryExpression):
    def __init__(self, T, exp, func=None):
        if func is None:
            select = exp.find(SelectExpression)
            if select is None or select.func is None:
                raise AttributeError(
                    u"Min expression with no lambda function must be preceded by a select with a lambda expression"
                )
            func = select.func
        super(MinExpression, self).__init__(
            T,
            MinOperator(T, func),
            exp
        )

    def visit(self, visitor):
        return visitor.visit_MinExpression(self)

    def __repr__(self):
        return u"Min(T={0}, op={1}, exp={2}".format(
            self.type.__class__.__name__,
            self.op.__repr__(),
            self.exp.__repr__()
        )

class WhereOperator(Operator):
    def __init__(self, T, func):
        super(WhereOperator, self).__init__(T)
        self.func = func

    def visit(self, visitor):
        return visitor.visit_WhereOperator(self)

    def __repr__(self):
        return u"WhereOperator(T={0}, func={1})".format(
            self.type.__class__.__name__,
            ast.dump(LambdaExpression.parse(self.type, self.func))
        )


class WhereExpression(UnaryExpression):
    def __init__(self, T, func, exp):
        super(WhereExpression, self).__init__(T, WhereOperator(T, func), exp)

    def visit(self, visitor):
        return visitor.visit_WhereExpression(self)

    def __repr__(self):
        return u"Where(T={0}, op={1}, exp={2})".format(
            self.type.__class__.__name__,
            self.op.__repr__(),
            self.exp.__repr__()
        )


class OrderByOperator(Operator):
    def __init__(self, T, func):
        super(OrderByOperator, self).__init__(T)
        self.func = func

    def visit(self, visitor):
        return visitor.visit_OrderByOperator(self)

    def __repr__(self):
        return u"OrderByOperator(T={0}, func={1})".format(
            self.type.__class__.name,
            ast.dump(LambdaExpression.parse(self.type, self.func))
        )


class ThenByOperator(Operator):
    def __init__(self, T, func):
        super(ThenByOperator, self).__init__(T)
        self.func = func

    def visit(self, visitor):
        return visitor.visit_ThenByOperator(self)

    def __repr__(self):
        return u"ThenByOperator(T={0}, func={1})".format(
            self.type.__class__.name,
            ast.dump(LambdaExpression.parse(self.type, self.func))
        )


class OrderByExpression(UnaryExpression):
    def __init__(self, T, func, exp):
        super(OrderByExpression, self).__init__(
            T,
            OrderByOperator(T, func),
            exp
        )

    def visit(self, visitor):
        return visitor.visit_OrderByExpression(self)

    def __repr__(self):
        return u"OrderBy(T={0}, op={1}, exp={2})".format(
            self.type.__class__.name,
            self.op.__repr__(),
            self.exp.__repr__()
        )


class ThenByExpression(UnaryExpression):
    def __init__(self, T, func, exp):
        super(ThenByExpression, self).__init__(
            T,
            ThenByOperator(T, func),
            exp
        )

    def visit(self, visitor):
        return visitor.visit_ThenByExpression(self)

    def __repr__(self):
        return u"ThenBy(T={0}, op={1}, exp={2})".format(
            self.type.__class__.name,
            self.op.__repr__(),
            self.exp.__repr__()
        )


class OrderByDescendingExpression(OrderByExpression):
    def __init__(self, T, func, exp):
        super(OrderByDescendingExpression, self).__init__(T, func, exp)

    def visit(self, visitor):
        return visitor.visit_OrderByDescendingExpression(self)

    def __repr__(self):
        return u"OrderByDescending(T={0}, op={1}, exp={2})".format(
            self.type.__class__.name,
            self.op.__repr__(),
            self.exp.__repr__()
        )


class ThenByDescendingExpression(ThenByExpression):
    def __init__(self, T, func, exp):
        super(ThenByDescendingExpression, self).__init__(T, func, exp)

    def visit(self, visitor):
        return visitor.visit_ThenByDescendingExpression(self)

    def __repr__(self):
        return u"ThenByDescending(T={0}, op={1}, exp={2})".format(
            self.type.__class__.name,
            self.op.__repr__(),
            self.exp.__repr__()
        )
