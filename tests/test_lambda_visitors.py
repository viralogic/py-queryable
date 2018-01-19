import ast
from unittest import TestCase
from .models import Student
from py_queryable.expressions import LambdaExpression


class SqlLambdaTranslatorTest(TestCase):
    def setUp(self):
        self.simple_eq_uni = lambda x: x.first_name == u"Bruce"
        self.simple_eq_str = lambda x: x.first_name == 'Bruce'
        self.simple_lte = lambda x: x.gpa <= 10
        self.simple_lt = lambda x: x.gpa < 10
        self.simple_gte = lambda x: x.gpa >= 10
        self.simple_gt = lambda x: x.gpa > 10
        self.simple_plus = lambda x: x.gpa + 10
        self.simple_minus = lambda x: x.gpa - 10
        self.simple_div = lambda x: x.gpa / 10
        self.simple_mult = lambda x: x.gpa * 10
        self.simple_mod = lambda x: x.gpa % 2
        self.simple_and = lambda x: x.gpa >= 10 and x.gpa <= 50
        self.simple_or = lambda x: x.gpa >= 10 or x.first_name == u'Bruce'
        self.simple_not = lambda x: not x.gpa == 10
        self.simple_not_equals = lambda x: x.gpa != 10

        self.simple_in = lambda x: x.first_name in u"Bruce"
        self.simple_not_in = lambda x: x.last_name not in u"Fenske"

        self.simple_select = lambda x: x.first_name
        self.list_select = lambda x: [x.first_name, x.last_name, x.gpa]
        self.tuple_select = lambda x: (x.first_name, x.last_name, x.gpa)
        self.dict_select = lambda x: {'FirstName': x.first_name, 'LastName': x.last_name, 'GPA': x.gpa}

    @staticmethod
    def translate(func):
        return LambdaExpression.parse(Student, func)

    def test_Eq(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_eq_uni)
        self.assertIsInstance(t.body.ops[0], ast.Eq, u"Should be Eq instance")
        self.assertEquals(t.body.ops[0].sql, u"=", u"Eq() node should have sql property of '='")

    def test_LtE(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_lte)
        self.assertIsInstance(t.body.ops[0], ast.LtE, u"Should be LtE instance")
        self.assertEquals(t.body.ops[0].sql, u"<=", u"LtE() node should have sql property of '<=")

    def test_Lt(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_lt)
        self.assertIsInstance(t.body.ops[0], ast.Lt, u"Should be Lt instance")
        self.assertEquals(t.body.ops[0].sql, u"<", u"Lt() node should have sql property of '<'")

    def test_GtE(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_gte)
        self.assertIsInstance(t.body.ops[0], ast.GtE, u"Should be GtE instance")
        self.assertEquals(t.body.ops[0].sql, u">=", u"GtE() node should have sql property of '>='")

    def test_Gt(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_gt)
        self.assertIsInstance(t.body.ops[0], ast.Gt, u"Should be Gt instance")
        self.assertEquals(t.body.ops[0].sql, u">", u"Gt() node should have sql property of '>")

    def test_In(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_in)
        self.assertIsInstance(t.body.ops[0], ast.In, u"Should be In instance")
        self.assertEquals(t.body.ops[0].sql, u"IN", u"In() node should have sql property of 'IN'")

    def test_NotIn(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_not_in)
        self.assertIsInstance(t.body.ops[0], ast.NotIn, u"Should be NotIn instance")
        self.assertEquals(t.body.ops[0].sql, u"NOT IN", u"NotIn() node should have sql property of 'NOT IN'")

    def test_plus(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_plus)
        self.assertIsInstance(t.body.op, ast.Add, u"Should be Add instance")
        self.assertEquals(t.body.op.sql, u"+", u"Add() node should have sql property of '+'")

    def test_minus(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_minus)
        self.assertIsInstance(t.body.op, ast.Sub, u"Should be Sub instance")
        self.assertEquals(t.body.op.sql, u"-", u"Sub() node should have sql property of '-'")

    def test_div(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_div)
        self.assertIsInstance(t.body.op, ast.Div, u"Should be Div instance")
        self.assertEquals(t.body.op.sql, u"/", u"Div() node should have sql property of '/'")

    def test_mult(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_mult)
        self.assertIsInstance(t.body.op, ast.Mult, u"Should be Mult instance")
        self.assertEquals(t.body.op.sql, u"*", u"Mult() node should have sql property of '*'")

    def test_mod(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_mod)
        self.assertIsInstance(t.body.op, ast.Mod, u"Should be Mod instance")
        self.assertEquals(t.body.op.sql, u"%", u"Mod() node should have sql property of '%")

    def test_num_binop(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_mult)
        self.assertIsInstance(t.body.right, ast.Num, u"Should be a Num instance")
        self.assertEquals(
            t.body.right.sql,
            unicode(t.body.right.n),
            u"Num() node should have sql property equal to {0}".format(t.body.right.n)
        )

    def test_num_compare(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_gte)
        self.assertIsInstance(t.body.comparators[0], ast.Num, u"Should be a Num instance")
        self.assertEquals(
            t.body.comparators[0].sql,
            unicode(t.body.comparators[0].n),
            u"Num() node should have sql property equal to {0}".format(t.body.comparators[0].n)
        )

    def test_str(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_eq_str)
        self.assertIsInstance(t.body.comparators[0], ast.Str, u"Should be a Str instance")
        self.assertEquals(
            t.body.comparators[0].sql,
            unicode(t.body.comparators[0].s),
            u"Str() node should have sql property equal to {0}".format(t.body.comparators[0].sql)
        )

    def test_attribute(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_eq_uni)
        self.assertIsInstance(t.body.left, ast.Attribute, u"Should be Attribute instance")
        self.assertEquals(
            t.body.left.sql,
            u"{0}.{1}".format(Student.table_name(), Student.first_name.column_name),
            u"{0} should equal {1}".format(t.body.left.sql, Student.first_name.column_name)
        )

    def test_and(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_and)
        self.assertIsInstance(t.body.op, ast.And, u"Should be And instance")
        self.assertEquals(
            t.body.op.sql,
            u"AND",
            u"And() node should have sql property equal 'AND'"
        )

    def test_or(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_or)
        self.assertIsInstance(t.body.op, ast.Or, u"Should be Or instance")
        self.assertEquals(
            t.body.op.sql,
            u"OR",
            u"Or() node should have sql property equal 'Or'"
        )

    def test_compare_simple(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_lte)
        correct = u"student.gpa <= 10"
        self.assertIsInstance(t.body, ast.Compare, u"Should be a Compare instance")
        self.assertEquals(
            t.body.sql,
            correct,
            u"{0} should be same as {1}".format(t.body.sql, correct)
        )

    def test_compare_complex(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_and)
        values = t.body.values
        corrects = [u"student.gpa >= 10", u"student.gpa <= 50"]
        for i in range(0, len(values) - 1, 1):
            correct = corrects[i]
            value = values[i].sql
            self.assertEquals(value, correct, u"{0} should equal {1}".format(value, correct))

    def test_boolop(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_and)
        correct = u"student.gpa >= 10 AND student.gpa <= 50"
        self.assertIsInstance(t.body, ast.BoolOp, u"Should be a BoolOp instance")
        self.assertEqual(
            t.body.sql,
            correct,
            u"{0} should equal {1}".format(t.body.sql, correct)
        )

    def test_binop(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_plus)
        correct = u"student.gpa + 10"
        self.assertIsInstance(t.body, ast.BinOp, u"Should be a BinOp instance")
        self.assertEqual(
            t.body.sql,
            correct,
            u"{0} should equal {1}".format(t.body.sql, correct)
        )

    def test_not(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_not)
        self.assertIsInstance(t.body.op, ast.Not, u"Should be a Not instance")
        self.assertEqual(
            t.body.op.sql,
            u"NOT",
            u"Not() sql property should equal NOT"
        )

    def test_not_equals(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_not_equals)
        correct = u"<>"
        self.assertIsInstance(t.body.ops[0], ast.NotEq, u"Should be a NotEq instance")
        self.assertEqual(
            t.body.ops[0].sql,
            correct,
            u"{0} sql property should equal {1}".format(t.body.ops[0].sql, correct)
        )

    def test_unary(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_not)
        self.assertIsInstance(t.body, ast.UnaryOp, u"Should be a UnaryOp instance")
        correct = u"NOT student.gpa = 10"
        self.assertEqual(
            t.body.sql,
            correct,
            u"{0} sql property should equal {1}".format(t.body.sql, correct)
        )

    def test_Lambda(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_and)
        correct = u"student.gpa >= 10 AND student.gpa <= 50"
        self.assertEqual(t.body.sql, correct, u"{0} should equal {1}".format(t.body.sql, correct))

    def test_simple_select(self):
        t = SqlLambdaTranslatorTest.translate(self.simple_select)
        self.assertEqual(t.body.sql, u"student.first_name", u"Should equal 'student.first_name")

    def test_list_select(self):
        t = SqlLambdaTranslatorTest.translate(self.list_select)
        self.assertIsInstance(t.body, ast.List, u"Should be a List instance")
        correct = u"student.first_name AS first_name, student.last_name AS last_name, student.gpa AS gpa"
        self.assertEqual(
            t.body.sql,
            correct,
            u"{0} should equal {1}".format(t.body.sql, correct)
        )

    def test_tuple_select(self):
        t = SqlLambdaTranslatorTest.translate(self.tuple_select)
        self.assertIsInstance(t.body, ast.Tuple, u"Should be a List instance")
        correct = u"student.first_name AS first_name, student.last_name AS last_name, student.gpa AS gpa"
        self.assertEqual(
            t.body.sql,
            correct,
            u"{0} should equal {1}".format(t.body.sql, correct)
        )

    def test_dict_select(self):
        t = SqlLambdaTranslatorTest.translate(self.dict_select)
        self.assertIsInstance(t.body, ast.Dict, u"Should be a Dict instance")
        correct = u"student.first_name AS 'FirstName', student.last_name AS 'LastName', student.gpa AS 'GPA'"
        self.assertEqual(
            t.body.sql,
            correct,
            u"{0} should equal {1}".format(t.body.sql, correct)
        )
