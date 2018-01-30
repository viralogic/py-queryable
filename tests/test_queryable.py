import os
from unittest import TestCase
from . import _sqlite_db_path
from py_queryable.expressions import *
from .models import Student
from py_queryable.db_providers import SqliteDbConnection
from py_linq.exceptions import NoElementsError


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

    def tearDown(self):
        if self.conn is not None:
            self.conn.connection.close()
        try:
            os.remove(self.conn.provider_config.db_uri)
        except:
            pass
