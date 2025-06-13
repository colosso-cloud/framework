from dataclasses import dataclass,asdict,astuple

# required:bool | driven:str | identifier
# TLV is a tuple of (Type, Length, Value)

@dataclass(frozen=True)
class metadata:
    identity:str
    type: str
    value: str
    cardinality: int
    schema:dict