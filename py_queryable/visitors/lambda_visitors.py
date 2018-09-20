import ast
from py_linq import Enumerable


class SqlLambdaTranslator(ast.NodeVisitor):

    def __init__(self, T):
        super(SqlLambdaTranslator, self).__init__()

    def visit_Eq(self, node):
        node.sql = u"="

    def visit_LtE(self, node):
        node.sql = u"<="

    def visit_GtE(self, node):
        node.sql = u">="

    def visit_Gt(self, node):
        node.sql = u">"

    def visit_Lt(self, node):
        node.sql = u"<"

    def visit_Add(self, node):
        node.sql = u"+"

    def visit_Sub(self, node):
        node.sql = u"-"

    def visit_Div(self, node):
        node.sql = u"/"

    def visit_Mult(self, node):
        node.sql = u"*"

    def visit_Mod(self, node):
        node.sql = u"%"

    def visit_Num(self, node):
        node.sql = u"{0}".format(node.n)

    def visit_Str(self, node):
        node.sql = unicode(node.s)

    def visit_In(self, node):
        node.sql = u"IN"
        node.text_sql = u"LIKE"

    def visit_NotIn(self, node):
        node.sql = u"NOT IN"
        node.text_sql = u"NOT LIKE"

    def visit_Attribute(self, node):
        # model_column = Enumerable(self.type.get_column_members())\
        #     .single_or_default(lambda c: c[0].lower() == node.attr.lower())

        # if model_column is None:
        #     raise AttributeError(u"No property named {0} can be found for {1}".format(node.attr, self.type.__name__))
        # node.sql = u"{0}.{1}".format(self.type.table_name(), model_column[1].column_name)
        # node.select_sql = u"{0} AS {1}".format(node.sql, model_column[0])
        # node.type = model_column[1].column_type
        raise NotImplementedError()

    def visit_And(self, node):
        node.sql = u"AND"

    def visit_Or(self, node):
        node.sql = u"OR"

    def visit_Compare(self, node):
        self.generic_visit(node)
        if hasattr(node.comparators[0], u"sql"):
            comparator = node.comparators[0].sql
        elif isinstance(node.comparators[0], unicode):
            comparator = u"'{0}'".format(node.comparators[0])
        else:
            comparator = node.comparators[0]
        
        operator = node.ops[0].sql
        if operator == "IN" and isinstance(node.left.sql, unicode) and isinstance(comparator, unicode):
            node.sql = u"{0} {1} '%{2}%'".format(comparator, node.ops[0].text_sql, node.left.sql)
        else:
            node.sql = u"{0} {1} {2}".format(node.left.sql, node.ops[0].sql, comparator
        )

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        vals = Enumerable(node.values)
        node.sql = u" {0} ".format(node.op.sql).join(
            vals.select(lambda v: u"({0})".format(v.sql) if isinstance(v, ast.BoolOp) else v.sql)
        )


    def visit_BinOp(self, node):
        self.generic_visit(node)
        node.sql = u"{0} {1} {2}".format(node.left.sql, node.op.sql, node.right.sql)

    def visit_Not(self, node):
        node.sql = u"NOT"

    def visit_NotEq(self, node):
        node.sql = u"<>"

    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        node.sql = u"{0} {1}".format(node.op.sql, node.operand.sql)

    def visit_Lambda(self, node):
        self.generic_visit(node)

    def visit_List(self, node):
        self.generic_visit(node)
        node.sql = u", ".join(Enumerable(node.elts).select(lambda x: x.select_sql))
        node.type = list

    def visit_Tuple(self, node):
        self.visit_List(node)
        node.type = tuple

    def visit_Dict(self, node):
        self.generic_visit(node)
        for i in range(0, len(node.values), 1):
            attr = node.values[i]
            key = node.keys[i] if not hasattr(node.keys[i], u"sql") else node.keys[i].sql
            attr.select_sql = u"{0} AS '{1}'".format(attr.sql, key)
        node.sql = u", ".join(Enumerable(node.values).select(lambda x: x.select_sql))
        node.type = dict




