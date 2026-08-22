from typing import Callable

from attrs import frozen, Factory


@frozen
class OnEventSubscriber[* TA, TO]:
    _event: "Event[*TA, TO]"

    def is_subscribed_by(self, subscriber: Callable[[*TA], TO]) -> bool:
        return self._event.is_subscribed_by(subscriber)

    def subscribe(self, subscriber: Callable[[*TA], TO]) -> None:
        self._event.subscribe(subscriber)

    def unsubscribe(self, subscriber: Callable[[*TA], TO], *, is_strict: bool = True) -> None:
        self._event.unsubscribe(subscriber, is_strict=is_strict)


@frozen
class Event[* TA, TO]:
    _subscribers: list[Callable[[*TA], TO]] = Factory(list)

    @property
    def subscriber(self) -> OnEventSubscriber[*TA, TO]:
        return OnEventSubscriber(self)

    def is_subscribed_by(self, subscriber: Callable[[*TA], TO]) -> bool:
        return subscriber in self._subscribers

    def subscribe(self, subscriber: Callable[[*TA], TO]) -> None:
        self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber: Callable[[*TA], TO], *, is_strict: bool = True) -> None:
        if is_strict or self.is_subscribed_by(subscriber):
            self._subscribers.remove(subscriber)

    def invoke(self, *args: *TA) -> None:
        for subscriber in self._subscribers:
            subscriber(*args)
