from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import random as stdlib_random
import re

CN_TZ = timezone(timedelta(hours=8))

# ── 签主题 ──────────────────────────────────────────────

SIGN_THEMES = {
    "饭": (
        ["满汉全席签", "外卖到了签", "厨神附体签", "泡面大师签", "奶茶续命签", "深夜食堂签",
         "白嫖试吃签", "自助餐回本签", "烧烤摊战神签"],
        ["点杯奶茶", "好好吃饭", "尝试新菜谱", "细嚼慢咽", "和朋友约饭"],
        ["空腹硬撑", "暴饮暴食", "边吃边工作", "深夜吃撑", "点评软件刷太久"],
        ["干饭不积极，思想有问题。", "吃饱了才有力气减肥。", "今天你也是米其林三星预备役。"],
    ),
    "卷": (
        ["卷王之王签", "内卷漩涡签", "卷心菜签", "卷不动了签", "被迫内卷签",
         "躺卷二象性签", "反卷斗士签", "卷中卷签"],
        ["专注提升自己", "制定可行计划", "早睡早起", "把事做完", "提高效率"],
        ["盲目跟风卷", "熬夜无效卷", "攀比焦虑", "同时开十个头", "假装努力"],
        ["卷可以，别把自己卷成春卷。", "真正的卷王卷的是自己，不是别人。",
         "卷不动就躺，不丢人。"],
    ),
    "躺": (
        ["躺平大师签", "葛优同款签", "地心引力签", "躺赢人生签", "咸鱼翻身签",
         "摆烂艺术家签", "床垫质量检测员签", "躺学博士签"],
        ["好好休息", "放空大脑", "听会音乐", "发会儿呆", "睡个午觉"],
        ["焦虑式躺平", "躺到腰疼", "躺完后悔", "边躺边内疚", "手机刷到头疼"],
        ["躺平不是放弃，是给灵魂放个假。", "偶尔躺平，是为了更好地站起来。"],
    ),
    "学": (
        ["学霸附体签", "知识入脑签", "冲刺期末签", "考研上岸签", "学无止境签",
         "图书馆钉子户签", "通宵自习室荣誉会员签", "笔记本写满签"],
        ["专注一小时", "做笔记", "整理错题", "回顾复习", "问老师问题"],
        ["假装学习", "收藏从未停止", "边学边玩手机", "通宵突击", "只翻第一页"],
        ["知识就是力量，但得先入脑。", "学不进去的时候，先学五分钟试试。",
         "学习是唯一稳赚不赔的投资。"],
    ),
    "工": (
        ["打工人续命签", "搬砖能手签", "摸鱼被捉签", "周报生产签", "会议修罗场签",
         "工位钉子户签", "PPT美化大师签", "茶水间闲聊王者签"],
        ["先做最重要的", "多喝水", "列待办清单", "定时站起来", "主动汇报"],
        ["同时开十个窗口", "摸鱼太明显", "拖延到deadline", "开会走神被抓", "邮件写一半"],
        ["搬砖要搬，但命更重要。", "工作是老板的，身体是自己的。",
         "打工可以，别把命打进去。"],
    ),
    "摸": (
        ["神级摸鱼签", "鱼王转世签", "Alt+Tab精通签", "厕所思想家签", "划水冠军签",
         "摸鱼美学签", "假装认真第一名签", "上班带薪拉屎签"],
        ["适时休息", "喝杯咖啡", "伸个懒腰", "看窗外风景", "和同事聊天"],
        ["摸到绩效警告", "被抓包", "摸到忘记正事", "太过嚣张", "ddl前通宵"],
        ["摸鱼有风险，划水需谨慎。", "高端的摸鱼，看起来像在认真工作。",
         "摸鱼是一门艺术，讲究收放自如。"],
    ),
    "氪": (
        ["钱包瘦身签", "剁手预警签", "重氪玩家签", "白嫖万岁签", "消费降级签",
         "购物车清理大师签", "信用卡账单凝视签", "拼多多砍一刀签"],
        ["理性消费", "先加购物车冷静三天", "记账", "等比价", "用优惠券"],
        ["深夜冲动消费", "信用卡刷爆", "为了凑单乱买", "跟风氪金", "超前消费"],
        ["氪金一时爽，还款火葬场。", "白嫖才是永恒的快乐。",
         "消费主义的尽头是拼多多。"],
    ),
    "水": (
        ["水群王者签", "龙王附体签", "表情包大户签", "话痨十级签", "冷场终结者签",
         "话题制造机签", "99+未读守护者签", "复读机转世签"],
        ["多冒泡", "分享快乐", "发个表情包", "参与讨论", "回应新人"],
        ["过度刷屏", "挖坟旧消息", "刷屏吵架", "自言自语太多", "打扰别人休息"],
        ["水群是对群最大的尊重。", "水可以，别把群淹了。",
         "真正的龙王懂得适时沉默。"],
    ),
    "乐": (
        ["哈哈大笑签", "快乐源泉签", "喜剧人附体签", "多巴胺爆棚签", "笑出腹肌签",
         "今天有好戏签", "快乐传染源签", "嘴角疯狂上扬签"],
        ["看搞笑视频", "和朋友聊天", "出门走走", "做喜欢的事", "听相声"],
        ["乐极生悲", "在严肃场合憋笑", "笑太大声吵到人", "笑完更空虚", "强行搞笑"],
        ["快乐是免费的，要多少有多少。", "笑一笑，十年少。",
         "今天不笑，更待何时。"],
    ),
    "宅": (
        ["御宅族认证签", "家门封印签", "快递养活签", "床以外是远方签", "自闭修炼签",
         "无人岛岛主签", "窗帘永不拉开签", "外卖会员黄金VIP签"],
        ["追番看剧", "打游戏", "看书", "做手工", "研究冷知识"],
        ["昼夜颠倒", "不出门不洗澡", "只吃外卖", "不回复消息", "窗帘永不拉开"],
        ["宅可以，但记得晒晒太阳。", "宅到极致就是修行。",
         "家里蹲也是一种生活方式。"],
    ),
    "练": (
        ["健身打卡签", "自律上瘾签", "帕梅拉要我命签", "跑步机钉子户签", "铁馆常客签",
         "刘畊宏女孩签", "瑜伽冥想入门签", "俯卧撑做五个就累签"],
        ["动起来", "拉伸放松", "定个小目标", "找个搭子", "听歌运动"],
        ["一天练太狠", "找借口休息", "动作不规范", "只练不拉伸", "三天打鱼两天晒网"],
        ["今天不动，明天更重。", "运动不是为了瘦，是为了快乐地吃。",
         "健身十分钟，拍照两小时。"],
    ),
    "混": (
        ["混子本混签", "得过且过签", "差不多先生签", "混一天算一天签", "及格万岁签",
         "躺平预备役签", "摸鱼转混子签", "混出了水平签"],
        ["降低期望", "轻松应对", "完成比完美重要", "放过自己", "享受当下"],
        ["混到事情搞砸", "摆烂成习惯", "拖累队友", "毫无底线", "混完后悔"],
        ["混可以，别混到没底线。", "差不多也行，但别差太多。",
         "混是一门学问，讲究恰到好处。"],
    ),
    "旅": (
        ["说走就走签", "云旅游签", "机票打折签", "风景收藏家签", "攻略达人签",
         "特种兵旅行签", "酒店试睡员签", "行李箱永不离手签"],
        ["看窗外远方", "规划下次旅行", "收拾行李箱", "拍张照", "尝试当地美食"],
        ["翘课翘班旅行", "不做攻略直接冲", "过度打卡", "为拍照冒险", "花钱超预算"],
        ["身体和灵魂，总有一个在路上。", "旅行的意义在于迷路。",
         "世界那么大，钱包那么小。"],
    ),
    "睡": (
        ["眼皮限流签", "被窝召回签", "梦里环游签", "Quark关机签", "失眠退散签",
         "早睡冠军签", "枕头封印签", "回笼觉大师签"],
        ["放下手机", "关灯", "深呼吸", "听白噪音", "定个闹钟"],
        ["凌晨规划人生", "继续刷短视频", "喝了咖啡还睡", "焦虑失眠", "报复性熬夜"],
        ["人类不是24小时运营线路。", "睡觉是最好的充电。",
         "熬夜不会让你多活一天，但会让你少活一天。"],
    ),
    "发": (
        ["精神状态美丽签", "发疯文学签", "抽象大师签", "赛博嘶吼签", "理智下线签",
         "Quark发疯许可证签", "已疯勿扰签", "精神状态堪忧签"],
        ["写下来发泄", "找朋友吐槽", "运动释放", "听重金属", "大喊十秒"],
        ["在工作群发疯", "删好友", "发完秒后悔", "深夜emo连发", "拉黑所有人"],
        ["发疯可以，记得收回来。", "偶尔发疯有益身心健康。",
         "不在沉默中爆发，就在沉默中更沉默。"],
    ),
    "考": (
        ["逢考必过签", "锦鲤护体签", "选择题全对签", "作文超常签", "蒙的全对签",
         "学神附体签", "答题卡填涂艺术家签", "考神临时抱佛脚签"],
        ["睡个好觉", "带齐文具", "先做会的题", "检查一遍", "深呼吸放松"],
        ["通宵复习", "互相传答案", "考前狂喝水", "带手机进考场", "放弃治疗"],
        ["会的全考，蒙的全对。", "考试不会因为你没准备好就改期。",
         "考完别对答案，对完影响下一科心情。"],
    ),
}

VALID_THEMES = set(SIGN_THEMES.keys())

# ── 今日运势 ────────────────────────────────────────────

FORTUNE_LEVELS = [
    ("大雄", 0.05, "今天是野比大雄附体"),
    ("大凶", 0.06, "诸事不宜，小心为上"),
    ("小凶", 0.10, "乌云密布，谨慎行事"),
    ("平", 0.18, "平平淡淡才是真"),
    ("小吉", 0.18, "小小的幸运在等你"),
    ("中吉", 0.17, "渐入佳境，稳步前进"),
    ("大吉", 0.13, "一帆风顺，好运连连"),
    ("超级吉", 0.08, "天选之人，欧皇附体"),
    ("妲己", 0.05, "祸国殃民级别的运气"),
]

FORTUNE_YI_POOL = [
    "写作业", "复习功课", "敲代码", "打游戏", "运动健身",
    "社交", "早睡早起", "看书", "看番追剧", "出去玩",
    "约饭", "桌游", "上号", "学新技能", "做手工",
    "听音乐", "冥想", "打扫卫生", "整理笔记", "泡图书馆",
    "预习", "刷题", "背单词", "写日记", "画画",
    "编程", "搞钱", "表白", "尝试新事物", "立flag",
]

FORTUNE_JI_POOL = [
    "熬夜", "翘课", "摸鱼", "冲动消费", "摆烂",
    "拖延", "通宵打游戏", "暴饮暴食", "不吃东西", "欠钱",
    "立flag", "课上睡觉", "抄作业", "内卷焦虑", "胡思乱想",
    "赖床", "刷短视频停不下来", "忘记ddl", "不回消息", "吃太多零食",
    "裸考", "迟到", "发誓", "借钱给别人", "随意承诺",
]

FORTUNE_NOTES = [
    "运气是实力的一部分，但实力才是硬道理。",
    "今天也是普通但珍贵的一天。",
    "你相信什么，就会遇见什么。",
    "好运气藏在你的每一个选择里。",
    "生活的惊喜往往在不经意间出现。",
    "不管什么运势，开心最重要。",
    "今天的你，比昨天更好就够了。",
    "运势仅供参考，行动才有改变。",
]

# ── 决策 ──────────────────────────────────────────────

DECISIONS = [
    "冲！", "别去！", "必须的！", "算了吧……",
    "再想想，不着急。", "去做！不问结果。",
    "听你内心的声音。", "别怂，就是干！",
    "建议先睡一觉再说。", "可以，但别后悔。",
    "不行，绝对不行。", "试试又不会掉块肉。",
    "相信自己，你可以的。", "建议放弃，及时止损。",
    "冲冲冲！", "躺平吧，别折腾了。",
]

# ── 辅助 ──────────────────────────────────────────────

def _rng(seed: str, n: int, k: int = 1):
    """基于种子的采样，保证同种子结果一致。"""
    rnd = stdlib_random.Random(seed)
    return rnd.sample(range(n), k)


class QuarkDailySign(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.data_dir / "daily_sign_cache.json"
        self.fortune_cache_file = self.data_dir / "fortune_cache.json"
        self.cache = self._load_json(self.cache_file)
        self.fortune_cache = self._load_json(self.fortune_cache_file)

    # ── 持久化 ────────────────────────────────────────

    def _load_json(self, path: Path):
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _save_json(self, path: Path, data: dict):
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

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

    def _clean_msg(self, msg: str) -> str:
        return re.sub(r"\[QQ:\d+\]|\[At:\d+\]", "", msg or "").strip()

    # ── 抽签 ──────────────────────────────────────────

    def _do_sign(self, theme: str, seed: str) -> dict:
        rnd = stdlib_random.Random(seed)
        names, yi, ji, notes = SIGN_THEMES[theme]
        level = rnd.choice(["大吉", "中吉", "小吉", "平", "微妙", "小凶"])
        return {
            "theme": theme,
            "name": rnd.choice(names),
            "level": level,
            "yi": " · ".join(rnd.sample(yi, k=min(3, len(yi)))),
            "ji": " · ".join(rnd.sample(ji, k=min(3, len(ji)))),
            "note": rnd.choice(notes),
        }

    def _format_sign(self, sign: dict, repeated: bool = False) -> str:
        theme = sign["theme"]
        label = "Quark签" if theme == "云" else f"Quark{theme}签"
        lines = []
        if repeated:
            lines.append("⚠️ 你今天已经抽过这个签啦，下面是今天的签文：")
        lines.append(f"📜 {label}")
        lines.append(f"🏷️ 签文：{sign['name']}")
        lines.append(f"⭐ 签面：{sign['level']}")
        lines.append(f"✅ 宜：{sign['yi']}")
        lines.append(f"❌ 忌：{sign['ji']}")
        lines.append(f"💬 Quark批注：{sign['note']}")
        return "\n".join(lines)

    def _list_signs(self) -> str:
        items = " · ".join(sorted(f"{t}签" for t in VALID_THEMES))
        return f"📜 当前支持的签：\n{items}\n\n发送「XX签」即可抽取（签在末尾），发送「抽签」随机出签～"

    # ── 今日运势 ──────────────────────────────────────

    def _do_fortune(self, seed: str) -> str:
        rnd = stdlib_random.Random(seed)
        # 加权选取运势等级
        level_names = [lv[0] for lv in FORTUNE_LEVELS]
        weights = [lv[1] for lv in FORTUNE_LEVELS]
        level_idx = rnd.choices(range(len(level_names)), weights=weights, k=1)[0]
        level_name, _, level_title = FORTUNE_LEVELS[level_idx]

        # 根据等级决定宜/忌数量
        ji_display = None
        if level_idx >= len(FORTUNE_LEVELS) - 2:  # 超级吉 / 妲己
            yi_count = 5
            ji_display = "✨ 诸事皆宜"
        elif level_name in ("大吉",):
            yi_count = 4
            ji_display = "✨ 诸事皆宜"
        elif level_name in ("中吉", "小吉"):
            yi_count = 3
            ji_count = 2
        elif level_name == "平":
            yi_count = 2
            ji_count = 2
        elif level_name == "小凶":
            yi_count = 2
            ji_count = 3
        elif level_name == "大凶":
            yi_count = 1
            ji_count = 4
        else:  # 大雄
            yi_count = 1
            ji_count = 4

        # 用不同 offset 采样避免宜/忌重叠
        yi_seed = seed + "_yi"
        ji_seed = seed + "_ji"
        yi_items = stdlib_random.Random(yi_seed).sample(FORTUNE_YI_POOL, yi_count)

        lines = [f"🔮 今日运势"]
        lines.append(f"📊 运势：{level_name}")

        # 用不同的随机种来选title
        title_seed = seed + "_t"
        is_lucky = level_name in ("大吉", "超级吉", "妲己") or level_idx >= 5
        if is_lucky and level_name != "妲己":
            lucky_titles = ["好运连连", "万事顺遂", "心想事成", "锦鲤附体", "诸事皆宜"]
            title = stdlib_random.Random(title_seed).choice(lucky_titles)
            lines.append(f"🏆 {title}")
        elif level_name == "妲己":
            daji_titles = ["祸国殃民", "倾国倾城", "妖孽级好运", "逆天改命", "众生平等"]
            title = stdlib_random.Random(title_seed).choice(daji_titles)
            lines.append(f"🏆 {title}")
        else:
            lines.append(f"🏆 {level_title}")

        lines.append(f"✅ 宜：{' · '.join(yi_items)}")

        if ji_display:
            lines.append(f"❌ 忌：{ji_display}")
        else:
            ji_items = stdlib_random.Random(ji_seed).sample(FORTUNE_JI_POOL, ji_count)
            lines.append(f"❌ 忌：{' · '.join(ji_items)}")

        note = stdlib_random.Random(seed + "_n").choice(FORTUNE_NOTES)
        lines.append(f"💬 箴言：{note}")
        return "\n".join(lines)

    # ── 消息处理 ──────────────────────────────────────

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent):
        msg = self._clean_msg(event.message_str)
        if not msg:
            return

        # ── 抽签列表 ──
        if "抽签列表" in msg:
            yield event.plain_result(self._list_signs())
            event.stop_event()
            return

        # ── 特定签 (X签 必须在末尾) ──
        m = re.search(r"([一-龥A-Za-z0-9]{1,8})签\s*$", msg)
        if m and m.group(1) in VALID_THEMES:
            theme = m.group(1)
            today = self._today()
            key = f"sign:{today}:{self._group_id(event)}:{self._sender_id(event)}:{theme}"
            if key in self.cache:
                yield event.plain_result(self._format_sign(self.cache[key], repeated=True))
                event.stop_event()
                return
            seed = hashlib.sha256(key.encode("utf-8")).hexdigest()
            sign = self._do_sign(theme, seed)
            sign["theme"] = theme
            self.cache[key] = sign
            self._save_json(self.cache_file, self.cache)
            yield event.plain_result(self._format_sign(sign))
            event.stop_event()
            return

        # ── 随机抽签 (消息含"抽签") ──
        if "抽签" in msg:
            theme = stdlib_random.Random(msg + str(datetime.now(CN_TZ).timestamp())).choice(list(VALID_THEMES))
            today = self._today()
            key = f"sign:{today}:{self._group_id(event)}:{self._sender_id(event)}:{theme}"
            if key in self.cache:
                # 如果随机到已抽过的，换一个没抽过的主题
                today_prefix = f"sign:{today}:{self._group_id(event)}:{self._sender_id(event)}:"
                all_keys = {k.split(":")[-1] for k in self.cache if k.startswith(today_prefix)}
                available = VALID_THEMES - all_keys
                if available:
                    theme = stdlib_random.Random(msg).choice(list(available))
                    key = f"sign:{today}:{self._group_id(event)}:{self._sender_id(event)}:{theme}"
                else:
                    yield event.plain_result("⚠️ 你今天已经把所有的签都抽过啦，明天再来吧～")
                    event.stop_event()
                    return
            seed = hashlib.sha256(key.encode("utf-8")).hexdigest()
            sign = self._do_sign(theme, seed)
            sign["theme"] = theme
            self.cache[key] = sign
            self._save_json(self.cache_file, self.cache)
            yield event.plain_result(self._format_sign(sign))
            event.stop_event()
            return

        # ── 骰子 ──
        if re.search(r"[骰色]子|dice|roll", msg, re.IGNORECASE):
            val = stdlib_random.Random(msg + str(datetime.now(CN_TZ).timestamp())).randint(1, 6)
            faces = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
            yield event.plain_result(f"🎲 你掷出了 **{val}** {faces[val - 1]}")
            event.stop_event()
            return

        # ── 抛硬币 ──
        if re.search(r"抛硬币|硬币|掷硬币", msg):
            val = stdlib_random.Random(msg).choice(["正面", "反面"])
            yield event.plain_result(f"🪙 {val}！")
            event.stop_event()
            return

        # ── 做决定 ──
        if ("做决定" in msg) or ("要不要" in msg and re.search(r"夸克|quark", msg, re.IGNORECASE)):
            decision = stdlib_random.Random(msg).choice(DECISIONS)
            yield event.plain_result(f"🤔 让我想想……\n➡️ **{decision}**")
            event.stop_event()
            return

        # ── 今日运势 ──
        if "今日运势" in msg:
            today = self._today()
            key = f"fortune:{today}:{self._group_id(event)}:{self._sender_id(event)}"
            if key in self.fortune_cache:
                yield event.plain_result("⚠️ 你今天已经看过运势啦：\n" + self.fortune_cache[key])
                event.stop_event()
                return
            seed = hashlib.sha256(key.encode("utf-8")).hexdigest()
            result = self._do_fortune(seed)
            self.fortune_cache[key] = result
            self._save_json(self.fortune_cache_file, self.fortune_cache)
            yield event.plain_result(result)
            event.stop_event()
            return

    async def terminate(self):
        self._save_json(self.cache_file, self.cache)
        self._save_json(self.fortune_cache_file, self.fortune_cache)
