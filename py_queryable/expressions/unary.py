from . import UnaryExpression
from . import operators

class CountExpression(UnaryExpression):

    def __init__(self, exp):
        super(CountExpression, self).__init__(exp)

    def visit(self, visitor):
        return visitor.visit_CountExpression(self)

class TakeExpression(UnaryExpression):
    def __init__(self, exp):
        super(TakeExpression, self).__init__(exp)

    def visit(self, visitor):
        return visitor.visit_TakeExpression(self)

class SkipExpression(UnaryExpression):
    def __init__(self, exp):
        super(SkipExpression, self).__init__(exp)

    def visit(self, visitor):
        return visitor.visit_SkipExpression(self)

class MaxExpression(UnaryExpression):
    def __init__(self, exp):
        if func is None:
            select = exp.find(SelectExpression)
            if select is None or select.func is None:
                raise AttributeError(
                    u"Max expression with no lambda function must be preceded by a select with a lambda expression"
                )
            func = select.func
        super(MaxExpression, self).__init__(exp)

    def visit(self, visitor):
        return visitor.visit_MaxExpression(self)

class MinExpression(UnaryExpression):
    def __init__(self, exp):
        if func is None:
            select = exp.find(SelectExpression)
            if select is None or select.func is None:
                raise AttributeError(
                    u"Min expression with no lambda function must be preceded by a select with a lambda expression"
                )
            func = select.func
        super(MinExpression, self).__init__(exp)

    def visit(self, visitor):
        return visitor.visit_MinExpression(self)

class SumExpression(UnaryExpression):
    def __init__(self, exp):
        if func is None:
            select = exp.find(SelectExpression)
            if select is None or select.func is None:
                raise AttributeError(
                    u"Sum expression with no lambda function must be preceded by a select with a lambda expression"
                )
            func = select.func
        super(SumExpression, self).__init__(exp)

    def visit(self, visitor):
        return visitor.visit_SumExpression(self)

class AvgExpression(UnaryExpression):
    def __init__(self, exp):
        if func is None:
            select = exp.find(SelectExpression)
            if select is None or select.func is None:
                raise AttributeError(
                    u"Average expression with no lambda function must be preceded by a select with a lambda expression"
                )
            func = select.func
        super(AvgExpression, self).__init__(operators.AveOperator(exp.exp, func))
    
    def visit(self, visitor):
        return visitor.visit_AvgExpression(self)

class WhereExpression(UnaryExpression):
    def __init__(self, exp):
        super(WhereExpression, self).__init__(exp)

    def visit(self, visitor):
        return visitor.visit_WhereExpression(self)

class OrderByExpression(UnaryExpression):
    def __init__(self, exp):
        super(OrderByExpression, self).__init__(exp)

    def visit(self, visitor):
        return visitor.visit_OrderByExpression(self)

class ThenByExpression(UnaryExpression):
    def __init__(self, exp):
        super(ThenByExpression, self).__init__(exp)

    def visit(self, visitor):
        return visitor.visit_ThenByExpression(self)
