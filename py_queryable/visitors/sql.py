import ast
from py_linq import Enumerable
from . import IExpressionVisitor
from ..expressions import LambdaExpression


class SqlVisitor(IExpressionVisitor):

    def visit_UnaryExpression(self, expression):
        return u"{0} {1}".format(expression.op.visit(self), expression.exp.visit(self))

    def visit_SelectExpression(self, expression):
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

    def visit_WhereExpression(self, expression):
        t = LambdaExpression.parse(expression.type, expression.func)
        return u"{0} WHERE {1}".format(expression.exp.visit(self), t.body.sql)

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


