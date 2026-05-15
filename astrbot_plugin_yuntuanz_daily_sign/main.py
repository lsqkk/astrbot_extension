from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import random
import re

CN_TZ = timezone(timedelta(hours=8))
SIGN_LEVELS = ["大吉", "中吉", "小吉", "平", "微妙", "小凶"]

THEMES = {
    "史": (
        ["秦始皇都没你统一得慢签", "乱纪元·恒纪元签", "史官提笔又放下签", "函谷关排队签"],
        ["先拿下一城", "把事情拆小"],
        ["同时开三条战线", "幻想一统六国"],
        ["今天先别称帝，先把眼前这城过了。"],
    ),
    "臭": (
        ["通风见喜签", "空气质量待观测签", "风和日丽但不保证签", "臭中带吉签"],
        ["开窗", "洗澡"],
        ["预测明天", "密闭空间嘴硬"],
        ["臭臭的一天也可能风和日丽，先把手头事干完。"],
    ),
    "吴": (
        ["吴事发生签", "吴中生有签", "吴法吴天签", "吴语伦次签"],
        ["装作无事发生", "低调通过"],
        ["主动解释太多", "把梗讲死"],
        ["今天的吴力波动稳定，适合低调通过。"],
    ),
    "牢": (
        ["放风十分钟签", "电子脚镣签", "今日缓刑签", "牢饭还行签"],
        ["休息十分钟", "吃点东西"],
        ["自愿加刑", "空腹坐牢"],
        ["牢可以坐，饭不能不吃。"],
    ),
    "癫": (
        ["癫中有序签", "精神脱轨签", "神经元蹦迪签", "语义漂移签"],
        ["把脑洞写下来", "找人说两句"],
        ["半夜做重大决定", "达速癫狂"],
        ["可以癫，但要有运行图。"],
    ),
    "唐": (
        ["唐完了但没全完签", "唐突发言签", "唐僧念经签", "唐而不倒签"],
        ["少说两句", "先做一件事"],
        ["把尴尬解释到更尴尬", "持续唐突"],
        ["唐可以，别连续剧化。"],
    ),
    "复习": (
        ["临阵磨云签", "选择题救命签", "公式回魂签", "知识点诈尸签"],
        ["刷错题", "背高频点"],
        ["列完美计划然后不执行", "同时开三本书"],
        ["考试不会因为你没准备好就改期，现在跑还来得及。"],
    ),
    "考试": (
        ["选择题救命签", "卷面玄学签", "及格线凝视签", "知识点诈尸签"],
        ["刷错题", "早点睡"],
        ["凌晨重开人生", "押题押到玄学区"],
        ["先把会的拿稳，不会的交给命运但别全交。"],
    ),
    "发疯": (
        ["疯完记得吃饭签", "小云发疯许可证签", "抽象合法签", "赛博尖叫签"],
        ["怪叫十秒", "吃饭"],
        ["把发疯当长期规划", "饿着发疯"],
        ["可以疯，别饿着疯。"],
    ),
    "摸鱼": (
        ["低调划水签", "窗口切换熟练签", "鱼群掩护签", "假装在忙签"],
        ["小摸", "及时收手"],
        ["摸到忘记自己是谁", "把船摸沉"],
        ["摸鱼可以，别把船摸沉。"],
    ),
    "睡觉": (
        ["眼皮限流签", "被窝召回签", "梦里换乘签", "小云关机签"],
        ["早点睡", "放下手机"],
        ["凌晨规划人生", "继续刷短视频"],
        ["人类不是 24 小时运营线路。"],
    ),
    "云": (
        ["普通平邮签", "星星盖戳签", "邮路畅通签", "轻微晚点签"],
        ["吃饭", "喝水"],
        ["空腹硬刚", "深夜规划人生"],
        ["平邮也会到，别催自己飞。"],
    ),
}

GENERIC = (
    ["小概率中奖签", "普通平邮签", "低速运行签", "邮戳盖糊签", "意外顺路签", "今日别硬刚签"],
    ["吃饭", "喝水", "先保存"],
    ["空腹硬刚", "过度解释"],
    ["这个签很抽象，但还能投递。"],
)


class YuntuanzDailySign(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.data_dir / "daily_sign_cache.json"
        self.cache = self._load_cache()

    def _load_cache(self):
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        self.cache_file.write_text(json.dumps(self.cache, ensure_ascii=False, indent=2), encoding="utf-8")

    def _today(self):
        return datetime.now(CN_TZ).strftime("%Y-%m-%d")

    def _sender_id(self, event):
        sender = getattr(event.message_obj, "sender", None)
        for attr in ("user_id", "id", "qq", "uid"):
            value = getattr(sender, attr, None)
            if value:
                return str(value)
        return str(event.get_sender_name())

    def _group_id(self, event):
        return str(getattr(event.message_obj, "group_id", "") or "private")

    def _extract_theme(self, msg):
        text = re.sub(r"\[At:\d+\]", "", msg or "").replace("云团子", "").strip()
        if "饭签" in text or "交梗" in text:
            return None
        m = re.search(r"([\u4e00-\u9fa5A-Za-z0-9]{1,8})签", text)
        if not m:
            return None
        theme = m.group(1).replace("今日", "").strip()
        return theme or "云"

    def _profile(self, theme):
        if theme in THEMES:
            return THEMES[theme]
        return THEMES.get(theme[0], GENERIC)

    def _make_sign(self, theme, seed):
        rnd = random.Random(seed)
        names, yi, ji, notes = self._profile(theme)
        return {
            "theme": theme,
            "name": rnd.choice(names),
            "level": rnd.choice(SIGN_LEVELS),
            "yi": "、".join(rnd.sample(yi, k=min(2, len(yi)))),
            "ji": "、".join(rnd.sample(ji, k=min(2, len(ji)))),
            "note": rnd.choice(notes),
        }

    def _format(self, sign, repeated=False):
        prefix = "你今天已经盖过戳啦：\n" if repeated else ""
        title = "云签" if sign["theme"] == "云" else f"{sign['theme']}签"
        return (
            f"{prefix}今日{title}：{sign['name']}\n"
            f"签面：{sign['level']}\n"
            f"宜：{sign['yi']}\n"
            f"忌：{sign['ji']}\n"
            f"小云批注：{sign['note']}"
        )

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent):
        theme = self._extract_theme(event.message_str)
        if not theme:
            return

        today = self._today()
        key = f"{today}:{self._group_id(event)}:{self._sender_id(event)}"

        if key in self.cache:
            yield event.plain_result(self._format(self.cache[key], repeated=True))
            event.stop_event()
            return

        seed = hashlib.sha256(key.encode("utf-8")).hexdigest()
        sign = self._make_sign(theme, seed)
        self.cache[key] = sign
        self._save_cache()

        yield event.plain_result(self._format(sign))
        event.stop_event()

    async def terminate(self):
        self._save_cache()
