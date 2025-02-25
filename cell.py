from attrs import define

import protocols as proto


@define
class Cell(proto.Cell):
    _belonging: proto.Agent
    _figure: proto.Figure
