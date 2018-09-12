from .unary import OrderByExpression, ThenByExpression

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