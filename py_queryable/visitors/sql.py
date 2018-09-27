import ast
from py_linq import Enumerable
from ..expressions import LambdaExpression, TableExpression
from ..expressions import operators
from . import Visitor


class SqlVisitor(Visitor):
    
    def _set_lambda(self, expression):
        if expression.func is None:
            if type(expression.exp) != operators.SelectOperator\
             or (type(expression.exp) == operators.SelectOperator and expression.exp.func is None):
                raise AttributeError("lambda function is required for SelectOperator")
            expression.func = expression.exp.func
        return expression

    def _visit_lambda(self, expression, sql):
        expression = self._set_lambda(expression)
        t = LambdaExpression.parse(expression.type, expression.func)
        return u"SELECT {0}({1}) {2}".format(
            sql,
            t.body.sql,
            operators.AliasOperator(t.body.id, expression.exp).visit(self)\
            if type(expression.exp) == operators.SelectOperator\
            else operators.AliasOperator(t.body.id, operators.SelectOperator(expression.exp, expression.func)).visit(self))

    def visit_SelectOperator(self, expression):
        cols = Enumerable(expression.type.inspect_columns())
        if not cols.count() > 0:
                raise TypeError(u"{0} has no defined columns in model".format(expression.type.__class__.__name__))
        if expression.func is not None:
            t = LambdaExpression.parse(expression.type, expression.func)
            if not hasattr(t.body, "sql"):
                sql = cols.select(
                    lambda c: u"{0}.{1}".format(t.body.id, c[1].column_name)
                )
                t.body.sql = u", ".join(sql)
            return u"SELECT {0} {1} {2}".format(t.body.sql, expression.exp.visit(self), t.body.id)
        else:
            sql = cols.select(
                lambda c: u"{0}.{1}".format(expression.type.table_name(), c[1].column_name)
            )
            return u"SELECT {0} {1} {2}".format(
                u", ".join(sql),
                expression.exp.visit(self),
                expression.type.table_name()
            )

    def visit_AliasOperator(self, expression):
        return "FROM ({0}) {1}".format(expression.exp.visit(self), expression.alias)

    def visit_WhereOperator(self, expression):
        return u"{0} WHERE {1}".format(expression.exp.visit(self), LambdaExpression.parse(expression.type, expression.func).body.sql)

    def visit_TableExpression(self, expression):
        return u"FROM {0}".format(expression.type.table_name())

    def visit_CountOperator(self, expression):
        result = expression.exp.visit(self)
        if type(expression.exp) != TableExpression:
            result = u"FROM ({0})".format(result)
        return u"SELECT COUNT(*) {0}".format(result)

    def visit_TakeOperator(self, expression):
        select = expression.find(operators.SelectOperator)
        if select is None:
            expression.exp = operators.SelectOperator(expression.exp)
        return u"{0} LIMIT {1}".format(expression.exp.visit(self), expression.limit)

    def visit_SkipOperator(self, expression):
        select = expression.find(operators.SelectOperator)
        if select is None:
            expression.exp = operators.SelectOperator(expression.exp)
        return u"{0} OFFSET {1}".format(expression.exp.visit(self), expression.skip)

    def visit_OrderByOperator(self, expression):
        t = LambdaExpression.parse(expression.type, expression.func)
        return u"ORDER BY {0}".format(t.body.sql)

    def visit_OrderByDescendingOperator(self, expression):
        expression = self._set_lambda(expression)
        t = LambdaExpression.parse(expression.type, expression.func)
        return u"SELECT {0} {1} ORDER BY {2} DESC".format(
            t.body.sql,
            u"{0} {1}".format(expression.exp.visit(self), t.body.id) if type(expression.exp) != operators.SelectOperator \
             else operators.AliasOperator(t.body.id, expression.exp).visit(self),
            t.body.sql
            )

    def visit_OrderByExpression(self, expression):
        return u"{0} {1} ASC".format(expression.exp.visit(self), expression.op.visit(self))

    def visit_ThenByOperator(self, expression):
        t = LambdaExpression.parse(expression.type, expression.func)
        return u", {0}".format(t.body.sql)

    def visit_ThenByExpression(self, expression):
        return self.visit_OrderByExpression(expression)

    def visit_ThenByDescendingExpression(self, expression):
        return self.visit_OrderByDescendingExpression(expression)

    def visit_MaxOperator(self, expression):
        return self._visit_lambda(expression, u"MAX")

    def visit_MinOperator(self, expression):
        return self._visit_lambda(expression, u"MIN")

    def visit_SumOperator(self, expression):
        return self._visit_lambda(expression, u"SUM")

    def visit_AveOperator(self, expression):
        return self._visit_lambda(expression, u"AVG")

