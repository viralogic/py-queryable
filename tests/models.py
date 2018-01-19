from py_queryable import Model
from py_queryable import Column, PrimaryKey, ForeignKey


class StubModel(Model):
    __table_name__ = u'test_table'
    test_int_column = Column(int, 'int_column')


class StubModel2(Model):
    __table_name__ = u'test_table'
    test_int_column = Column(int)


class StubPrimary(Model):
    __table_name__ = u"test_table"
    test_pk = PrimaryKey(int, 'int_pk')


class StubPrimaryString(Model):
    __table_name__ = u"test_table"
    test_pk = PrimaryKey(unicode, 'unicode_pk')


class StubIntUnique(Model):
    __table_name__ = u"test_table"
    test_pk = PrimaryKey(int)
    test_unique = Column(int, 'int_column', is_unique=True)


class StubForeignKey(Model):
    __table_name__ = u"foreign_key_table"
    test_pk = PrimaryKey(int, 'int_pk')
    test_fk = ForeignKey(StubPrimary, 'test_fk', is_nullable=False)


class StubUpdateModel(Model):
    __table_name__ = u"test_update_table"
    key = PrimaryKey(int, 'key_column')
    update_col = Column(int, 'update_column')


class Student(Model):
    __table_name__ = u"student"
    student_id = PrimaryKey(int, "student_id")
    first_name = Column(unicode, "first_name")
    last_name = Column(unicode, "last_name")
    gpa = Column(int, "gpa")
