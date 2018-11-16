import abc
from . import Expression


class BinaryExpression(Expression):
    def __init__(self, left_exp, right_exp):
        super(BinaryExpression, self).__init__()
        self.left = left_exp
        self.right = right_exp

    @abc.abstractmethod
    def visit(self, visitor):
        raise NotImplementedError()

    @property
    def children(self):
        return [self.left, self.right]

    def __repr__(self):
        return u"{0}(left={1}, right={3})".format(
            self.__class__.__name__,
            self.left.__repr__(),
            self.right.__repr__())


class JoinExpression(BinaryExpression):
    def __init__(self, outer_exp, inner_exp, outer_key, inner_key, select_func):
        super(JoinExpression, self).__init__(outer_exp, inner_exp)
        self.inner_key = inner_key
        self.outer_key = outer_key
        self.select_func = select_func

    def visit(self, visitor):
        return visitor.visit_JoinExpression(self)

    def __repr__(self):
        return u"JoinExpression(outer={0}, inner={1}, outer_key={2}, inner_key={3}, select={4})".format(
            self.left.__repr__(),
            self.right.__repr__(),
            self.outer_key.__repr__(),
            self.inner_key.__repr__(),
            self.select_func.__repr__()
        )
