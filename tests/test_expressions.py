from unittest import TestCase
from py_queryable import expressions
from py_queryable.expressions import unary
from py_queryable.expressions import operators
from py_queryable.expressions import sort
from py_queryable.visitors.sql import SqlVisitor
from .models import Student


class TestSqlExpressions(TestCase):

    def setUp(self):
        self.visitor = SqlVisitor()

    def test_select_expression(self):
        se = operators.SelectOperator(expressions.TableExpression(Student), lambda x: x.first_name)
        sql = self.visitor.visit(se)
        self.assertEqual(sql, u"SELECT x.first_name FROM student x")

        se = operators.SelectOperator(expressions.TableExpression(Student), lambda x: (x.first_name, x.last_name))
        sql = self.visitor.visit(se)
        self.assertEqual(sql, u"SELECT x.first_name, x.last_name FROM student x")

        se = operators.SelectOperator(expressions.TableExpression(Student), lambda x: { 'first': x.first_name, 'last': x.last_name })
        sql = self.visitor.visit(se)
        self.assertEqual(sql, u"SELECT x.first_name AS 'first', x.last_name AS 'last' FROM student x")

    def test_select_all(self):
        se = operators.SelectOperator(expressions.TableExpression(Student))
        sql = self.visitor.visit(se)
        self.assertEqual(sql, u"SELECT student.student_id, student.first_name, student.gpa, student.last_name FROM student")

        se = operators.SelectOperator(expressions.TableExpression(Student), lambda s: s)
        sql = self.visitor.visit(se)
        self.assertEqual(sql, u"SELECT s.student_id, s.first_name, s.gpa, s.last_name FROM student s")

    def test_where_expression(self):
        we = operators.WhereOperator(expressions.TableExpression(Student), lambda x: x.gpa > 10)
        sql = self.visitor.visit(we)
        self.assertTrue(sql.endswith(u"x.gpa > 10"))

    def test_where_expression_complex(self):
        we = operators.WhereOperator(
            expressions.TableExpression(Student), 
            lambda x: (x.gpa > 10 and x.first_name == u'Bruce') or x.first_name == u'Dustin'
            )
        sql = self.visitor.visit(we)
        self.assertTrue(
            sql.endswith(u"WHERE (x.gpa > 10 AND x.first_name = 'Bruce') OR x.first_name = 'Dustin'")
        )

        we = operators.WhereOperator(
            expressions.TableExpression(Student),
            lambda x: ((x.first_name == u'Bruce' and x.last_name == u'Fenske') or x.first_name == u'Dustin') or (x.gpa > 10 and x.gpa < 20)
        )
        sql = self.visitor.visit(we)
        self.assertTrue(
            sql.endswith(u"WHERE (x.first_name = 'Bruce' AND x.last_name = 'Fenske') OR (x.first_name = 'Dustin' OR (x.gpa > 10 AND x.gpa < 20))")
        )

    def test_count_expression(self):
        ce = operators.CountOperator(expressions.TableExpression(Student))
        sql = self.visitor.visit(ce)
        self.assertEqual(
            sql,
            u"SELECT COUNT(*) FROM student"
        )

        ce = operators.CountOperator(operators.SelectOperator(expressions.TableExpression(Student), lambda s: s.student_id))
        sql = self.visitor.visit(ce)
        self.assertEqual(
            sql,
            u"SELECT COUNT(*) FROM (SELECT s.student_id FROM student s)"
        )

    def test_take_expression(self):
        te = operators.TakeOperator(operators.SelectOperator(expressions.TableExpression(Student), lambda s: s.first_name), 1)
        sql = self.visitor.visit(te)
        self.assertEqual(sql, u"SELECT s.first_name FROM student s LIMIT 1")

        te = operators.TakeOperator(expressions.TableExpression(Student), 1)
        sql = self.visitor.visit(te)
        self.assertEqual(sql, u'SELECT student.student_id, student.first_name, student.gpa, student.last_name FROM student LIMIT 1')

    def test_skip_expression(self):
        se = operators.SkipOperator(operators.SelectOperator(expressions.TableExpression(Student), lambda s: s.first_name), 1)
        sql = self.visitor.visit(se)
        self.assertEqual(sql, u"SELECT s.first_name FROM student s OFFSET 1")

        se = operators.SkipOperator(expressions.TableExpression(Student), 1)
        sql = self.visitor.visit(se)
        self.assertEquals(sql, u'SELECT student.student_id, student.first_name, student.gpa, student.last_name FROM student OFFSET 1')

    def test_skip_limit_expression(self):
        qe = operators.TakeOperator(operators.SkipOperator(operators.SelectOperator(expressions.TableExpression(Student), lambda s: s.first_name), 1), 1)
        sql = self.visitor.visit(qe)
        self.assertEqual(sql, u"SELECT s.first_name FROM student s OFFSET 1 LIMIT 1")

        qe = operators.TakeOperator(operators.SkipOperator(expressions.TableExpression(Student), 1), 1)
        sql = self.visitor.visit(qe)
        self.assertEqual(sql, u'SELECT student.student_id, student.first_name, student.gpa, student.last_name FROM student OFFSET 1 LIMIT 1')

        qe = operators.SkipOperator(operators.TakeOperator(operators.SelectOperator(expressions.TableExpression(Student), lambda s: s.first_name), 1), 1)
        sql = self.visitor.visit(qe)
        self.assertEqual(sql, u"SELECT s.first_name FROM student s LIMIT 1 OFFSET 1")

        qe = operators.SkipOperator(operators.TakeOperator(expressions.TableExpression(Student), 1), 1)
        sql = self.visitor.visit(qe)
        self.assertEqual(sql, u'SELECT student.student_id, student.first_name, student.gpa, student.last_name FROM student LIMIT 1 OFFSET 1')

    def test_order_by_expression(self):
        te = operators.OrderByOperator(
            operators.SelectOperator(expressions.TableExpression(Student), lambda s: s.first_name),
            lambda s: s.first_name)
        sql = self.visitor.visit(te)
        self.assertEqual(sql, u"SELECT s.first_name FROM student s ORDER BY s.first_name ASC")

        te = operators.OrderByOperator(
            operators.SelectOperator(expressions.TableExpression(Student), lambda s: s.first_name))
        sql = self.visitor.visit(te)
        self.assertEqual(sql, u"SELECT s.first_name FROM student s ORDER BY s.first_name ASC")

        te = operators.OrderByOperator(
            expressions.TableExpression(Student),
            lambda s: s.first_name
        )
        sql = self.visitor.visit(te)
        self.assertEqual(
            sql, 
            u"SELECT student.student_id, student.first_name, student.gpa, student.last_name FROM student ORDER BY s.first_name ASC"
        )


    def test_then_by_expression(self):
        te = operators.ThenByOperator(
            operators.OrderByOperator(
                operators.SelectOperator(
                    expressions.TableExpression(Student),
                    lambda s: (s.first_name, s.gpa)
                ), lambda s: s.first_name
            ), lambda s: s.gpa
        )
        sql = self.visitor.visit(te)
        self.assertEqual(
            sql,
            u"SELECT s.first_name, s.gpa FROM student s ORDER BY s.first_name ASC, s.gpa ASC")

        te = operators.ThenByOperator(
            operators.OrderByOperator(
                operators.SelectOperator(
                    expressions.TableExpression(Student),
                    lambda s: (s.first_name, s.gpa)
                ), lambda s: s.first_name
            ), lambda u: u.gpa
        )
        sql = self.visitor.visit(te)
        self.assertEqual(
            sql,
            u"SELECT s.first_name, s.gpa FROM student s ORDER BY s.first_name ASC, s.gpa ASC"
        )

        tbde = operators.ThenByDescendingOperator(
            operators.OrderByOperator(
                operators.SelectOperator(expressions.TableExpression(Student)),
                lambda s: s.first_name
            ), lambda s: s.gpa
        )
        sql = self.visitor.visit(tbde)
        self.assertEqual(
            sql,
            u"SELECT student.student_id, student.first_name, student.gpa, student.last_name FROM student ORDER BY s.first_name ASC, s.gpa DESC")

    def test_order_by_descending_expression(self):
        te = operators.OrderByDescendingOperator(
            operators.SelectOperator(expressions.TableExpression(Student), lambda s: s.first_name),
            lambda s: s.first_name
        )
        sql = self.visitor.visit(te)
        self.assertEqual(sql, u"SELECT s.first_name FROM student s ORDER BY s.first_name DESC")

        te = operators.OrderByDescendingOperator(
            operators.SelectOperator(expressions.TableExpression(Student), lambda s: s.first_name))
        sql = self.visitor.visit(te)
        self.assertEqual(sql, u"SELECT s.first_name FROM student s ORDER BY s.first_name DESC")

        te = operators.OrderByDescendingOperator(
            expressions.TableExpression(Student),
            lambda s: s.first_name
        )
        sql = self.visitor.visit(te)
        self.assertEqual(sql, u"SELECT student.student_id, student.first_name, student.gpa, student.last_name FROM student ORDER BY s.first_name DESC")

    def test_then_by_descending_expression(self):
        te = unary.UnaryExpression(
            Student, 
            unary.SelectExpression(Student, lambda s: (s.first_name, s.gpa)), self.table_expression)
        tbde = sort.ThenByDescendingExpression(
            Student,
            lambda s: s.gpa,
            sort.OrderByDescendingExpression(Student, lambda s: s.first_name, te)
        )
        sql = self.visitor.visit(tbde)
        self.assertEqual(
            sql,
            u"SELECT student.first_name AS first_name, student.gpa AS gpa FROM student ORDER BY student.first_name DESC , student.gpa DESC"
        )

        tbde = unary.ThenByExpression(
            Student,
            lambda s: s.gpa,
            sort.OrderByDescendingExpression(Student, lambda s: s.first_name, te)
        )

        sql = self.visitor.visit(tbde)
        self.assertEqual(
            sql,
            u"SELECT student.first_name AS first_name, student.gpa AS gpa FROM student ORDER BY student.first_name DESC , student.gpa ASC"
        )

    def test_max_expression(self):
        te = operators.MaxOperator(expressions.TableExpression(Student))
        self.assertRaises(AttributeError, self.visitor.visit, te)

        te = operators.MaxOperator(expressions.TableExpression(Student), lambda s: s.gpa)
        sql = self.visitor.visit(te)
        self.assertEqual(
            sql,
            u"SELECT MAX(s.gpa) FROM (SELECT s.gpa FROM student s) s"
        )

        te = operators.MaxOperator(operators.SelectOperator(expressions.TableExpression(Student), lambda s: s.gpa))
        sql = self.visitor.visit(te)
        self.assertEqual(
            sql,
            u"SELECT MAX(s.gpa) FROM (SELECT s.gpa FROM student s) s"
        )

        te = operators.MaxOperator(operators.SelectOperator(expressions.TableExpression(Student), lambda s: s.gpa), lambda u: u.gpa)
        sql = self.visitor.visit(te)
        self.assertEqual(
            sql,
            u"SELECT MAX(u.gpa) FROM (SELECT s.gpa FROM student s) u"
        )

    def test_min_expression(self):
        te = operators.MinOperator(expressions.TableExpression(Student), lambda s: s.gpa)
        sql = self.visitor.visit(te)
        self.assertEqual(
            sql,
            u"SELECT MIN(s.gpa) FROM (SELECT s.gpa FROM student s) s"
        )

        te = operators.MinOperator(operators.SelectOperator(expressions.TableExpression(Student), lambda s: s.gpa))
        sql = self.visitor.visit(te)
        self.assertEqual(
            sql,
            u"SELECT MIN(s.gpa) FROM (SELECT s.gpa FROM student s) s"
        )

        te = operators.MinOperator(operators.SelectOperator(expressions.TableExpression(Student), lambda s: s.gpa), lambda u: u.gpa)
        sql = self.visitor.visit(te)
        self.assertEqual(
            sql,
            u"SELECT MIN(u.gpa) FROM (SELECT s.gpa FROM student s) u"
        )

    def test_sum_expression(self):
        te = operators.SumOperator(expressions.TableExpression(Student), lambda s: s.gpa)
        sql = self.visitor.visit(te)
        self.assertEqual(
            sql,
            u"SELECT SUM(s.gpa) FROM (SELECT s.gpa FROM student s) s"
        )

        te = operators.SumOperator(operators.SelectOperator(expressions.TableExpression(Student), lambda s: s.gpa))
        sql = self.visitor.visit(te)
        self.assertEqual(
            sql,
            u"SELECT SUM(s.gpa) FROM (SELECT s.gpa FROM student s) s"
        )

        te = operators.SumOperator(operators.SelectOperator(expressions.TableExpression(Student), lambda s: s.gpa), lambda u: u.gpa)
        sql = self.visitor.visit(te)
        self.assertEqual(
            sql,
            u"SELECT SUM(u.gpa) FROM (SELECT s.gpa FROM student s) u"
        )

    def test_avg_expression(self):
        te = operators.AveOperator(expressions.TableExpression(Student), lambda s: s.gpa)
        sql = self.visitor.visit(te)
        self.assertEqual(
            sql,
            u"SELECT AVG(s.gpa) FROM (SELECT s.gpa FROM student s) s"
        )

        te = operators.AveOperator(operators.SelectOperator(expressions.TableExpression(Student), lambda s: s.gpa))
        sql = self.visitor.visit(te)
        self.assertEqual(
            sql,
            u"SELECT AVG(s.gpa) FROM (SELECT s.gpa FROM student s) s"
        )

        te = operators.AveOperator(operators.SelectOperator(expressions.TableExpression(Student), lambda s: s.gpa), lambda u: u.gpa)
        sql = self.visitor.visit(te)
        self.assertEqual(
            sql,
            u"SELECT AVG(u.gpa) FROM (SELECT s.gpa FROM student s) u"
        )