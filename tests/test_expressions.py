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
        se = unary.UnaryExpression(Student, unary.SelectExpression(Student, lambda x: x.first_name), self.table_expression)
        sql = self.visitor.visit(se)
        correct = u"SELECT student.first_name AS first_name FROM student"
        self.assertEqual(
            sql,
            correct,
            u"{0} does not equal {1}".format(sql, correct)
        )

    def test_select_all(self):
        se = unary.UnaryExpression(Student, unary.SelectExpression(Student), self.table_expression)
        sql = self.visitor.visit(se)
        self.assertTrue(sql.startswith(u"SELECT"))
        self.assertTrue(sql.endswith(u"FROM student"))
        self.assertTrue(u"student.first_name AS first_name" in sql)
        self.assertTrue(u"student.student_id AS student_id" in sql)
        self.assertTrue(u"student.last_name AS last_name" in sql)
        self.assertTrue(u"student.gpa AS gpa")

    def test_where_expression(self):
        we = unary.WhereExpression(Student, lambda x: x.gpa > 10, self.table_expression)
        sql = self.visitor.visit(we)
        self.assertTrue(sql.endswith(u"student.gpa > 10"))

    def test_where_expression_complex(self):
        we = unary.WhereExpression(
            Student,
            lambda x: (x.gpa > 10 and x.first_name == u'Bruce') or x.first_name == u'Dustin',
            self.table_expression
        )
        sql = self.visitor.visit(we)
        self.assertTrue(
            sql.endswith(u"WHERE (student.gpa > 10 AND student.first_name = 'Bruce') OR student.first_name = 'Dustin'")
        )

        we = unary.WhereExpression(
                Student,
                lambda x: ((x.first_name == u'Bruce' and x.last_name == u'Fenske') or x.first_name == u'Dustin') or (x.gpa > 10 and x.gpa < 20),
                self.table_expression
            )
        sql = self.visitor.visit(we)
        self.assertTrue(
            sql.endswith(u"WHERE (student.first_name = 'Bruce' AND student.last_name = 'Fenske') OR (student.first_name = 'Dustin' OR (student.gpa > 10 AND student.gpa < 20))")
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

    def test_avg_expression(self):
        te = operators.AveOperator(expressions.TableExpression(Student), lambda s: s.gpa)
        sql = self.visitor.visit(te)
        self.assertEqual(
            sql,
            u"SELECT AVG(student.gpa) FROM student"
        )

        # te = unary.UnaryExpression(
        #     Student,
        #     unary.SelectExpression(Student, lambda s: s.gpa), self.table_expression)
        # me = unary.AvgExpression(Student, te)
        # sql = self.visitor.visit(me)
        # self.assertEqual(
        #     sql,
        #     u"SELECT AVG(student.gpa) FROM student"
        # )