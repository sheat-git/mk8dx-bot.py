from components import BotMessage

class BotError(Exception):
    __slots__ = (
        'message'
    )
    def __init__(self, message: BotMessage, *args: object) -> None:
        self.message: BotMessage = message
        super().__init__(*args)
