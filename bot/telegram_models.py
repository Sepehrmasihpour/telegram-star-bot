from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, Any, List, Union


class Chat(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    id: int
    type: Literal["private"]
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None


class User(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    username: Optional[str] = None


EntityType = Literal[
    "mention",  # @username
    "hashtag",  # #hashtag or #hashtag@chatusername
    "cashtag",  # $USD or $USD@chatusername
    "bot_command",  # /start@jobs_bot
    "url",  # https://telegram.org
    "email",  # do-not-reply@telegram.org
    "phone_number",  # +1-212-555-0123
    "bold",
    "italic",
    "underline",
    "strikethrough",
    "spoiler",
    "blockquote",
    "expandable_blockquote",
    "code",  # monowidth string
    "pre",  # monowidth block
    "text_link",  # clickable text URL
    "text_mention",  # for users without usernames
    "custom_emoji",  # inline custom emoji stickers
]


class MessageEntity(BaseModel):
    type: EntityType
    offset: int
    length: int
    url: Optional[str] = None
    user: Optional[User] = User


class KeyboardButton(BaseModel):
    text: str


class ReplyKeyboardMarkup(BaseModel):
    keyboard: List[List[KeyboardButton]]
    is_persistant: Optional[bool] = (
        False  # * defaults to false if true the bot will always show the keyboard when the keyboard is not on
    )
    resize_keyboard: Optional[bool] = False  # * resize the keyboard to fit well
    one_time_keyboard: Optional[bool] = (
        False  # * the keyboard will hide when used with custom logic
    )
    input_field_placeholder: Optional[str] = False


class InlineKeyboardButton(BaseModel):
    text: str
    url: Optional[str] = None
    callback_date: str
    copy_text: Optional[str] = None


class InlineKeyboardMarkup(BaseModel):
    inline_keyboard: list[list[InlineKeyboardButton]]


class CopyTextButton(BaseModel):
    text: str


class ForceReply(BaseModel):
    input_field_placeholder: Optional[str] = str


class ReplyKeyboardRemove(BaseModel):
    remove_keyboard: Literal[True]


class BotCommand(BaseModel):
    command: str
    description: str


class Message(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    message_id: int
    from_: User = Field(alias="from")
    date: int
    chat: Chat
    forward_origin: Any
    #!forward_origin is intended for sending an error if not none the message is forwarded
    #! if later we want to something different with forward messages we need to change this
    text: str  # * later this should be optional
    entities: Optional[MessageEntity] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None


class MaybeInaccessibleMessage(Message): ...


class CallbackQuery(BaseModel):
    id: str
    from_: User = Field(alias="from")
    message: Optional[MaybeInaccessibleMessage] = None
    data: Optional[str] = None


class Update(BaseModel):
    update_id: int
    message: Optional[Message] = None
    edited_message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None


# * below are the data models for the api methdos


class SendMessage(BaseModel):
    chat_id: int
    text: str
    entities: Optional[List[MessageEntity]] = None
    parse_mode: Optional[str] = None
    protect_content: Optional[bool] = False
    reply_markup: Optional[
        Union[
            InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply
        ]
    ] = None
