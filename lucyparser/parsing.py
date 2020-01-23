import string
from typing import List, Optional, Callable

from .cursor import Cursor
from .exceptions import LucyUnexpectedEndException, LucyUnexpectedCharacter, LucyIllegalLiteral
from .tree import BaseNode, simplify, NotNode, AndNode, ExpressionNode, LogicalNode, get_logical_node, LogicalOperator, \
    RawOperator, RAW_OPERATOR_TO_OPERATOR, Operator


def parse(string: str, parser_class: Optional[Callable] = None) -> BaseNode:
    """
    User facing parse function. All user needs to know about
    """
    if parser_class is None:
        parser_class = Parser
    cursor = Cursor(string)
    cursor.consume_spaces()
    parser = parser_class()
    tree = parser.read_tree(cursor)
    cursor.consume_spaces()
    if not cursor.empty():
        raise LucyUnexpectedEndException()
    return tree


class Parser:
    name_chars = string.ascii_letters + string.digits + "_."
    name_first_chars = string.ascii_letters + "_"
    value_chars = string.ascii_letters + string.digits + "-.*_?!;,:@|"
    escaped_chars = {
        "\\": "\\",
        "n": "\n",
        '"': '"',
        "'": "'",
        "a": "\a",
        "b": "\b",
        "f": "\f",
        "r": "\r",
        "t": "\t",
        "v": "\v"
    }

    def permitted_name_char(self, c: str) -> bool:
        return c in self.name_chars

    def permitted_name_first_char(self, c: str) -> bool:
        return c in self.name_first_chars

    def permitted_name_value_char(self, c: str) -> bool:
        return c in self.value_chars

    def read_tree(self, cur: Cursor) -> BaseNode:
        tree = self.read_expressions(cur)
        return simplify(tree)

    def read_expressions(self, cur: Cursor) -> BaseNode:
        """
        Read several expressions, separated with logical operators
        """

        def pop_expression_from_stack() -> LogicalNode:
            right = expressions_stack.pop()
            left = expressions_stack.pop()
            return get_logical_node(logical_operator=operators_stack.pop(), children=[left, right])

        cur.consume_spaces()
        expression = self.read_expression(cur)
        cur.consume_spaces()

        operators_stack: List[LogicalOperator] = []
        expressions_stack: List[BaseNode] = [expression]

        while 1:
            if cur.starts_with_a_word("and"):
                expressions_stack.append(self.read_and_operator(cur))
                operators_stack.append(LogicalOperator.AND)
                cur.consume_spaces()

            elif cur.starts_with_a_word("or"):
                node = self.read_or_operator(cur)

                if operators_stack and operators_stack[-1] == LogicalOperator.AND:
                    expressions_stack.append(pop_expression_from_stack())

                operators_stack.append(LogicalOperator.OR)
                expressions_stack.append(node)
                cur.consume_spaces()
            else:
                break
        while operators_stack:
            expressions_stack.append(pop_expression_from_stack())
        return expressions_stack[0]

    def _read_operator(self, cur: Cursor, length: int) -> BaseNode:
        """
        Read operator and following expression from the stream
        """
        cur.consume(length)
        cur.consume_spaces()
        expression = self.read_expression(cur)
        cur.consume_spaces()
        return expression

    def read_or_operator(self, cur: Cursor) -> BaseNode:
        return self._read_operator(cur=cur, length=2)

    def read_and_operator(self, cur: Cursor) -> BaseNode:
        return self._read_operator(cur=cur, length=3)

    def read_expression(self, cur: Cursor) -> BaseNode:
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
            tree = NotNode(children=[self.read_expression(cur)])
            cur.consume_spaces()
            return tree
        return AndNode(children=[self.read_condition(cur)])

    def read_condition(self, cur: Cursor) -> ExpressionNode:
        """
        Read a single entry of "name: value"
        """
        cur.consume_spaces()
        name = self.read_field_name(cur)
        cur.consume_spaces()
        operator = self.read_operator(cur=cur)
        cur.consume_spaces()
        value = self.read_field_value(cur)
        return ExpressionNode(name=name, value=value, operator=operator)

    def read_operator(self, cur: Cursor) -> Operator:
        current_operator = cur.pop()

        if current_operator in RawOperator.equal_not_required:
            return RAW_OPERATOR_TO_OPERATOR[current_operator]

        equal_is_possible = current_operator in RawOperator.equal_is_possible

        if not equal_is_possible:
            raise LucyUnexpectedCharacter(unexpected=current_operator, expected="".join(RawOperator.equal_is_possible))

        next_char = cur.peek()

        if next_char == RawOperator.EQUAL_SIGN:
            cur.pop()
            current_operator += RawOperator.EQUAL_SIGN

        return RAW_OPERATOR_TO_OPERATOR[current_operator]

    def read_field_name(self, cur: Cursor) -> str:
        name = cur.pop()
        if not self.permitted_name_first_char(name):
            raise LucyUnexpectedCharacter(unexpected=name, expected=self.name_first_chars)

        while 1:
            next_char = cur.peek()
            if next_char and self.permitted_name_char(next_char):
                name += cur.pop()
            else:
                return name

    def read_field_value(self, cur: Cursor) -> str:
        def read_until(terminator: str) -> str:
            value = ""
            while 1:
                char = cur.pop()

                if char == "\\":
                    char = cur.pop()
                    char_with_escaped_slash = self.escaped_chars.get(char)

                    if char_with_escaped_slash is None:
                        raise LucyIllegalLiteral(literal=char)
                    value += char_with_escaped_slash
                    continue

                elif char == terminator:
                    return value

                value += char

        if cur.starts_with_a_char('"'):
            cur.consume_known_char('"')
            return read_until('"')
        if cur.starts_with_a_char("'"):
            cur.consume_known_char("'")
            return read_until("'")
        next_char = cur.peek()
        if not next_char:
            raise LucyUnexpectedEndException()
        if not self.permitted_name_value_char(next_char):
            raise LucyUnexpectedCharacter(unexpected=next_char, expected=self.value_chars)

        value = cur.pop()
        while 1:
            next_char = cur.peek()
            if not next_char or not self.permitted_name_value_char(next_char):
                return value
            value += cur.pop()
