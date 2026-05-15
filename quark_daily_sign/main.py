from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import random
import re

CN_TZ = timezone(timedelta(hours=8))

SIGN_LEVELS = ["大吉", "中吉", "小吉", "平", "小凶"]

THEMES = {
    "饭": (
        ["满汉全席签", "外卖到了签", "厨神附体签", "泡面大师签", "奶茶续命签", "深夜食堂签"],
        ["点杯奶茶", "好好吃饭", "尝试新菜谱", "细嚼慢咽", "和朋友约饭"],
        ["空腹硬撑", "暴饮暴食", "边吃边工作", "深夜吃撑", "点评软件刷太久"],
        ["干饭不积极，思想有问题。", "吃饱了才有力气减肥。"],
    ),
    "卷": (
        ["卷王之王签", "内卷漩涡签", "卷心菜签", "卷不动了签", "被迫内卷签", "躺卷二象性签"],
        ["专注提升自己", "制定计划", "早睡早起", "把事做完", "提高效率"],
        ["盲目跟风卷", "熬夜无效卷", "攀比焦虑", "同时开十个头", "假装努力"],
        ["卷可以，别把自己卷成春卷。", "真正的卷王卷的是自己，不是别人。"],
    ),
    "躺": (
        ["躺平大师签", "葛优同款签", "地心引力签", "躺赢人生签", "咸鱼翻身签", "摆烂艺术家签"],
        ["好好休息", "放空大脑", "听会音乐", "发会儿呆", "睡个午觉"],
        ["焦虑式躺平", "躺到腰疼", "躺完后悔", "边躺边内疚", "手机刷到头疼"],
        ["躺平不是放弃，是给灵魂放个假。", "偶尔躺平，是为了更好地站起来。"],
    ),
    "学": (
        ["学霸附体签", "知识入脑签", "冲刺期末签", "考研上岸签", "学无止境签", "图书馆钉子户签"],
        ["专注一小时", "做笔记", "整理错题", "回顾复习", "问老师问题"],
        ["假装学习", "收藏从未停止", "边学边玩手机", "通宵突击", "只翻第一页"],
        ["知识就是力量，但得先入脑。", "学不进去的时候，先学五分钟试试。"],
    ),
    "工": (
        ["打工人续命签", "搬砖能手签", "摸鱼被捉签", "周报生产签", "会议修罗场签", "工位钉子户签"],
        ["先做最重要的", "多喝水", "列待办清单", "定时站起来", "主动汇报"],
        ["同时开十个窗口", "摸鱼太明显", "拖延到deadline", "开会走神被抓", "邮件写一半"],
        ["搬砖要搬，但命更重要。", "工作是老板的，身体是自己的。"],
    ),
    "摸": (
        ["神级摸鱼签", "鱼王转世签", "Alt+Tab精通签", "厕所思想家签", "划水冠军签", "摸鱼美学签"],
        ["适时休息", "喝杯咖啡", "伸个懒腰", "看窗外风景", "和同事聊天"],
        ["摸到绩效警告", "被抓包", "摸到忘记正事", "太过嚣张", "ddl前通宵"],
        ["摸鱼有风险，划水需谨慎。", "高端的摸鱼，看起来像在认真工作。"],
    ),
    "氪": (
        ["钱包瘦身签", "剁手预警签", "重氪玩家签", "白嫖万岁签", "消费降级签", "购物车删除签"],
        ["理性消费", "先加购物车冷静", "记账", "等打折", "用优惠券"],
        ["深夜冲动消费", "信用卡刷爆", "为了凑单乱买", "跟风氪金", "超前消费"],
        ["氪金一时爽，还款火葬场。", "白嫖才是永恒的快乐。"],
    ),
    "欧": (
        ["欧皇附体签", "锦鲤本鲤签", "天选之人签", "一发入魂签", "幸运七连签", "紫气东来签"],
        ["试试手气", "买张彩票", "抽一发", "参加活动", "转发好运"],
        ["上头连续抽", "透支运气", "贪得无厌", "欧了还想更欧", "晒欧过度"],
        ["欧气要省着用，毕竟守恒的。", "今天的你，就是天选之人。"],
    ),
    "非": (
        ["非酋认证签", "保底人保底魂签", "霉运附体签", "抽卡沉船签", "非洲大酋长签", "反向欧皇签"],
        ["及时止损", "佛系随缘", "攒资源等下次", "看开点", "删游戏冷静"],
        ["头铁继续氪", "怪天怪地", "怒删账号", "跟人对喷", "怀疑人生"],
        ["非久必欧，欧久必非——但不是今天。", "保底也是一种稳定。"],
    ),
    "水": (
        ["水群王者签", "龙王附体签", "表情包大户签", "话痨十级签", "冷场终结者签", "话题制造机签"],
        ["多冒泡", "分享快乐", "发个表情包", "参与讨论", "回应新人"],
        ["过度刷屏", "挖坟旧消息", "刷屏广告", "刷屏吵架", "自言自语"],
        ["水群是对群最大的尊重。", "水可以，别把群淹了。"],
    ),
    "麻": (
        ["麻木大师签", "精神出走签", "大脑离线签", "当代麻瓜签", "已遁入空门签", "CPU过热签"],
        ["发会儿呆", "听首歌", "出去走走", "深呼吸", "暂停思考"],
        ["做重大决定", "回消息不过脑", "机械刷手机", "硬撑着工作", "开车走神"],
        ["麻了就歇会儿，不丢人。", "大脑需要重启，不是报废。"],
    ),
    "乐": (
        ["哈哈大笑签", "快乐源泉签", "喜剧人附体签", "多巴胺爆棚签", "笑出腹肌签", "今天有好戏签"],
        ["看搞笑视频", "和朋友聊天", "出门走走", "做喜欢的事", "听相声"],
        ["乐极生悲", "在严肃场合憋笑", "笑太大声吵到人", "笑完更空虚", "强行搞笑"],
        ["快乐是免费的，要多少有多少。", "笑一笑，十年少。"],
    ),
    "社": (
        ["社交恐怖分子签", "社牛症晚期签", "社恐保护签", "社交悍匪签", "人群焦点签", "尴尬化解师签"],
        ["主动打招呼", "约朋友吃饭", "微笑", "倾听别人", "参加活动"],
        ["过度分享", "强行找话题", "尬聊到底", "查户口式提问", "回避所有人"],
        ["社交可以，别把天聊死。", "真诚是最好的社交货币。"],
    ),
    "宅": (
        ["御宅族认证签", "家门封印签", "快递养活签", "床以外是远方签", "自闭修炼签", "无人岛岛主签"],
        ["追番看剧", "打游戏", "看书", "做手工", "研究冷知识"],
        ["昼夜颠倒", "不出门不洗澡", "只吃外卖", "不回复消息", "窗帘永不拉开"],
        ["宅可以，但记得晒晒太阳。", "宅到极致就是修行。"],
    ),
    "练": (
        ["健身打卡签", "自律上瘾签", "帕梅拉要我命签", "跑步机钉子户签", "铁馆常客签", "刘畊宏女孩签"],
        ["动起来", "拉伸放松", "定个小目标", "找个搭子", "听歌运动"],
        ["一天练太狠", "找借口休息", "动作不规范", "只练不拉伸", "三天打鱼两天晒网"],
        ["今天不动，明天更重。", "运动不是为了瘦，是为了快乐地吃。"],
    ),
    "混": (
        ["混子本混签", "得过且过签", "差不多先生签", "混一天算一天签", "及格万岁签", "躺平预备役签"],
        ["降低期望", "轻松应对", "完成比完美重要", "放过自己", "享受当下"],
        ["混到事情搞砸", "摆烂成习惯", "拖累队友", "毫无底线", "混完后悔"],
        ["混可以，别混到没底线。", "差不多也行，但别差太多。"],
    ),
    "旅": (
        ["说走就走签", "云旅游签", "机票打折签", "风景收藏家签", "攻略达人签", "特种兵旅行签"],
        ["看窗外远方", "规划下次旅行", "收拾行李箱", "拍张照", "尝试当地美食"],
        ["翘课翘班旅行", "不做攻略直接冲", "过度打卡", "为拍照冒险", "花钱超预算"],
        ["身体和灵魂，总有一个在路上。", "旅行的意义在于迷路。"],
    ),
    "睡": (
        ["眼皮限流签", "被窝召回签", "梦里环游签", "Quark关机签", "失眠退散签", "早睡冠军签"],
        ["放下手机", "关灯", "深呼吸", "听白噪音", "定个闹钟"],
        ["凌晨规划人生", "继续刷短视频", "喝了咖啡还睡", "焦虑失眠", "报复性熬夜"],
        ["人类不是24小时运营线路。", "睡觉是最好的充电。"],
    ),
    "发": (
        ["精神状态美丽签", "发疯文学签", "抽象大师签", "赛博嘶吼签", "理智下线签", "Quark发疯许可证签"],
        ["写下来发泄", "找朋友吐槽", "运动释放", "听重金属", "大喊十秒"],
        ["在工作群发疯", "删好友", "发完秒后悔", "深夜emo连发", "拉黑所有人"],
        ["发疯可以，记得收回来。", "偶尔发疯有益身心健康。"],
    ),
    "考": (
        ["逢考必过签", "锦鲤护体签", "选择题全对签", "作文超常签", "蒙的全对签", "学神附体签"],
        ["睡个好觉", "带齐文具", "先做会的题", "检查一遍", "深呼吸放松"],
        ["通宵复习", "互相传答案", "考前狂喝水", "带手机进考场", "放弃治疗"],
        ["会的全考，蒙的全对。", "考试不会因为你没准备好就改期。"],
    ),
    "云": (
        ["万事随缘签", "平平无奇签", "一切随云签", "来都来了签", "普通村民签", "风轻云淡签"],
        ["保持好心态", "顺其自然", "深呼吸", "微笑", "相信自己"],
        ["焦虑过度", "钻牛角尖", "和别人比较", "想太多", "乱立flag"],
        ["云卷云舒，随遇而安。", "今天也是普通但珍贵的一天。"],
    ),
}

GENERIC = (
    ["随机掉落签", "薛定谔的好运签", "测不准原理签", "平行时空另一个你已经成功了签", "宇宙的终极答案是42签"],
    ["深呼吸", "相信自己", "先做再说"],
    ["过度思考", "和别人比较"],
    ["未来不可测，但现在你可以选。", "签不够用了，将就一下吧。"],
)

VALID_THEMES = set(THEMES.keys())


class QuarkDailySign(Star):
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
        self.cache_file.write_text(
            json.dumps(self.cache, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _today(self):
        return datetime.now(CN_TZ).strftime("%Y-%m-%d")

    def _sender_id(self, event: AstrMessageEvent) -> str:
        qq = getattr(event, "injected_qq", None)
        if qq:
            return qq
        sender = getattr(event.message_obj, "sender", None)
        for attr in ("user_id", "id", "qq", "uid"):
            value = getattr(sender, attr, None) if sender else None
            if value:
                return str(value)
        return event.get_sender_name() or "unknown"

    def _group_id(self, event: AstrMessageEvent) -> str:
        return str(getattr(event.message_obj, "group_id", "") or "private")

    def _extract_theme(self, msg: str) -> str | None:
        """提取签主题，要求 X签 必须出现在消息末尾（忽略尾部空白）。"""
        text = re.sub(r"\[QQ:\d+\]|\[At:\d+\]", "", msg or "").strip()
        # 签类型必须在消息末尾（尾部允许空白和标点）
        m = re.search(r"([一-龥A-Za-z0-9]{1,8})签\s*$", text)
        if not m:
            return None
        theme = m.group(1)
        # 只识别预定义的主题
        if theme not in VALID_THEMES:
            return None
        return theme

    def _profile(self, theme: str):
        return THEMES.get(theme, GENERIC)

    def _make_sign(self, theme: str, seed: str):
        rnd = random.Random(seed)
        names, yi, ji, notes = self._profile(theme)
        return {
            "theme": theme,
            "name": rnd.choice(names),
            "level": rnd.choice(SIGN_LEVELS),
            "yi": "、".join(rnd.sample(yi, k=min(3, len(yi)))),
            "ji": "、".join(rnd.sample(ji, k=min(3, len(ji)))),
            "note": rnd.choice(notes),
        }

    def _format(self, sign: dict, repeated: bool = False) -> str:
        theme = sign["theme"]
        label = "Quark签" if theme == "云" else f"Quark{theme}签"
        content_lines = [
            f"签文：{sign['name']}",
            f"签面：{sign['level']}",
            f"宜：{sign['yi']}",
            f"忌：{sign['ji']}",
            f"Quark批注：{sign['note']}",
        ]
        max_w = max(len(l) for l in content_lines)
        border = "─" * (max_w + 2)
        pad = " " * (max_w - len(label))
        lines = []
        if repeated:
            lines.append("你今天已经盖过戳啦，下面是今天的签文：")
        lines.append(f"┌{border}┐")
        lines.append(f"│ {label}{pad} │")
        lines.append(f"├{border}┤")
        for line in content_lines:
            lines.append(f"│ {line.ljust(max_w)} │")
        lines.append(f"└{border}┘")
        return "\n".join(lines)

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
