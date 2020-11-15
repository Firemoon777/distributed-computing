from pa.reactor.event_type import EventType
from pa.reactor.handler import EventHandler


class Reactor:

    

    def register_handler(self, handler: EventHandler, event_type: EventType):
        pass

    def remove_handler(self, handler: EventHandler, event_type: EventType):
        pass

    def handle_events(self, timeout):
        pass