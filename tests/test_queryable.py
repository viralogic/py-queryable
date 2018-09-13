import os
from unittest import TestCase
from . import _sqlite_db_path
from py_queryable.expressions import *
from .models import Student
from py_queryable.db_providers import SqliteDbConnection
from py_linq.exceptions import NoElementsError, MoreThanOneMatchingElement, NoMatchingElement


class QueryableTest(TestCase):
    def setUp(self):
        self.path = _sqlite_db_path
        self.conn = SqliteDbConnection(self.path)

        self.conn.create_table(Student)
        self.conn.save_changes()

        self.student1 = Student()
        self.student1.student_id = 1
        self.student1.first_name = u"Bruce"
        self.student1.last_name = u"Fenske"
        self.student1.gpa = 50

        self.student2 = Student()
        self.student2.student_id = 2
        self.student2.first_name = u"Abraham"
        self.student2.last_name = u"Mudryk"
        self.student2.gpa = 9

        self.conn.add(self.student1)
        self.conn.add(self.student2)

        self.conn.save_changes()

    def test_sql(self):
        sql = self.conn.query(UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))).sql
        self.assertTrue(sql.startswith(u"SELECT"))
        self.assertTrue(sql.endswith(u"FROM student"))
        self.assertTrue(u"student.first_name AS first_name" in sql)
        self.assertTrue(u"student.student_id AS student_id" in sql)
        self.assertTrue(u"student.last_name AS last_name" in sql)
        self.assertTrue(u"student.gpa AS gpa")

    def test_count(self):
        count = self.conn.query(UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))).count()
        self.assertEquals(count, 2, u"Number of students inserted should equal 2 - get {0}".format(count))

    def test_take(self):
        result = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        ).take(1).to_list()
        self.assertEquals(len(result), 1, u"Appears that take expression is not working")
        self.assertEquals(
            result[0].student_id,
            1,
            u"Student ID should be 1 - get {0}".format(result[0].student_id)
        )
        self.assertEquals(
            result[0].first_name,
            u"Bruce", u"Bruce should be the first name - get {0}".format(result[0].first_name)
        )
        self.assertEquals(
            result[0].last_name,
            u"Fenske", u"Fenske should be the last name - get {0}".format(result[0].last_name)
        )

        result = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        ).skip(1).take(1).to_list()

        self.assertEquals(
            result[0].student_id,
            2,
            u"Student ID should be 2 - get {0}".format(result[0].student_id)
        )
        self.assertEquals(
            result[0].first_name,
            u"Abraham", u"Abraham should be the first name - get {0}".format(result[0].first_name)
        )
        self.assertEquals(
            result[0].last_name,
            u"Mudryk", u"Mudryk should be the last name - get {0}".format(result[0].last_name)
        )

    def test_skip(self):
        result = self.conn.query(UnaryExpression(
            Student,
            SelectExpression(Student),
            TableExpression(Student)
        )).skip(1).to_list()

        self.assertEquals(
            len(result),
            1,
            u"Appears that skip expression is not working"
        )

        self.assertEquals(
            result[0].student_id,
            2,
            u"Student ID should be 2 - get {0}".format(result[0].student_id)
        )
        self.assertEquals(
            result[0].first_name,
            u"Abraham", u"Abraham should be the first name - get {0}".format(result[0].first_name)
        )
        self.assertEquals(
            result[0].last_name,
            u"Mudryk", u"Mudryk should be the last name - get {0}".format(result[0].last_name)
        )

        result = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student, lambda x: x.first_name), TableExpression(Student))
        ).take(1).skip(1).to_list()
        self.assertEquals(
            len(result),
            1,
            u"Appears that take expression is not working"
        )
        self.assertEquals(
            result[0],
            u"Abraham",
            u"Abraham should be the first name - get {0}".format(result[0])
        )

    def test_first(self):

        result = self.conn.query(UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))).first()
        self.assertEquals(
            result.student_id,
            1,
            u"Student ID should be 1 - get {0}".format(result.student_id)
        )
        self.assertEquals(
            result.first_name,
            u"Bruce", u"Bruce should be the first name - get {0}".format(result.first_name)
        )
        self.assertEquals(
            result.last_name,
            u"Fenske",
            u"Fenske should be the last name - get {0}".format(result.last_name)
        )

        self.conn.remove(self.student1)
        self.conn.remove(self.student2)
        self.conn.save_changes()

        self.assertRaises(
            NoElementsError,
            self.conn.query(UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))).first
        )

    def test_first_or_default(self):
        self.conn.remove(self.student1)
        self.conn.save_changes()

        result = self.conn.query(UnaryExpression(Student, SelectExpression(Student), TableExpression(Student)))\
            .first_or_default()
        self.assertEquals(result.student_id, 2, u"Student ID should be 2 - get {0}".format(result.student_id))
        self.assertEquals(
            result.first_name,
            u"Abraham",
            u"Abraham should be the first name - get {0}".format(result.first_name)
        )
        self.assertEquals(
            result.last_name,
            u"Mudryk",
            u"Mudryk should be the last name - get {0}".format(result.last_name)
        )

        self.conn.remove(self.student2)
        self.conn.save_changes()
        result = self.conn.query(UnaryExpression(Student, SelectExpression(Student), TableExpression(Student)))\
            .first_or_default()
        self.assertIsNone(result, u"First or Default query should be none. The Student table is empty")

    def test_where(self):
        students = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        ).where(lambda s: s.student_id == 1)
        num_students = students.count()
        self.assertEquals(num_students, 1, u"Should only be one student row returned in query")

        student = students.first()
        self.assertIsNotNone(student, u"Student instance should not be None")
        self.assertEquals(student.first_name, u"Bruce", u"First name should be Bruce")
        self.assertEquals(student.gpa, 50, u"GPA should be 50")

        self.student3 = Student()
        self.student3.student_id = 3
        self.student3.first_name = u"Miguel"
        self.student3.last_name = u"McDavid"
        self.student3.gpa = 90

        self.conn.add(self.student3)
        self.conn.save_changes()

        students = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        ).where(lambda s: s.student_id == 1 or student.gpa >= 50)
        self.assertEquals(students.count(), 2)

        students = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        ).where(lambda s: s.student_id == 1 and student.gpa > 50)
        self.assertIsNone(students.first_or_default())

    def test_single(self):
        students = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        )
        student = students.single(lambda s: s.student_id == 1)
        self.assertIsNotNone(student, u"Student instance should not be None")
        self.assertEquals(student.first_name, u"Bruce", u"First name should be Bruce")
        self.assertEquals(student.gpa, 50, u"GPA should be 50")

        self.assertRaises(MoreThanOneMatchingElement, students.single, lambda s: s.gpa > 0)

        self.assertRaises(
            NoMatchingElement,
            students.single,
            lambda s: s.first_name == u"Wayne" and s.last_name == u"Gretzky"
        )

    def test_single_or_default(self):
        students = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        )
        student = students.single_or_default(lambda s: s.student_id == 1)
        self.assertIsNotNone(student, u"Student instance should not be None")
        self.assertEquals(student.first_name, u"Bruce", u"First name should be Bruce")
        self.assertEquals(student.gpa, 50, u"GPA should be 50")

        self.assertIsNone(students.single_or_default(lambda s: s.first_name == u"Wayne" and s.last_name == u"Gretzky"))
        self.assertRaises(MoreThanOneMatchingElement, students.single_or_default, lambda s: s.gpa > 0)

    def test_order_by(self):
        self.student3 = Student()
        self.student3.student_id = 3
        self.student3.first_name = u"Miguel"
        self.student3.last_name = u"McDavid"
        self.student3.gpa = 90

        self.conn.add(self.student3)
        self.conn.save_changes()

        students = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        )

        ordered_students = students.order_by(lambda x: x.gpa)
        highest_grade = 0
        for s in ordered_students:
            self.assertTrue(highest_grade <= s.gpa, u"{0} is not <= {1}".format(highest_grade, s.gpa))
            highest_grade = s.gpa

        # Try ordering multiple columns
        ordered_students = students.order_by(lambda x: x.last_name).then_by(lambda x: x.first_name).to_list()
        self.assertEquals(ordered_students[0].last_name, u"Fenske")
        self.assertEquals(ordered_students[0].first_name, u"Bruce")
        self.assertEquals(ordered_students[1].last_name, u"McDavid")
        self.assertEquals(ordered_students[1].first_name, u"Miguel")
        self.assertEquals(ordered_students[2].last_name, u"Mudryk")
        self.assertEquals(ordered_students[2].first_name, u"Abraham")

    def test_order_by_multiple(self):
        self.student3 = Student()
        self.student3.student_id = 3
        self.student3.first_name = u"Miguel"
        self.student3.last_name = u"McDavid"
        self.student3.gpa = 9

        self.conn.add(self.student3)
        self.conn.save_changes()

        students = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        )

        # Try ordering multiple columns
        ordered_students = students.order_by(lambda x: x.gpa).then_by(lambda x: x.last_name).to_list()
        self.assertEquals(ordered_students[0].gpa, 9)
        self.assertEquals(ordered_students[0].last_name, u"McDavid")
        self.assertEquals(ordered_students[1].gpa, 9)
        self.assertEquals(ordered_students[1].last_name, u"Mudryk")
        self.assertEquals(ordered_students[2].gpa, 50)
        self.assertEquals(ordered_students[2].last_name, u"Fenske")

    def test_order_by_descending(self):
        self.student3 = Student()
        self.student3.student_id = 3
        self.student3.first_name = u"Miguel"
        self.student3.last_name = u"McDavid"
        self.student3.gpa = 90

        self.conn.add(self.student3)
        self.conn.save_changes()

        students = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        )

        ordered_students = students.order_by_descending(lambda x: x.gpa)
        highest_grade = 100
        for s in ordered_students:
            self.assertTrue(highest_grade >= s.gpa, u"{0} is not <= {1}".format(highest_grade, s.gpa))
            highest_grade = s.gpa

        # Try ordering multiple columns
        ordered_students = students\
            .order_by_descending(lambda x: x.last_name)\
            .then_by_descending(lambda x: x.first_name).\
            to_list()
        self.assertEquals(ordered_students[0].last_name, u"Mudryk")
        self.assertEquals(ordered_students[0].first_name, u"Abraham")
        self.assertEquals(ordered_students[1].last_name, u"McDavid")
        self.assertEquals(ordered_students[1].first_name, u"Miguel")
        self.assertEquals(ordered_students[2].last_name, u"Fenske")
        self.assertEquals(ordered_students[2].first_name, u"Bruce")

    def test_order_by_descending_multiple(self):
        self.student3 = Student()
        self.student3.student_id = 3
        self.student3.first_name = u"Miguel"
        self.student3.last_name = u"McDavid"
        self.student3.gpa = 9

        self.conn.add(self.student3)
        self.conn.save_changes()

        students = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        )

        # Try ordering multiple columns
        ordered_students = students\
            .order_by_descending(lambda x: x.gpa)\
            .then_by_descending(lambda x: x.last_name)\
            .to_list()
        self.assertEquals(ordered_students[0].gpa, 50)
        self.assertEquals(ordered_students[0].last_name, u"Fenske")
        self.assertEquals(ordered_students[1].gpa, 9)
        self.assertEquals(ordered_students[1].last_name, u"Mudryk")
        self.assertEquals(ordered_students[2].gpa, 9)
        self.assertEquals(ordered_students[2].last_name, u"McDavid")

        ordered_students = students\
            .order_by_descending(lambda x: x.last_name)\
            .then_by_descending(lambda x: x.gpa)\
            .to_list()
        self.assertEquals(ordered_students[0].gpa, 9)
        self.assertEquals(ordered_students[0].last_name, u"Mudryk")
        self.assertEquals(ordered_students[1].gpa, 9)
        self.assertEquals(ordered_students[1].last_name, u"McDavid")
        self.assertEquals(ordered_students[2].gpa, 50)
        self.assertEquals(ordered_students[2].last_name, u"Fenske")

    def test_max(self):
        students = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        )
        max_gpa = students.max(lambda s: s.gpa)
        self.assertEquals(max_gpa, 50)

    def test_min(self):
        students = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        )
        min_gpa = students.min(lambda s: s.gpa)
        self.assertEquals(min_gpa, 9)

    def test_sum(self):
        students = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        )
        sum_gpa = students.sum(lambda s: s.gpa)
        self.assertEquals(sum_gpa, 59)

    def test_sum_exceptions(self):
        students = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        )
        self.assertRaises(AttributeError, students.sum)

    def test_avg(self):
        students = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        )
        avg_gpa = students.average(lambda s: s.gpa)
        self.assertEqual(avg_gpa, 29.5)

    def test_any(self):
        students = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        )
        self.assertTrue(students.any(lambda s: s.gpa < 50))
        self.assertFalse(students.any(lambda s: s.gpa > 80))
        self.assertTrue(students.any())

    def test_all(self):
        students = self.conn.query(
            UnaryExpression(Student, SelectExpression(Student), TableExpression(Student))
        )
        self.assertFalse(students.all(lambda s: s.gpa > 50))
        self.assertTrue(students.all(lambda s: "k" in s.last_name))
        self.assertTrue(students.all())

    def tearDown(self):
        if self.conn is not None:
            self.conn.connection.close()
        try:
            os.remove(self.conn.provider_config.db_uri)
        except:
            pass
