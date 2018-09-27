import abc
import ast
from . import Expression, UnaryExpression, TableExpression, LambdaExpression

class LambdaOperator(Expression):
    def __init__(self, exp, func):
        super(LambdaOperator, self).__init__()
        self.exp = exp
        self.func = func
        self.class_type = None

    @property
    def children(self):
        return [self.exp]

    @property
    def type(self):
        if self.class_type is None:
            t = self.find(TableExpression)
            if t is None:
                raise Exception("Cannot find TableExpression in {0}".format(self.exp.__repr__()))
            self.class_type = t.type
        return self.class_type

    def __repr__(self):
        return u"{0}(T={1}, func={2})".format(
            self.__class__.__name__,
            self.type.__class__.__name__,
            ast.dump(LambdaExpression.parse(self.type, self.func))
        )

class SelectOperator(LambdaOperator):
    def __init__(self, exp, func=None):
        super(SelectOperator, self).__init__(exp, func)

    def visit(self, visitor):
        return visitor.visit_SelectOperator(self)

class WhereOperator(LambdaOperator):
    def __init__(self, exp, func):
        super(WhereOperator, self).__init__(exp, func)

    def visit(self, visitor):
        return visitor.visit_WhereOperator(self)

class AliasOperator(UnaryExpression):
    def __init__(self, alias, exp):
        super(AliasOperator, self).__init__(exp)
        self.alias = alias

    def visit(self, visitor):
        return visitor.visit_AliasOperator(self)

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

class MaxOperator(LambdaOperator):
    def __init__(self, exp, func=None):
        super(MaxOperator, self).__init__(exp, func)

    def visit(self, visitor):
        return visitor.visit_MaxOperator(self)

class MinOperator(LambdaOperator):
    def __init__(self, exp, func=None):
        super(MinOperator, self).__init__(exp, func)

    def visit(self, visitor):
        return visitor.visit_MinOperator(self)

class SumOperator(LambdaOperator):
    def __init__(self, exp, func=None):
        super(SumOperator, self).__init__(exp, func)

    def visit(self, visitor):
        return visitor.visit_SumOperator(self)

class AveOperator(LambdaOperator):
    def __init__(self, exp, func=None):
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

class OrderByDescendingOperator(LambdaOperator):
    def __init__(self, exp, func=None):
        super(OrderByDescendingOperator, self).__init__(exp, func)

    def visit(self, visitor):
        return visitor.visit_OrderByDescendingOperator(self)

class ThenByOperator(LambdaOperator):
    def __init__(self, exp, func):
        super(ThenByOperator, self).__init__(exp, func)

    def visit(self, visitor):
        return visitor.visit_ThenByOperator(self)

