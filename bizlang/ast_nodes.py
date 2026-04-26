from dataclasses import dataclass, field
from typing import Optional, Union


@dataclass
class AggExpr:
    func: str    # sum | avg | count | min | max
    column: str


@dataclass
class Condition:
    column: str
    op: str      # == | != | > | < | >= | <=
    value: Union[str, int, float]
    negate: bool = False


@dataclass
class LoadNode:
    filename: str
    follow_on: Optional[object] = None  # another AST node chained via AND


@dataclass
class ComputeNode:
    agg: AggExpr
    group_by: list
    time_grain: Optional[str] = None   # monthly | daily | quarterly | yearly
    where: Optional[Condition] = None


@dataclass
class ChartNode:
    chart_type: str          # bar | line | pie | scatter
    agg: AggExpr
    compare_cols: list = field(default_factory=list)
    group_by: list = field(default_factory=list)


@dataclass
class PivotNode:
    index_cols: list
    column_cols: list = field(default_factory=list)
    agg: Optional[AggExpr] = None


@dataclass
class FilterNode:
    source: str
    conditions: list  # list[Condition]
