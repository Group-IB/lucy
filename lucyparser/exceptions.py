class BaseLucyException(Exception):
    pass


class LucyUnexpectedEndException(BaseLucyException):
    def __init__(self):
        super().__init__("Unexpected end of input")


class LucyUnexpectedCharacter(BaseLucyException):
    def __init__(self, unexpected, expected):
        super().__init__(f"Unexpected character {unexpected}, expected one of {expected}")


class LucyUndefinedOperator(BaseLucyException):
    def __init__(self, operator):
        super().__init__(f"Undefined operator: {operator}")


class LucyIllegalLiteral(BaseLucyException):
    def __init__(self, literal):
        super().__init__(f"Illegal literal with escaped slash: {literal}")
