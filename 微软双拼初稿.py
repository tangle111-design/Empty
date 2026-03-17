import subprocess
import sys

# 自动安装缺失的第三方库
for pkg in ['customtkinter', 'pypinyin']:
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

import customtkinter as ctk
import random
import time
from pypinyin import pinyin, Style
'''
TODO
改为微软双拼方案
增加错题练习
增加数据分析
增加小鹤方案
增加文章模式
'''
# TODO
# NOTE
# FIXME
# HACK
# BUG
# XXX
# 这些注释标签可以帮助你在代码中标记需要改进、修复或优化的部分，方便后续维护和迭代。

# --- 配置部分 ---
ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

# --- 微软双拼映射表 ---
# 声母映射 (只有非单字符的声母需要转换，其余即为键盘对应字母)
INITIALS_MAP = {"zh": "v", "ch": "i", "sh": "u"}

# 韵母映射
FINALS_MAP = {
    # 单字母韵母
        "a": "a", 
        "o": "o", 
        "e": "e", 
        "i": "i", 
        "u": "u", 
        "v": "y", "ü": "y",  
        
        # 双字母及以上韵母
        "ai": "l", 
        "ei": "z", 
        "ui": "v", 
        "ao": "k", 
        "ou": "b", 
        "iu": "q",
        "ie": "x", 
        "ve": "t", "üe": "t", "ue": "t", 
        "er": "r",
        
        "an": "j", 
        "en": "f", 
        "in": "n", 
        "un": "p", 
        "vn": "p", "ün": "p", 
        
        "ang": "h", 
        "eng": "g", 
        "ing": ";",           # 注意：微软双拼的 ing 映射在分号键上
        "ong": "s", 
        "iong": "s",
        
        "ia": "w", 
        "iao": "c", 
        "ian": "m", 
        "iang": "d", 
        
        "ua": "w", 
        "uai": "y", 
        "uan": "r", 
        "uang": "d", 
        "uo": "o"
}
# ==========================================
# 附加说明：微软双拼的零声母（没有声母的拼音）规则：
# 微软双拼固定使用字母 `o` 作为零声母的占位引导符（代替声母键）。
# 
# 1. 单字母韵母 (a, o, e)：前加 o。
#    例如：a -> oa, o -> oo, e -> oe
# 2. 双字母/多字母韵母 (ai, an, ang 等)：首键固定为 o，第二码为韵母映射键。
#    例如：ai -> o + l(ai) -> ol
#          ang -> o + h(ang) -> oh
#          er -> o + r(er) -> or
# ==========================================


# 汉字库 包含所有拼音组合
COMMON_CHARS = (
    "八把波伯百白北被班半本奔帮榜崩蹦比必别憋表标边变宾滨兵病不布爬怕婆破拍派陪配"
    "盘判盆喷旁胖朋碰皮批撇瞥票飘片偏品贫平苹普铺妈马摸莫么买卖每美满慢门们忙盲梦"
    "猛米密灭蔑秒妙谬面棉民敏明名母目发法佛飞非反饭分份方房风封父服大打的得代带得"
    "到道斗豆但单扥当党等邓地第爹跌掉调丢点电定顶读度多朵对队顿盾东动他它特太台套"
    "讨头偷谈探躺趟疼腾体提铁贴条跳天田听停土图脱托退推吞屯同通那拿呢哪乃奶内馁脑"
    "闹耨男难嫩囊囔能你泥聂捏鸟尿牛纽年念您娘酿宁凝努怒诺挪女虐黁弄农拉啦了乐来赖"
    "类累老劳楼漏兰蓝浪朗冷愣里力列烈了聊六流连联林临两量领另路陆落罗绿旅略论伦龙"
    "笼嘎尬个哥改该给高搞够狗感干跟根刚港更耕古故挂瓜国果怪拐贵鬼关管光广工公卡咖"
    "可科开凯尅考靠口扣看刊肯恳抗康坑吭哭库跨夸阔括快块亏愧款宽况狂空孔哈蛤和喝还"
    "海黑嘿好号后厚汉含很恨行航横恒湖虎话化或活坏怀会回换欢黄皇红洪几机家假姐接叫"
    "教九就见间进今将讲经竟句剧觉决卷捐军君七起恰掐且切桥巧求秋前钱亲琴强枪请情去"
    "取却确全权群裙西喜下夏写谢小笑休秀现先新心想香星行需许学雪选宣寻训查扎这着摘"
    "宅这找照周洲战站真针张长正整只之主住抓爪桌捉拽追坠转专装状查差车扯柴拆超朝抽"
    "丑产缠称晨唱常成程吃迟出处欻戳绰揣踹吹垂传船创窗杀沙社设晒筛谁少烧手收山闪什"
    "身上商生声是时书数刷耍说硕帅摔水谁栓涮双爽热惹绕扰肉柔然染人认让嚷仍扔日如入"
    "若弱瑞锐软阮润闰容荣杂砸则责子自在再贼早造走奏咱暂怎谮脏葬增赠组族做作最罪尊"
    "遵总宗擦嚓册侧此次才菜操草凑参残岑涔藏仓层曾粗促错措催脆村存从聪撒洒色塞四思"
    "赛塞扫嫂搜艘三散森桑丧僧素速所锁岁随孙损送松啊阿哦噢额恶爱埃欸奥澳欧偶安按"
    "恩昂盎鞥而儿衣一呀压也爷要药有又眼言因音样洋应英无五哇挖我握外歪为位完万文问"
    "王忘与于月越云运"
)



class MicrosoftPinyinLogic:
    """处理汉字到微软双拼编码的转换逻辑"""

    @staticmethod
    def get_microsoft_code(char):
        """获取单个汉字的微软双拼编码"""
        # 获取声母和韵母
        # pypinyin 返回格式: [['zh'], ['uang']]
        py_initial = pinyin(char, style=Style.INITIALS, strict=False)[0][0]
        py_final = pinyin(char, style=Style.FINALS, strict=False)[0][0]
        
        code1 = ""
        if py_initial:
            code1 = INITIALS_MAP.get(py_initial, py_initial)  # 查表，查不到就是原字母
        else:
            # 微软双拼的零声母规则：使用字母 `o` 作为零声母的占位引导符
            code1 = "o"

        # 2. 处理韵母 code2
        code2 = ""
        if py_final in FINALS_MAP:
            code2 = FINALS_MAP[py_final]
        else:
            # 单韵母如果不在表中（比如 a, o, e），通常映射为自身
            # 微软双拼中，单韵母 a, o, e, i, u, v 都在键盘上有对应
            # 特殊情况处理：比如输入的字通过 pypinyin 解析比较特殊
            if len(py_final) == 1:
                code2 = py_final
            else:
                code2 = py_final[-1]  # fallback，通常不会走到这

        return (code1 + code2).lower()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("微软双拼极速练习")
        self.geometry("800x600")
        self.resizable(False, False)

        # 状态变量
        self.current_char = ""
        self.target_code = ""
        self.total_chars = 0
        self.correct_chars = 0
        self.start_time = None
        self.show_hint = True

        # 界面布局
        self.create_widgets()
        self.bind_events()
        self.load_new_char()

    def create_widgets(self):
        # 1. 顶部数据栏
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(pady=20, padx=20, fill="x")

        


        self.acc_label = ctk.CTkLabel(
            self.top_frame,
            text="正确率: 100%",
            font=("Arial", 20, "bold"),
            text_color="#2CC985",
        )
        self.acc_label.pack(side="right", padx=20)

        # 2. 中间显示区
        self.center_frame = ctk.CTkFrame(self)
        self.center_frame.pack(expand=True, fill="both", padx=50, pady=20)

        self.char_label = ctk.CTkLabel(
            self.center_frame, text="练", font=("SimHei", 120)
        )
        self.char_label.place(relx=0.5, rely=0.4, anchor="center")

        # 提示区
        self.hint_label = ctk.CTkLabel(
            self.center_frame, text="lian", font=("Arial", 24), text_color="gray"
        )
        self.hint_label.place(relx=0.5, rely=0.6, anchor="center")

        # 编码提示 (作弊码)
        self.code_hint_label = ctk.CTkLabel(
            self.center_frame,
            text="[lm]",
            font=("Arial", 20, "bold"),
            text_color="#E04F5F",
        )
        self.code_hint_label.place(relx=0.5, rely=0.7, anchor="center")

        # 3. 底部输入和控制
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(pady=30, fill="x")

        # 输入框
        self.entry = ctk.CTkEntry(
            self.bottom_frame,
            placeholder_text="在此输入...",
            width=200,
            height=50,
            font=("Arial", 24),
            justify="center",
        )
        self.entry.pack(pady=10)
        self.entry.focus()  # 自动聚焦

        # 按钮区
        self.btn_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        self.toggle_hint_btn = ctk.CTkButton(
            self.btn_frame, text="隐藏提示", command=self.toggle_hint
        )
        self.toggle_hint_btn.pack(side="left", padx=10)

        
        

        self.reset_btn = ctk.CTkButton(
            self.btn_frame,
            text="重置数据",
            command=self.reset_stats,
            fg_color="#E04F5F",
            hover_color="#C0392B",
        )
        self.reset_btn.pack(side="left", padx=10)

    def bind_events(self):
        # 监听输入框内容的改变
        self.entry.bind("<KeyRelease>", self.check_input)

    def load_new_char(self):
        """加载一个新的随机汉字"""
        self.current_char = random.choice(COMMON_CHARS)
        self.target_code = MicrosoftPinyinLogic.get_microsoft_code(self.current_char)
        

        # 更新UI
        self.char_label.configure(text=self.current_char)

        # 获取拼音用于显示
        full_pinyin = pinyin(self.current_char, style=Style.NORMAL)[0][0]
        self.hint_label.configure(text=full_pinyin)

        if self.show_hint:
            self.code_hint_label.configure(text=f"[{self.target_code}]")
        else:
            self.code_hint_label.configure(text="[??]")

        # 清空输入框
        self.entry.delete(0, "end")

    def check_input(self, event):
        """检查用户输入"""
        user_input = self.entry.get().lower().strip()

        # 如果是刚开始输入，记录开始时间
        if self.start_time is None and len(user_input) > 0:
            self.start_time = time.time()

        # 双拼每个字固定2码
        if len(user_input) >= 2:
            self.total_chars += 1
            if user_input == self.target_code:
                # 输入正确
                self.correct_chars += 1
                self.flash_feedback("green")
                self.load_new_char()
            else:
                # 输入错误
                self.flash_feedback("red")
                self.entry.delete(0, "end")  # 清空让用户重输

            self.update_stats()

    def flash_feedback(self, color):
        """简单的视觉反馈"""
        original_color = self.entry.cget("border_color")
        flash_color = "#2CC985" if color == "green" else "#E04F5F"

        self.entry.configure(border_color=flash_color, border_width=2)
        self.after(200, lambda: self.entry.configure(border_color=original_color))

    def update_stats(self):
        """更新正确率"""
        if self.total_chars > 0:
            acc = (self.correct_chars / self.total_chars) * 100
            self.acc_label.configure(text=f"正确率: {acc:.1f}%")

        

    def toggle_hint(self):
        self.show_hint = not self.show_hint
        self.toggle_hint_btn.configure(
            text="显示提示" if not self.show_hint else "隐藏提示"
        )
        # 刷新当前显示
        if self.show_hint:
            self.code_hint_label.configure(text=f"[{self.target_code}]")
        else:
            self.code_hint_label.configure(text="[??]")

        self.entry.focus()

    def reset_stats(self):
        self.total_chars = 0
        self.correct_chars = 0
        self.start_time = None
        self.acc_label.configure(text="正确率: 100%")
        self.load_new_char()
        self.entry.focus()

    


if __name__ == "__main__":
    # while 1:
    #    a = input()
    #    b = MicrosoftPinyinLogic.get_microsoft_code(a)
    #    print(f"字 '{a}' 的双拼代码是: {b}")
    app = App()
    app.mainloop()
