from dataclasses import dataclass,asdict,astuple

@dataclass(frozen=True)
class expression:
    identifier = identifier
    expression = expression
    symbol = ':='
    variables = variables