from . import Expression


class BinaryExpression(Expression):
    def __init__(self, left_exp, op_exp, right_exp):
        super(BinaryExpression, self).__init__()
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
