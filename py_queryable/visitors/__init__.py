class Visitor(object):
    def visit(self, expression):
        return expression.visit(self)
