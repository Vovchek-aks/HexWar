from attrs import frozen

import appearance.protocols as proto


@frozen
class NoCatchingLayer(proto.ClicksCatchingLayer):
    def can_catch(self, click: proto.Click) -> bool:
        return False

    def catch(self, click: proto.Click) -> None:
        ...
