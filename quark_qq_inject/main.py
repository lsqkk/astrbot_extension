from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star


class QuarkQQInject(Star):
    """将发送者的 QQ 号注入消息文本，使得 AI 在上下文中能看到 QQ 号。"""

    def __init__(self, context: Context):
        super().__init__(context)

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent):
        sender = getattr(event.message_obj, "sender", None)
        if not sender:
            return

        qq = (
            getattr(sender, "user_id", None)
            or getattr(sender, "qq", None)
            or getattr(sender, "uin", None)
        )
        if qq is not None:
            qq_str = str(qq)
        else:
            qq_str = event.get_sender_name() or "unknown"

        # 事件属性注入（供插件使用）
        event.injected_qq = qq_str

        # 消息文本注入（供 AI 看到），避免重复注入
        prefix = f"[QQ:{qq_str}]"
        if not event.message_str.startswith("[QQ:"):
            event.message_str = prefix + event.message_str

    async def terminate(self):
        pass
