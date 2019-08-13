from dataclasses import dataclass
from typing import Optional

from lucyparser.tree import USER_OPERATOR_TO_OPERATOR, Operator, UserOperator
from .exceptions import LucyUnexpectedEndException, LucyUnexpectedCharacter


@dataclass
class Cursor:
    """
    Peekable iterator implementation. For parsing lookaheades
    """

    input: str
    cursor: int = 0

    def pop(self) -> str:
        next_char = self.peek()
        if next_char:
            self.cursor += 1
            return next_char
        raise LucyUnexpectedEndException()

    def peek(self, n=0) -> Optional[str]:
        """
        Peek a character n elements ahead
        """
        if len(self.input) <= self.cursor + n:
            return None
        return self.input[self.cursor + n]

    def empty(self) -> bool:
        return len(self.input) <= self.cursor

    def starts_with_a_word(self, word: str) -> bool:
        counter = 0
        for expected_char in word:
            actual_char = self.peek(counter)
            if not actual_char:
                return False
            if actual_char.casefold() != expected_char.casefold():
                return False
            counter += 1
        char_after_word = self.peek(counter)
        if not char_after_word:
            # Probably something is wrong but, we will notice it later
            return True
        # Checkin a next character to chack that match was not a part of a bigger word
        return char_after_word.isspace() or char_after_word == "("

    def starts_with_a_char(self, char: str) -> bool:
        return self.peek() == char

    def consume_known_char(self, char: str):
        actual_char = self.pop()
        if actual_char != char:
            raise LucyUnexpectedCharacter(unexpected=actual_char, expected=char)

    def consume_known_operator(self) -> Operator:
        current_operator = self.pop()

        if current_operator == UserOperator.EQ:
            return USER_OPERATOR_TO_OPERATOR[current_operator]

        equal_is_possible = current_operator in UserOperator.equal_is_possible
        equal_is_required = current_operator in UserOperator.equal_is_required

        if not (equal_is_possible or equal_is_required):
            raise LucyUnexpectedCharacter(unexpected=current_operator, expected="".join((*UserOperator.equal_is_required,
                                                                                         *UserOperator.equal_is_possible)))

        next_char = self.peek()

        if next_char == UserOperator.EQUAL_SIGN:
            self.pop()
            return USER_OPERATOR_TO_OPERATOR[current_operator + UserOperator.EQUAL_SIGN]
        elif equal_is_possible:
            return USER_OPERATOR_TO_OPERATOR[current_operator]
        elif equal_is_required:
            raise LucyUnexpectedCharacter(unexpected=next_char, expected=UserOperator.EQUAL_SIGN)

        raise LucyUnexpectedEndException()

    def consume(self, n: int):
        for _ in range(n):
            if not self.pop():
                raise LucyUnexpectedEndException()

    def consume_spaces(self):
        while 1:
            next_char = self.peek()
            if next_char is None:
                break
            if next_char.isspace():
                self.pop()
            else:
                break
