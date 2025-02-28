from attrs import define

import protocols as proto


@define
class Cell(proto.Cell):
    _controlling: proto.Agent
    _figure: proto.Figure

    @property
    def controlling(self) -> proto.Agent:
        return self._controlling

    @property
    def figure(self) -> proto.Figure:
        return self._figure
