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

    def test_select_all(self):
        se = operators.SelectOperator(expressions.TableExpression(Student))
        sql = self.visitor.visit(se)
        self.assertEqual(sql, u"SELECT student.student_id, student.first_name, student.gpa, student.last_name FROM student")

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
        ce = unary.CountExpression(
            Student, 
            expressions.UnaryExpression(Student, unary.SelectExpression(Student), self.table_expression)
        )
        sql = self.visitor.visit(ce)
        self.assertEqual(
            sql,
            u"SELECT COUNT(*) FROM (SELECT student.student_id AS student_id, student.first_name AS first_name, student.gpa AS gpa, student.last_name AS last_name FROM student)"
        )

    def test_take_expression(self):
        qe = unary.UnaryExpression(
            Student,
            unary.SelectExpression(Student, lambda s: s.first_name), self.table_expression)
        te = unary.TakeExpression(Student, qe, 1)
        sql = self.visitor.visit(te)
        self.assertEqual(sql, u"SELECT student.first_name AS first_name FROM student LIMIT 1")

    def test_skip_expression(self):
        se = unary.SkipExpression(
            Student,
            expressions.UnaryExpression(Student, unary.SelectExpression(Student, lambda s: s.first_name), self.table_expression), 1)
        sql = self.visitor.visit(se)
        self.assertEqual(sql, u"SELECT student.first_name AS first_name FROM student OFFSET 1")

    def test_skip_limit_expression(self):
        qe = unary.UnaryExpression(
            Student, 
            unary.SelectExpression(Student, lambda s: s.first_name), self.table_expression)
        se = unary.SkipExpression(Student, qe, 1)
        te = unary.TakeExpression(Student, se, 1)
        sql = self.visitor.visit(te)
        self.assertEqual(sql, u"SELECT student.first_name AS first_name FROM student OFFSET 1 LIMIT 1")

        te = unary.TakeExpression(Student, qe, 1)
        se = unary.SkipExpression(Student, te, 1)
        sql = self.visitor.visit(se)
        self.assertEqual(sql, u"SELECT student.first_name AS first_name FROM student LIMIT 1 OFFSET 1")

    def test_order_by_operator(self):
        obo = operators.OrderByOperator(Student, lambda x: x.first_name)
        sql = self.visitor.visit(obo)
        self.assertEqual(sql, u"ORDER BY student.first_name")

    def test_order_by_expression(self):
        te = unary.UnaryExpression(
            Student, 
            unary.SelectExpression(Student, lambda s: s.first_name), self.table_expression)
        obe = unary.OrderByExpression(Student, lambda s: s.first_name, te)
        sql = self.visitor.visit(obe)
        self.assertEqual(sql, u"SELECT student.first_name AS first_name FROM student ORDER BY student.first_name ASC")

    def test_then_by_expression(self):
        te = unary.UnaryExpression(
            Student,
            unary.SelectExpression(Student, lambda s: (s.first_name, s.gpa)), self.table_expression)
        tbe = unary.ThenByExpression(
            Student, 
            lambda s: s.gpa,
            unary.OrderByExpression(Student, lambda s: s.first_name, te))
        sql = self.visitor.visit(tbe)
        self.assertEqual(
            sql,
            u"SELECT student.first_name AS first_name, student.gpa AS gpa FROM student ORDER BY student.first_name ASC , student.gpa ASC")

        tbde = sort.ThenByDescendingExpression(
            Student,
            lambda s: s.gpa, unary.OrderByExpression(Student, lambda s: s.first_name, te))
        sql = self.visitor.visit(tbde)
        self.assertEqual(
            sql,
            u"SELECT student.first_name AS first_name, student.gpa AS gpa FROM student ORDER BY student.first_name ASC , student.gpa DESC")

    def test_order_by_descending_expression(self):
        te = unary.UnaryExpression(
            Student,
            unary.SelectExpression(Student, lambda s: s.first_name), self.table_expression)
        obe = sort.OrderByDescendingExpression(Student, lambda s: s.first_name, te)
        sql = self.visitor.visit(obe)
        self.assertEqual(sql, u"SELECT student.first_name AS first_name FROM student ORDER BY student.first_name DESC")

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
        te = unary.UnaryExpression(
            Student,
            unary.SelectExpression(Student),
            self.table_expression)
        me = unary.MaxExpression(Student, te, lambda s: s.gpa)
        sql = self.visitor.visit(me)
        self.assertEqual(
            sql,
            u"SELECT MAX(student.gpa) FROM student"
        )

        te = unary.UnaryExpression(
            Student,
            unary.SelectExpression(Student, lambda s: s.gpa), self.table_expression)
        me = unary.MaxExpression(Student, te)
        sql = self.visitor.visit(me)
        self.assertEqual(
            sql,
            u"SELECT MAX(student.gpa) FROM student"
        )

    def test_min_expression(self):
        te = unary.UnaryExpression(
            Student,
            unary.SelectExpression(Student), self.table_expression)
        me = unary.MinExpression(Student, te, lambda s: s.gpa)
        sql = self.visitor.visit(me)
        self.assertEqual(
            sql,
            u"SELECT MIN(student.gpa) FROM student"
        )

        te = unary.UnaryExpression(
            Student,
            unary.SelectExpression(Student, lambda s: s.gpa), self.table_expression)
        me = unary.MinExpression(Student, te)
        sql = self.visitor.visit(me)
        self.assertEqual(
            sql,
            u"SELECT MIN(student.gpa) FROM student"
        )

    def test_sum_expression(self):
        te = unary.UnaryExpression(
            Student,
            unary.SelectExpression(Student), self.table_expression)
        me = unary.SumExpression(Student, te, lambda s: s.gpa)
        sql = self.visitor.visit(me)
        self.assertEqual(
            sql,
            u"SELECT SUM(student.gpa) FROM student"
        )

        te = unary.UnaryExpression(
            Student,
            unary.SelectExpression(Student, lambda s: s.gpa), self.table_expression)
        me = unary.SumExpression(Student, te)
        sql = self.visitor.visit(me)
        self.assertEqual(
            sql,
            u"SELECT SUM(student.gpa) FROM student"
        )

    # def test_avg_expression(self):
    #     te = operators.AveOperator(expressions.TableExpression(Student), lambda s: s.gpa)
    #     sql = self.visitor.visit(te)
    #     self.assertEqual(
    #         sql,
    #         u"SELECT AVG(student.gpa) FROM student"
    #     )
    
    # te = unary.UnaryExpression(
    #     Student,
    #     unary.SelectExpression(Student, lambda s: s.gpa), self.table_expression)
    # me = unary.AvgExpression(Student, te)
    # sql = self.visitor.visit(me)
    # self.assertEqual(
    #     sql,
    #     u"SELECT AVG(student.gpa) FROM student"
    # )