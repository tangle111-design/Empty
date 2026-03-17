import customtkinter as ctk
import random
import time
from pypinyin import pinyin, Style, load_phrases_dict

# --- 配置部分 ---
ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

# --- 小鹤双拼映射表 ---
# 声母映射 (只有非单字符的声母需要转换，其余即为键盘对应字母)
INITIALS_MAP = {"zh": "v", "ch": "i", "sh": "u"}

# 韵母映射
FINALS_MAP = {
    "iu": "q",
    "ei": "w",
    "e": "e",
    "uan": "r",
    "ue": "t",
    "ve": "t",
    "un": "y",
    "u": "u",
    "i": "i",
    "o": "o",
    "uo": "o",
    "ie": "p",
    "a": "a",
    "ong": "s",
    "iong": "s",
    "ai": "d",
    "ing": "k",
    "uai": "k",
    "ang": "h",
    "an": "j",
    "uai": "k",
    "ing": "k",
    "uang": "l",
    "iang": "l",
    "ou": "z",
    "ia": "x",
    "ua": "x",
    "ao": "c",
    "ui": "v",
    "v": "v",
    "in": "b",
    "iao": "n",
    "m": "m",  # m is rarely separate but useful
    "ian": "m",
    "en": "f",
    "eng": "g",
}

# 常用汉字库 (Top 500+)
COMMON_CHARS = (
    "的一是了我不人在他有这个上们来到时大地为子中你说生国年着就那和要她出也得里后自以会"
    "家可下而过天去能对小多然于心学么之都好看起发当没成只如事把还用第样道想作种开美总从"
    "无情己面最女但现前些所同日手又行意动方期它头经长儿回位分爱老因很给名法间斯知世什两"
    "次使身者被高已亲其进此话常与活正感见明问力理尔点文几定本公特做外孩相西果走将月十实"
    "向声车全信重三机工物气每并别真打太新比才便夫再书部水像眼等体却加电主界门利海受听表"
    "德少克代员许稜先口由死安写性马光白或住难望教命花结乐色更拉东神记处让母父应直字场平"
    "报友关放至张认接告入笑内英军候民岁往何度山息线产保务设式近强够曲质决指系形统干流眼"
    "连任量治师观象省元干感流连任量治师观象省元"
)


class XiaoheLogic:
    """处理汉字到小鹤双拼编码的转换逻辑"""

    @staticmethod
    def get_xiaohe_code(char):
        """获取单个汉字的小鹤双拼编码"""
        # 获取声母和韵母
        # pypinyin 返回格式: [['zh'], ['uang']]
        py_initial = pinyin(char, style=Style.INITIALS, strict=False)[0][0]
        py_final = pinyin(char, style=Style.FINALS, strict=False)[0][0]

        # 1. 处理声母 code1
        code1 = ""
        if py_initial:
            code1 = INITIALS_MAP.get(py_initial, py_initial)  # 查表，查不到就是原字母
        else:
            # 零声母规则：取韵母的首字母作为声母键
            # 例如: an -> a + j;  ou -> o + z;  a -> a + a
            if py_final:
                code1 = py_final[0]
            else:
                return "??"  # 异常处理

        # 2. 处理韵母 code2
        code2 = ""
        if py_final in FINALS_MAP:
            code2 = FINALS_MAP[py_final]
        else:
            # 单韵母如果不在表中（比如 a, o, e），通常映射为自身
            # 小鹤双拼中，单韵母 a, o, e, i, u, v 都在键盘上有对应
            # 特殊情况处理：比如输入的字通过 pypinyin 解析比较特殊
            if len(py_final) == 1:
                code2 = py_final
            else:
                code2 = py_final[-1]  # fallback，通常不会走到这

        return (code1 + code2).lower()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("小鹤双拼极速练习")
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

        self.wpm_label = ctk.CTkLabel(
            self.top_frame,
            text="WPM: 0",
            font=("Arial", 20, "bold"),
            text_color="#3B8ED0",
        )
        self.wpm_label.pack(side="left", padx=20)

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

        self.map_btn = ctk.CTkButton(
            self.btn_frame,
            text="查看键位图",
            command=self.show_key_map,
            fg_color="gray",
        )
        self.map_btn.pack(side="left", padx=10)

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
        self.target_code = XiaoheLogic.get_xiaohe_code(self.current_char)

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

        # 小鹤双拼每个字固定2码
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
        """更新 WPM 和 正确率"""
        if self.total_chars > 0:
            acc = (self.correct_chars / self.total_chars) * 100
            self.acc_label.configure(text=f"正确率: {acc:.1f}%")

        if self.start_time:
            elapsed_min = (time.time() - self.start_time) / 60
            if elapsed_min > 0:
                wpm = int(self.correct_chars / elapsed_min)
                self.wpm_label.configure(text=f"WPM: {wpm}")

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
        self.wpm_label.configure(text="WPM: 0")
        self.acc_label.configure(text="正确率: 100%")
        self.load_new_char()
        self.entry.focus()

    def show_key_map(self):
        """弹窗显示口诀/键位"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("小鹤双拼键位参考")
        dialog.geometry("500x400")

        # 简单文本口诀，如果想更美观可以用图片 Label
        text_map = (
            "【小鹤双拼口诀】\n\n"
            "Q - Qiu (秋)   |  W - Wei (卫)   |  R - Ruan (软)\n"
            "T - Tue (特)   |  Y - Yun (韵)   |  O - uO (窝)\n"
            "P - Pie (撇)   |  S - Song (松)  |  D - Dai (代)\n"
            "F - Fen (分)   |  G - Geng (更)  |  H - Hang (航)\n"
            "J - an (安)    |  K - Kuai (快)  |  L - Liang (两)\n"
            "Z - Zou (走)   |  X - Xia (夏)   |  C - Cao (草)\n"
            "V - Vui (追)   |  B - Bin (滨)   |  N - Niao (鸟)\n"
            "M - Mian (棉)\n\n"
            "【零声母规则】\n"
            "以元音开头的字，首字母为第一码，韵母所在键为第二码。\n"
            "例：安(an) -> aj | 欧(ou) -> oz | 啊(a) -> aa"
        )

        label = ctk.CTkLabel(
            dialog, text=text_map, font=("SimHei", 16), justify="left", padx=20, pady=20
        )
        label.pack(expand=True, fill="both")


if __name__ == "__main__":
    app = App()
    app.mainloop()
