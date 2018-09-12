from . import UnaryExpression, SelectExpression
from . import operators

class CountExpression(UnaryExpression):

    def __init__(self, T, exp):
        super(CountExpression, self).__init__(T, operators.CountOperator(T), exp)

    def visit(self, visitor):
        return visitor.visit_CountExpression(self)

class TakeExpression(UnaryExpression):
    def __init__(self, T, exp, limit):
        super(TakeExpression, self).__init__(T, operators.TakeOperator(T, limit), exp)

    def visit(self, visitor):
        return visitor.visit_TakeExpression(self)

class SkipExpression(UnaryExpression):
    def __init__(self, T, exp, skip):
        super(SkipExpression, self).__init__(T, operators.SkipOperator(T, skip), exp)

    def visit(self, visitor):
        return visitor.visit_SkipExpression(self)

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
            operators.MaxOperator(T, func),
            exp.exp
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
            operators.MinOperator(T, func),
            exp.exp
        )

    def visit(self, visitor):
        return visitor.visit_MinExpression(self)

    def __repr__(self):
        return u"Min(T={0}, op={1}, exp={2}".format(
            self.type.__class__.__name__,
            self.op.__repr__(),
            self.exp.__repr__()
        )

class WhereExpression(UnaryExpression):
    def __init__(self, T, func, exp):
        super(WhereExpression, self).__init__(T, operators.WhereOperator(T, func), exp)

    def visit(self, visitor):
        return visitor.visit_WhereExpression(self)

    def __repr__(self):
        return u"Where(T={0}, op={1}, exp={2})".format(
            self.type.__class__.__name__,
            self.op.__repr__(),
            self.exp.__repr__()
        )

class OrderByExpression(UnaryExpression):
    def __init__(self, T, func, exp):
        super(OrderByExpression, self).__init__(
            T,
            operators.OrderByOperator(T, func),
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
            operators.ThenByOperator(T, func),
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
