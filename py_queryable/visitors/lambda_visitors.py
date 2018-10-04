import ast
from py_linq import Enumerable
from collections import deque


class SqlLambdaTranslator(ast.NodeVisitor):

    def __init__(self):
        super(SqlLambdaTranslator, self).__init__()

    def find_node_type(self, start_node, node_type, children_attr):
        if isinstance(start_node, node_type):
            return start_node
        if not hasattr(start_node, children_attr):
            raise AttributeError(u"No such attribute = {0} found for node = {1}".format(children_attr, start_node.__repr__()))
        children = getattr(start_node, children_attr)
        q = deque(children)
        while len(q) > 0:
            node = q.popleft()
            if isinstance(node, node_type):
                return node
            for n in getattr(node, children_attr):
                q.append(n)
        return None

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
        node.sql = u"{0}.{1}".format(node.value.id, node.attr)
        node.id = node.value.id

    def visit_And(self, node):
        node.sql = u"AND"

    def visit_Or(self, node):
        node.sql = u"OR"

    def visit_Compare(self, node):
        self.generic_visit(node)

        operator = node.ops[0].sql
        if operator == "IN":
            if isinstance(node.left, ast.Str):
                node.id = node.comparators[0].id
                node.sql = u"{0} {1} '%{2}%'".format(node.comparators[0].sql, node.ops[0].text_sql, node.left.sql)
            elif isinstance(node.left, unicode) and isinstance(node.comparators[0], unicode):
                node.sql = u"{0} {1} '%{2}%'".format(node.comparators[0], node.ops[0].text_sql, node.left)
            elif isinstance(node.left, unicode) and isinstance(node.comparators[0], ast.Attribute):
                node.id = node.comparators[0].id
                node.sql = u"{0} {1} '%{2}%'".format(node.comparators[0].sql, node.ops[0].text_sql, node.left)
            elif isinstance(node.left, ast.Attribute) and isinstance(node.comparators[0], unicode):
                node.id = node.left.id
                node.sql = u"{0} {1} '%{2}%'".format(node.left.sql, node.ops[0].sql, node.comparators[0])
            else:
                raise Exception(u"Don't know what to do with this node={0} for the IN operator".format(node.__repr__()))
        else:
            node.id = node.left.id
            if hasattr(node.comparators[0], u"sql"):
                comparator = node.comparators[0].sql
            elif isinstance(node.comparators[0], unicode):
                comparator = u"'{0}'".format(node.comparators[0])
            else:
                comparator = node.comparators[0]
            node.sql = u"{0} {1} {2}".format(node.left.sql, node.ops[0].sql, comparator)

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        vals = Enumerable(node.values)
        compare = self.find_node_type(node, ast.Compare, u"values")
        if compare is None:
            raise AttributeError(u"No ast.Compare node can be found in ast.BoolOp={0}".format(node.__repr__()))
        node.id = compare.id
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
        node.sql = u", ".join(Enumerable(node.elts).select(lambda x: x.sql))
        node.id = node.elts[0].value.id

    def visit_Tuple(self, node):
        self.visit_List(node)

    def visit_Dict(self, node):
        self.generic_visit(node)
        result = []
        for i in range(len(node.values)):
            result.append(u"{0} AS '{1}'".format(node.values[i].sql, node.keys[i].s))
        node.sql = u", ".join(result)
        node.id = node.values[0].id
