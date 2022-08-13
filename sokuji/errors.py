from components import BotMessage
from lang import Lang

class SokujiError(Exception):
    __slots__ = (
        'message'
    )
    def __init__(self, message: BotMessage, *args: object) -> None:
        self.message: BotMessage = message
        super().__init__(*args)

class SokujiNotFoundError(SokujiError):
    def __init__(self, *args: object) -> None:
        super().__init__(message=BotMessage(content=\
            'Sokuji is not found. Starts sokuji.\n'
            '即時が見つかりません。即時を開始してください'
        ), *args)

class SokujiArchivedError(SokujiError):
    def __init__(self, lang: Lang, *args: object) -> None:
        super().__init__(message=BotMessage(content={
            Lang.JA: '即時は終了しています。再開するには `%resume` を使用して下さい。',
            Lang.EN: 'Sokuji was ended. Use `%resume` to continue sokuji.'
        }[lang]), *args)

class NotValidRaceNumError(SokujiError):
    def __init__(self, lang: Lang, *args: object) -> None:
        super().__init__(message=BotMessage(content={
            Lang.JA: '該当のレースがありません。',
            Lang.EN: 'Given race_num is not valid.'
        }[lang]), *args)

class NotValidRanksError(SokujiError):
    def __init__(self, lang: Lang, *args: object) -> None:
        super().__init__(message=BotMessage(content={
            Lang.JA: '入力された順位に誤りがあります。',
            Lang.EN: 'Given ranks are not valid.'
        }[lang]), *args)

class NoBackableContentError(SokujiError):
    def __init__(self, lang: Lang, *args: object) -> None:
        super().__init__(message=BotMessage(content={
            Lang.JA: 'backできる項目がありません。',
            Lang.EN: 'There is no content to back.'
        }[lang]), *args)

class TagNotFoundError(SokujiError):
    def __init__(self, lang: Lang, *args: object) -> None:
        super().__init__(message=BotMessage(content={
            Lang.JA: '存在しないタグが指定されています。',
            Lang.EN: 'Given tag is not found.'
        }[lang]), *args)

class NoArgumentToEditError(SokujiError):
    def __init__(self, *args: object) -> None:
        super().__init__(message=BotMessage(content=\
            'Give at least one argument to edit.\n'
            '編集項目が指定されていません。'
        ), *args)

class LeftRaceNumMinusError(SokujiError):
    def __init__(self, lang: Lang, *args: object) -> None:
        super().__init__(message=BotMessage(content={
            Lang.JA: '残りレース数は負にできません。',
            Lang.EN: 'Can\'t set minus left race num.'
        }[lang]), *args)

class ResultNotValidFormatError(SokujiError):
    def __init__(self, lang: Lang, *args: object) -> None:
        super().__init__(message=BotMessage(content={
            Lang.JA: '集計表作成は現在6v6にしか対応してません。',
            Lang.EN: 'This is now only for 6v6.'
        }[lang]), *args)

class ChannelCanNotSendError(SokujiError):
    def __init__(self, id: int, *args: object) -> None:
        super().__init__(message=BotMessage(content=\
            f'This bot has few permissions to send to <#{id}>.\n'
            f'<#{id}>に送信する権限がありません。'
        ), *args)

class NotValidRanksTextError(SokujiError):
    def __init__(self, *args: object) -> None:
        super().__init__(message=BotMessage(content=\
            'Not Valid Ranks.\nranksの表記に誤りがあります。'
        ), *args)
