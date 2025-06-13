from dataclasses import dataclass,asdict,astuple

@dataclass(frozen=True)
class WORKER:
    identifier:Metadata
    job:Metadata
    events:Metadata
    app:Metadata
    tasks:Metadata