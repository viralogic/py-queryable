import abc
import ast
from . import Expression, UnaryExpression, TableExpression, LambdaExpression

class LambdaOperator(Expression):
    __class_type__ = None

    def __init__(self, exp, func):
        super(LambdaOperator, self).__init__()
        self.exp = exp
        self.func = func

    @property
    def type(self):
        if self.__class_type__ is None:
            t = self.exp.find(TableExpression)
            if t is None:
                raise Exception("Cannot find TableExpression in {0}".format(self.exp.__repr__()))
            self.__class_type__ = t.type
        return self.__class_type__

    def __repr__(self):
        return u"{0}(T={1}, func={2})".format(
            self.__class__.__name__,
            self.type.__class__.__name__,
            ast.dump(LambdaExpression.parse(self.type, self.func))
        )

class CountOperator(UnaryExpression):
    def __init__(self, exp):
        super(CountOperator, self).__init__(exp)

    def visit(self, visitor):
        return visitor.visit_CountOperator(self)

class TakeOperator(UnaryExpression):
    def __init__(self, exp, limit):
        super(TakeOperator, self).__init__(exp)
        self.limit = limit

    def visit(self, visitor):
        return visitor.visit_TakeOperator(self)

class SkipOperator(UnaryExpression):
    def __init__(self, exp, skip):
        super(SkipOperator, self).__init__(exp)
        self.skip = skip

    def visit(self, visitor):
        return visitor.visit_SkipOperator(self)

class SelectOperator(LambdaOperator):

    def __init__(self, exp, func=None):
        super(SelectOperator, self).__init__(exp, func)

    def visit(self, visitor):
        return visitor.visit_SelectOperator(self)

class MaxOperator(LambdaOperator):
    def __init__(self, exp, func):
        super(MaxOperator, self).__init__(exp, func)

    def visit(self, visitor):
        return visitor.visit_MaxOperator(self)

class MinOperator(LambdaOperator):
    def __init__(self, exp, func):
        super(MinOperator, self).__init__(exp, func)

    def visit(self, visitor):
        return visitor.visit_MinOperator(self)

class SumOperator(LambdaOperator):
    def __init__(self, exp, func):
        super(SumOperator, self).__init__(exp, func)

    def visit(self, visitor):
        return visitor.visit_SumOperator(self)

class AveOperator(LambdaOperator):
    def __init__(self, exp, func):
        super(AveOperator, self).__init__(exp, func)

    def visit(self, visitor):
        return visitor.visit_AveOperator(self)

class WhereOperator(LambdaOperator):
    def __init__(self, exp, func):
        super(WhereOperator, self).__init__(exp, func)

    def visit(self, visitor):
        return visitor.visit_WhereOperator(self)

class OrderByOperator(LambdaOperator):
    def __init__(self, exp, func):
        super(OrderByOperator, self).__init__(exp, func)

    def visit(self, visitor):
        return visitor.visit_OrderByOperator(self)

class ThenByOperator(LambdaOperator):
    def __init__(self, exp, func):
        super(ThenByOperator, self).__init__(exp, func)

    def visit(self, visitor):
        return visitor.visit_ThenByOperator(self)

