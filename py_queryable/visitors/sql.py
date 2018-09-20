import ast
from py_linq import Enumerable
from ..expressions import LambdaExpression
from ..expressions.unary import SelectExpression
from . import Visitor


class SqlVisitor(Visitor):
    
    def visit_SelectOperator(self, expression):
        if expression.func is not None:
            t = LambdaExpression.parse(expression.type, expression.func)
            return u"SELECT {0}".format(t.body.sql if not isinstance(t.body, ast.Attribute) else t.body.select_sql)
        else:
            cols = Enumerable(expression.type.inspect_columns())
            if not cols.count() > 0:
                raise TypeError(u"{0} has no defined columns in model".format(expression.type.__class__.__name__))
            sql = cols.select(
                lambda c: u"{0}.{1} AS {2}".format(expression.type.table_name(), c[1].column_name, c[0])
            )
            return u"SELECT {0}".format(u", ".join(sql))

    def visit_TableExpression(self, expression):
        return u"FROM {0}".format(expression.type.table_name())

    def visit_CountOperator(self, expression):
        return u"SELECT COUNT(*)"

    def visit_TakeOperator(self, expression):
        return u"LIMIT {0}".format(expression.limit)

    def visit_TakeExpression(self, expression):
        return u"{0} {1}".format(expression.exp.visit(self), expression.op.visit(self))

    def visit_SkipOperator(self, expression):
        return u"OFFSET {0}".format(expression.skip)

    def visit_SkipExpression(self, expression):
        return u"{0} {1}".format(expression.exp.visit(self), expression.op.visit(self))

    def visit_CountExpression(self, expression):
        return u"{0} FROM ({1})".format(expression.op.visit(self), expression.exp.visit(self))

    def visit_WhereOperator(self, expression):
        return u"WHERE {0}".format(LambdaExpression.parse(expression.type, expression.func).body.sql)

    def visit_WhereExpression(self, expression):
        return u"{0} {1}".format(expression.exp.visit(self), expression.op.visit(self))

    def visit_OrderByOperator(self, expression):
        t = LambdaExpression.parse(expression.type, expression.func)
        return u"ORDER BY {0}".format(t.body.sql)

    def visit_OrderByExpression(self, expression):
        return u"{0} {1} ASC".format(expression.exp.visit(self), expression.op.visit(self))

    def visit_OrderByDescendingExpression(self, expression):
        return u"{0} {1} DESC".format(expression.exp.visit(self), expression.op.visit(self))

    def visit_ThenByOperator(self, expression):
        t = LambdaExpression.parse(expression.type, expression.func)
        return u", {0}".format(t.body.sql)

    def visit_ThenByExpression(self, expression):
        return self.visit_OrderByExpression(expression)

    def visit_ThenByDescendingExpression(self, expression):
        return self.visit_OrderByDescendingExpression(expression)

    def visit_MaxOperator(self, expression):
        return u"SELECT MAX({0})".format(LambdaExpression.parse(expression.type, expression.func).body.sql)

    def visit_MaxExpression(self, expression):
        return self.visit_UnaryExpression(expression)

    def visit_MinOperator(self, expression):
        return u"SELECT MIN({0})".format(LambdaExpression.parse(expression.type, expression.func).body.sql)

    def visit_MinExpression(self, expression):
        return self.visit_UnaryExpression(expression)

    def visit_SumOperator(self, expression):
        return u"SELECT SUM({0})".format(LambdaExpression.parse(expression.type, expression.func).body.sql)

    def visit_SumExpression(self, expression):
        return self.visit_UnaryExpression(expression)

    def visit_AveOperator(self, expression):
        return u"SELECT AVG({0})".format(LambdaExpression.parse(expression.type, expression.func).body.sql)

    def visit_AvgExpression(self, expression):
        return self.visit_UnaryExpression(expression)




