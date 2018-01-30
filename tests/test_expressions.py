from unittest import TestCase
from py_queryable.expressions import *
from py_queryable.visitors.sql import SqlVisitor
from .models import Student


class TestSqlExpressions(TestCase):

    def setUp(self):
        self.visitor = SqlVisitor()
        self.table_expression = TableExpression(Student)

    def test_select_expression(self):
        se = UnaryExpression(Student, SelectExpression(Student, lambda x: x.first_name), self.table_expression)
        sql = self.visitor.visit(se)
        correct = u"SELECT student.first_name AS first_name FROM student"
        self.assertEqual(
            sql,
            correct,
            u"{0} does not equal {1}".format(sql, correct)
        )

    def test_select_all(self):
        se = UnaryExpression(Student, SelectExpression(Student), self.table_expression)
        sql = self.visitor.visit(se)
        self.assertTrue(sql.startswith(u"SELECT"))
        self.assertTrue(sql.endswith(u"FROM student"))
        self.assertTrue(u"student.first_name AS first_name" in sql)
        self.assertTrue(u"student.student_id AS student_id" in sql)
        self.assertTrue(u"student.last_name AS last_name" in sql)
        self.assertTrue(u"student.gpa AS gpa")

    def test_where_expression(self):
        we = WhereExpression(Student, lambda x: x.gpa > 10, self.table_expression)
        sql = self.visitor.visit(we)
        self.assertTrue(sql.endswith(u"student.gpa > 10"))

    def test_where_expression_complex(self):
        we = WhereExpression(
            Student,
            lambda x: (x.gpa > 10 and x.first_name == u'Bruce') or x.first_name == u'Dustin',
            self.table_expression
        )
        sql = self.visitor.visit(we)
        self.assertTrue(
            sql.endswith(u"WHERE (student.gpa > 10 AND student.first_name = 'Bruce') OR student.first_name = 'Dustin'")
        )

        we = WhereExpression(
                Student,
                lambda x: ((x.first_name == u'Bruce' and x.last_name == u'Fenske') or x.first_name == u'Dustin') or (x.gpa > 10 and x.gpa < 20),
                self.table_expression
            )
        sql = self.visitor.visit(we)
        self.assertTrue(
            sql.endswith(u"WHERE (student.first_name = 'Bruce' AND student.last_name = 'Fenske') OR (student.first_name = 'Dustin' OR (student.gpa > 10 AND student.gpa < 20))")
        )

    def test_count_expression(self):
        ce = CountExpression(Student, UnaryExpression(Student, SelectExpression(Student), self.table_expression))
        sql = self.visitor.visit(ce)
        self.assertEqual(
            sql,
            u"SELECT COUNT(*) FROM (SELECT student.student_id AS student_id, student.first_name AS first_name, student.gpa AS gpa, student.last_name AS last_name FROM student)"
        )

    def test_take_expression(self):
        qe = UnaryExpression(Student, SelectExpression(Student, lambda s: s.first_name), self.table_expression)
        te = TakeExpression(Student, qe, 1)
        sql = self.visitor.visit(te)
        self.assertEqual(sql, u"SELECT student.first_name AS first_name FROM student LIMIT 1")

    def test_skip_expression(self):
        se = SkipExpression(Student, UnaryExpression(Student, SelectExpression(Student, lambda s: s.first_name), self.table_expression), 1)
        sql = self.visitor.visit(se)
        self.assertEqual(sql, u"SELECT student.first_name AS first_name FROM student OFFSET 1")

    def test_skip_limit_expression(self):
        qe = UnaryExpression(Student, SelectExpression(Student, lambda s: s.first_name), self.table_expression)
        se = SkipExpression(Student, qe, 1)
        te = TakeExpression(Student, se, 1)
        sql = self.visitor.visit(te)
        self.assertEqual(sql, u"SELECT student.first_name AS first_name FROM student OFFSET 1 LIMIT 1")

        te = TakeExpression(Student, qe, 1)
        se = SkipExpression(Student, te, 1)
        sql = self.visitor.visit(se)
        self.assertEqual(sql, u"SELECT student.first_name AS first_name FROM student LIMIT 1 OFFSET 1")
