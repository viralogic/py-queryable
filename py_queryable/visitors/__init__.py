class Visitor(object):
    def visit(self, expression):
        name = expression.__class__.__name__
        return getattr(self, u"visit_{0}".format(name))(expression)





