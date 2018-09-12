from . import Operator, LambdaOperator

class CountOperator(Operator):
    def __init__(self, T):
        super(CountOperator, self).__init__(T)

    def visit(self, visitor):
        return visitor.visit_CountOperator(self)

class TakeOperator(Operator):
    def __init__(self, T, limit):
        super(TakeOperator, self).__init__(T)
        self.limit = limit

    def visit(self, visitor):
        return visitor.visit_TakeOperator(self)

class SkipOperator(Operator):
    def __init__(self, T, skip):
        super(SkipOperator, self).__init__(T)
        self.skip = skip

    def visit(self, visitor):
        return visitor.visit_SkipOperator(self)

class MaxOperator(LambdaOperator):
    def __init__(self, T, func):
        super(MaxOperator, self).__init__(T, func)

    def visit(self, visitor):
        return visitor.visit_MaxOperator(self)

class MinOperator(LambdaOperator):
    def __init__(self, T, func):
        super(MinOperator, self).__init__(T, func)

    def visit(self, visitor):
        return visitor.visit_MinOperator(self)

class SumOperator(LambdaOperator):
    def __init__(self, T, func):
        super(SumOperator, self).__init__(T, func)

    def visit(self, visitor):
        return visitor.visit_SumOperator(self)

class AveOperator(LambdaOperator):
    def __init__(self, T, func):
        super(AveOperator, self).__init__(T, func)

    def visit(self, visitor):
        return visitor.visit_AveOperator(self)

class WhereOperator(LambdaOperator):
    def __init__(self, T, func):
        super(WhereOperator, self).__init__(T, func)

    def visit(self, visitor):
        return visitor.visit_WhereOperator(self)

class OrderByOperator(LambdaOperator):
    def __init__(self, T, func):
        super(OrderByOperator, self).__init__(T, func)

    def visit(self, visitor):
        return visitor.visit_OrderByOperator(self)

class ThenByOperator(LambdaOperator):
    def __init__(self, T, func):
        super(ThenByOperator, self).__init__(T, func)

    def visit(self, visitor):
        return visitor.visit_ThenByOperator(self)
