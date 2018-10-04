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
            return u"SELECT {0} {1}".format(
                u", ".join(sql),
                expression.exp.visit(self)
            )

    def visit_AliasOperator(self, expression):
        return "FROM ({0}) {1}".format(expression.exp.visit(self), expression.alias)

    def visit_WhereOperator(self, expression):
        select = expression.find(operators.SelectOperator)
        if select is None:
            expression.exp = operators.SelectOperator(expression.exp)
        t = LambdaExpression.parse(expression.type, expression.func)
        return u"SELECT * {0} WHERE {1}".format(
            operators.AliasOperator(t.body.id, expression.exp).visit(self),
            t.body.sql
        )

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
            if type(expression.exp) == operators.SkipOperator:
                expression.exp.exp = operators.SelectOperator(expression.exp.exp)
            else:
                expression.exp = operators.SelectOperator(expression.exp)
        if type(expression.exp) == operators.SkipOperator:
            return operators.SkipOperator(
                operators.TakeOperator(expression.exp.exp, expression.limit),
                expression.exp.skip
                ).visit(self)
        return u"{0} LIMIT {1}".format(expression.exp.visit(self), expression.limit)

    def visit_SkipOperator(self, expression):
        select = expression.find(operators.SelectOperator)
        if select is None:
            if type(expression.exp) == operators.TakeOperator:
                expression.exp.exp = operators.SelectOperator(expression.exp.exp)
            else:
                expression.exp = operators.SelectOperator(expression.exp)
        if type(expression.exp) != operators.TakeOperator:
            expression.exp = operators.TakeOperator(expression.exp, -1)
        return u"{0} OFFSET {1}".format(expression.exp.visit(self), expression.skip)

    def visit_OrderByOperator(self, expression):
        t = LambdaExpression.parse(expression.type, expression.func)
        select = expression.find(operators.SelectOperator)
        if select is None:
            expression.exp = operators.SelectOperator(expression.exp)
        return u"SELECT * {0} ORDER BY {1} ASC".format(
            operators.AliasOperator(t.body.id, expression.exp).visit(self),
            t.body.sql
        )

    def visit_OrderByDescendingOperator(self, expression):
        sql = self.visit_OrderByOperator(expression)[0:-4]
        return u"{0} DESC".format(sql)

    def visit_ThenByOperator(self, expression):
        if type(expression.exp) != operators.OrderByOperator and type(expression.exp) != operators.OrderByDescendingOperator:
            raise AttributeError("ThenBy needs to follow OrderBy or OrderByDescending")
        t = LambdaExpression.parse(expression.type, expression.func)
        te = LambdaExpression.parse(expression.exp.type, expression.exp.func)
        return u"{0}, {1} ASC".format(
            expression.exp.visit(self),
            t.body.sql.replace(t.body.id, te.body.id)
        )

    def visit_ThenByDescendingOperator(self, expression):
        sql = self.visit_ThenByOperator(expression)[0:-4]
        return u"{0} DESC".format(sql)

    def visit_MaxOperator(self, expression):
        return self._visit_lambda(expression, u"MAX")

    def visit_MinOperator(self, expression):
        return self._visit_lambda(expression, u"MIN")

    def visit_SumOperator(self, expression):
        return self._visit_lambda(expression, u"SUM")

    def visit_AveOperator(self, expression):
        return self._visit_lambda(expression, u"AVG")

