import string
from dataclasses import dataclass
from typing import List, Tuple, Union

from .condition import Condition, Operator
from .cursor import Cursor
from .tree import ConditionTree, LogicalOperator

Expression = Union[ConditionTree, Condition]


def parse(string: str) -> Union[ConditionTree, Condition]:
    """
    User facing parse function. All user needs to know about
    """
    cursor = Cursor(string)
    cursor.consume_spaces()
    parser = Parser()
    tree = parser.read_tree(cursor)
    cursor.consume_spaces()
    if not cursor.empty():
        raise Exception(
            f"Input should've been finished by now! Left: {cursor.input[cursor.cursor:]}"
        )
    return tree


class Parser:
    name_chars = string.ascii_letters + string.digits + "_."
    name_first_chars = string.ascii_letters + "_"
    value_chars = string.ascii_letters + string.digits

    def read_tree(self, cur: Cursor) -> Expression:
        tree = self.read_expressions(cur)
        if isinstance(tree, ConditionTree):
            tree.simplify()
        return tree

    def read_expressions(self, cur: Cursor) -> Expression:
        """
        Read several expressions, separated with logical operators
        """

        def pop_expression_from_stack(
            op_stack: List[LogicalOperator], expr_stack: List[Expression]
        ) -> Expression:
            op = operators_stack.pop()
            right = expressions_stack.pop()
            left = expressions_stack.pop()
            return ConditionTree(operator=op, children=[left, right])

        expression = self.read_expression(cur)
        cur.consume_spaces()
        operators_stack: List[LogicalOperator] = []
        expressions_stack: List[Expression] = [expression]
        while 1:
            if cur.starts_with_a_word("and"):
                op, expr = self.read_operator(cur, LogicalOperator.AND)
                operators_stack.append(op)
                expressions_stack.append(expr)
                cur.consume_spaces()
            elif cur.starts_with_a_word("or"):
                op, expr = self.read_operator(cur, LogicalOperator.OR)
                if operators_stack and operators_stack[-1] == LogicalOperator.AND:
                    expressions_stack.append(
                        pop_expression_from_stack(operators_stack, expressions_stack)
                    )
                operators_stack.append(op)
                expressions_stack.append(expr)
                cur.consume_spaces()
            else:
                break
        while operators_stack:
            expressions_stack.append(
                pop_expression_from_stack(operators_stack, expressions_stack)
            )
        return expressions_stack[0]

    def read_operator(
        self, cur: Cursor, op: LogicalOperator
    ) -> Tuple[LogicalOperator, Expression]:
        """
        Read operator and folowing expression from the stream
        """
        if op == LogicalOperator.AND:
            length = 3
        else:
            length = 2
        cur.consume(length)
        cur.consume_spaces()
        expression = self.read_expression(cur)
        cur.consume_spaces()
        return op, expression

    def read_expression(self, cur: Cursor) -> Expression:
        """
        Read a single expression:
        Expression is:
            - multiple expressions combined (in some way) in braces
            - negation of something
            - a single condition in name:value form
        """
        if cur.starts_with_a_char("("):
            cur.consume_known_char("(")
            tree = self.read_tree(cur)
            cur.consume_known_char(")")
            return tree
        if cur.starts_with_a_word("not"):
            cur.consume(3)
            cur.consume_spaces()
            tree = ConditionTree(
                operator=LogicalOperator.NOT, children=[self.read_expression(cur)]
            )
            cur.consume_spaces()
            return tree
        return self.read_condition(cur)

    def read_condition(self, cur: Cursor) -> Condition:
        """
        Read a single entry of "name: value"
        """
        name = self.read_field_name(cur)
        cur.consume_spaces()
        cur.consume_known_char(":")
        cur.consume_spaces()
        value = self.read_field_value(cur)
        return Condition(name=name, value=value, operator=Operator.EQ)

    def read_field_name(self, cur: Cursor) -> str:
        name = cur.pop()
        if name not in self.name_first_chars:
            raise Exception(
                f"Unexpected character {name}. Expected one of {self.name_first_chars}"
            )
        while 1:
            next_char = cur.peek()
            if next_char and next_char in self.name_chars:
                name += cur.pop()
            else:
                return name

    def read_field_value(self, cur: Cursor) -> str:
        def read_until(terminator: str) -> str:
            value = ""
            while 1:
                if not cur.empty():
                    char = cur.pop()
                    if char == terminator:
                        return value
                    value += char
                else:
                    raise Exception("Unexpected end of input")

        if cur.starts_with_a_char('"'):
            cur.consume_known_char('"')
            return read_until('"')
        if cur.starts_with_a_char("'"):
            cur.consume_known_char("'")
            return read_until("'")
        next_char = cur.peek()
        if not next_char:
            raise Exception("Unexpected end of input")
        if next_char not in self.value_chars:
            raise Exception(
                f"Unexpected character {next_char}, expected one of {self.value_chars}"
            )
        value = cur.pop()
        while 1:
            next_char = cur.peek()
            if not next_char or next_char not in self.value_chars:
                return value
            value += cur.pop()
