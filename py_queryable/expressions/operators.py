from . import Operator

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
