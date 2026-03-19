import sys, subprocess, importlib, random, time, json, os

# 自动安装库
for p in ["customtkinter", "pypinyin", "matplotlib"]:
    try:
        importlib.import_module(p)
    except:
        subprocess.check_call([sys.executable, "-m", "pip", "install", p])

import customtkinter as ctk
from pypinyin import pinyin, Style

# --- 配置部分 ---
ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
DATA_FILE = "practice_data_v2.json"

# 声母映射
INITIALS_MAP = {"zh": "v", "ch": "i", "sh": "u"}

# 韵母映射
XIAOHE_FINALS_MAP = [
    {"ai": "d", "an": "j", "ao": "c", "ei": "w", "en": "f", "er": "r", "ou": "z"},
    {
        "a": "a", "o": "o", "e": "e", "i": "i", "u": "u", "v": "v", "ang": "h", "eng": "g",
        "ia": "x", "ian": "m", "iang": "l", "iao": "n", "ie": "p", "in": "b", "ing": "k",
        "iong": "s", "iu": "q", "ong": "s", "ua": "x", "uai": "k", "uan": "r", "uang": "l",
        "ue": "t", "ui": "v", "un": "y", "uo": "o",
    },
]

MICROSOFT_FINALS_MAP = {
    "a": "a", "o": "o", "e": "e", "i": "i", "u": "u", "v": "y", 
    "ai": "l", "ei": "z", "ui": "v", "ao": "k", "ou": "b", "iu": "q", "ie": "x",
    "ue": "t", "er": "r", "an": "j", "en": "f", "in": "n",
    "un": "p",   "ang": "h", "eng": "g", "ing": ";", "ong": "s",
    "iong": "s", "ia": "w", "iao": "c", "ian": "m", "iang": "d", "ua": "w", "uai": "y",
    "uan": "r", "uang": "d", "uo": "o",
}

# --- 新增：反映射字典 (用于统计图表显示) ---
# 声母反映射
REVERSE_INITIALS_MAP = {v: k for k, v in INITIALS_MAP.items()}

# 小鹤韵母反映射
REVERSE_XIAOHE_FINALS_MAP = {}
for group in XIAOHE_FINALS_MAP:
    for py, key in group.items():
        if key not in REVERSE_XIAOHE_FINALS_MAP:
            REVERSE_XIAOHE_FINALS_MAP[key] = py
        else:
            # 如果按键对应多个拼音（如s对应ong/iong），合并显示
            if py not in REVERSE_XIAOHE_FINALS_MAP[key]:
                REVERSE_XIAOHE_FINALS_MAP[key] += f"/{py}"

# 微软韵母反映射
REVERSE_MICROSOFT_FINALS_MAP = {}
for py, key in MICROSOFT_FINALS_MAP.items():
    if key not in REVERSE_MICROSOFT_FINALS_MAP:
        REVERSE_MICROSOFT_FINALS_MAP[key] = py
    else:
        if py not in REVERSE_MICROSOFT_FINALS_MAP[key]:
            REVERSE_MICROSOFT_FINALS_MAP[key] += f"/{py}"

# 汉字库
COMMON_CHARS = (
    "八把波伯百白北被班半本奔帮榜崩蹦比必别憋表标边变宾滨兵病不布爬怕婆破拍派陪配"
    "盘判盆喷旁胖朋碰皮批撇瞥票飘片偏品贫平苹普铺妈马摸莫么买卖每美满慢门们忙盲梦"
    "猛米密灭蔑秒妙谬面棉民敏明名母目发法佛飞非反饭分份方房风封父服大打的得代带得"
    "到道斗豆但单扥当党等邓地第爹跌掉调丢点电定顶读度多朵对队顿盾东动他它特太台套"
    "讨头偷谈探躺趟疼腾体提铁贴条跳天田听停土图脱托退推吞屯同通那拿呢哪乃奶内馁脑"
    "闹男难嫩囊囔能你泥聂捏鸟尿牛纽年念您娘酿宁凝努怒诺挪女虐疟弄农拉啦了乐来赖"
    "类累老劳楼漏兰蓝浪朗冷愣里力列烈了聊六流连联林临两量领另路陆落罗绿旅略论伦龙"
    "笼嘎尬个哥改该给高搞够狗感干跟根刚港更耕古故挂瓜国果怪拐贵鬼关管光广工公卡咖"
    "可科开凯尅考靠口扣看刊肯恳抗康坑吭哭库跨夸阔括快块亏愧款宽况狂空孔哈蛤和喝还"
    "海黑嘿好号后厚汉含很恨行航横恒湖虎话化或活坏怀会回换欢黄皇红洪几机家假姐接叫"
    "教九就见间进今将讲经竟句剧觉决卷捐军君七起恰掐且切桥巧求秋前钱亲琴强枪请情去"
    "取却确全权群裙西喜下夏写谢小笑休秀现先新心想香星行需许学雪选宣寻训查扎这着摘"
    "宅这找照周洲战站真针张长正整只之主住抓爪桌捉拽追坠转专装状查差车扯柴拆超朝抽"
    "丑产缠称晨唱常成程吃迟出处欻戳绰揣踹吹垂传船创窗杀沙社设晒筛谁少烧手收山闪什"
    "身上商生声是时书数刷耍说硕帅摔水谁栓涮双爽热惹绕扰肉柔然染人认让嚷仍扔日如入"
    "若弱瑞锐软阮润闰容荣杂砸则责子自在再贼早造走奏咱暂怎脏葬增赠组族做作最罪尊"
    "遵总宗擦嚓册侧此次才菜操草凑参残岑藏仓层曾粗促错措催脆村存从聪撒洒色塞四思"
    "赛塞扫嫂搜艘三散森桑丧僧素速所锁岁随孙损送松啊阿哦噢额恶爱埃欸奥澳欧偶安按"
    "恩昂盎而儿衣一呀压也爷要药有又眼言因音样洋应英无五哇挖我握外歪为位完万文问"
    "王忘与于月越云运"
)


class XiaohePinyinLogic:
    """处理汉字到小鹤双拼编码的转换逻辑"""
    @staticmethod
    def get_xiaohe_code(char):
        py_initial = pinyin(char, style=Style.INITIALS, strict=False)[0][0]
        py_final = pinyin(char, style=Style.FINALS, strict=False)[0][0]
        code1 = INITIALS_MAP.get(py_initial, py_initial) if py_initial else ""
        if code1 == "":
            if py_final in XIAOHE_FINALS_MAP[0]:
                code2 = py_final
            else:
                code1, code2 = py_final[0], XIAOHE_FINALS_MAP[1].get(py_final, "")
        else:
            code2 = XIAOHE_FINALS_MAP[1].get(
                py_final, XIAOHE_FINALS_MAP[0].get(py_final, "")
            )
        return code1, code2


class MicrosoftPinyinLogic:
    """处理汉字到微软双拼编码的转换逻辑"""
    @staticmethod
    def get_microsoft_code(char):
        py_initial = pinyin(char, style=Style.INITIALS, strict=False)[0][0]
        py_final = pinyin(char, style=Style.FINALS, strict=False)[0][0]
        code1 = INITIALS_MAP.get(py_initial, py_initial) if py_initial else "o"
        code2 = MICROSOFT_FINALS_MAP.get(py_final, "")
        return code1, code2


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("双拼极速练习")
        self.geometry("800x600")
        self.resizable(False, False)

        self.scheme = "microsoft"  # 默认使用微软双拼方案
        self._is_error_practice_mode = False
        self.current_char = ""
        self.target_code = ""
        self.start_time = None
        self.show_hint = True

        self.practice_data = {
            "microsoft": {
                "error_chars": [],
                "error_analysis_data": [{}, {}],
                "total_chars": 0,
                "correct_chars": 0
            },
            "xiaohe": {
                "error_chars": [],
                "error_analysis_data": [{}, {}],
                "total_chars": 0,
                "correct_chars": 0
            }
        }

        self.load_data()
        self.create_widgets()
        self.bind_events()
        self.load_new_char()
        self.update_stats()

    def get_current_data(self):
        return self.practice_data[self.scheme]

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.practice_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存数据失败: {e}")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                    for s in ["microsoft", "xiaohe"]:
                        if s in loaded_data:
                            self.practice_data[s].update(loaded_data[s])
            except Exception as e:
                print(f"加载数据失败: {e}")

    def create_widgets(self):
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(pady=20, padx=20, fill="x")

        self.acc_label = ctk.CTkLabel(
            self.top_frame, text="正确率: 100%", font=("Arial", 20, "bold"), text_color="#2CC985"
        )
        self.acc_label.pack(side="right", padx=20)

        self.center_frame = ctk.CTkFrame(self)
        self.center_frame.pack(expand=True, fill="both", padx=50, pady=20)

        self.char_label = ctk.CTkLabel(self.center_frame, text="练", font=("SimHei", 120))
        self.char_label.place(relx=0.5, rely=0.35, anchor="center")

        self.hint_label = ctk.CTkLabel(self.center_frame, text="lian", font=("Arial", 24), text_color="gray")
        self.hint_label.place(relx=0.5, rely=0.6, anchor="center")

        self.code_hint_label = ctk.CTkLabel(
            self.center_frame, text="[lm]", font=("Arial", 20, "bold"), text_color="#E04F5F"
        )
        self.code_hint_label.place(relx=0.5, rely=0.7, anchor="center")

        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(pady=30, fill="x")

        self.entry = ctk.CTkEntry(
            self.bottom_frame, width=200, height=50, font=("Arial", 24), justify="center"
        )
        self.entry.pack(pady=30)

        self.btn_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.btn_frame.pack(pady=20, padx=20, fill="x")

        self.toggle_hint_btn = ctk.CTkButton(self.btn_frame, text="隐藏提示", command=self.toggle_hint)
        self.toggle_hint_btn.pack(side="left", padx=10)

        self.error_analysis_btn = ctk.CTkButton(
            self.btn_frame, text="错题分析", command=self.show_error_analysis, fg_color="#0BAD7F"
        )
        self.error_analysis_btn.pack(side="left", padx=10)

        self.scheme_btn = ctk.CTkButton(
            self.btn_frame, text="当前方案: 微软双拼", command=self.switch_scheme, fg_color="#3498DB"
        )
        self.scheme_btn.pack(side="left", padx=10)

        self.error_practice_btn = ctk.CTkButton(
            self.btn_frame, text="错题练习", command=self.change_error_practice_mode, fg_color="#F39C12"
        )
        self.error_practice_btn.pack(side="left", padx=10)

        self.stats_btn = ctk.CTkButton(
            self.btn_frame, text="查看统计", command=self.show_stats, fg_color="#0BAD7F"
        )
        self.stats_btn.pack(side="left", padx=10)

        self.reset_btn = ctk.CTkButton(
            self.top_frame, text="重置数据", command=self.reset_stats, fg_color="#E04F5F"
        )
        self.reset_btn.place(relx=0.01, rely=0.5, anchor="w")

    def bind_events(self):
        self.entry.bind("<KeyRelease>", self.check_input)

    def load_new_char(self):
        data = self.get_current_data()
        if self._is_error_practice_mode and data["error_chars"]:
            self.current_char = random.choice(data["error_chars"])
        else:
            self.current_char = random.choice(COMMON_CHARS)

        if self.scheme == "microsoft":
            code1, code2 = MicrosoftPinyinLogic.get_microsoft_code(self.current_char)
            self.target_code = (code1 + code2).lower()
        else:
            code1, code2 = XiaohePinyinLogic.get_xiaohe_code(self.current_char)
            self.target_code = (code1 + code2).lower()

        self.char_label.configure(text=self.current_char)
        full_pinyin = pinyin(self.current_char, style=Style.NORMAL)[0][0]
        self.hint_label.configure(text=full_pinyin)

        if self.show_hint:
            self.code_hint_label.configure(text=f"[{self.target_code}]")
        else:
            self.code_hint_label.configure(text="[??]")
        self.entry.delete(0, "end")

    def check_input(self, event):
        user_input = self.entry.get().lower().strip()
        data = self.get_current_data()

        if self.start_time is None and len(user_input) > 0:
            self.start_time = time.time()
        
        if len(user_input) > 2:
            self.flash_feedback("red")
            self.entry.delete(0, "end")
            return

        if len(user_input) == 2:
            data["total_chars"] += 1
            if user_input == self.target_code:
                data["correct_chars"] += 1
                self.flash_feedback("green")
                self.load_new_char()
            else:
                self.flash_feedback("red")
                self.entry.delete(0, "end")
                if not self._is_error_practice_mode:
                    if self.current_char not in data["error_chars"]:
                        data["error_chars"].append(self.current_char)
                    
                    for i in range(2):
                        if user_input[i] != self.target_code[i]:
                            target_key = self.target_code[i]
                            if target_key not in data["error_analysis_data"][i]:
                                data["error_analysis_data"][i][target_key] = {"error_count": 0, "timestamps": []}
                            data["error_analysis_data"][i][target_key]["error_count"] += 1
                            data["error_analysis_data"][i][target_key]["timestamps"].append(time.time())

            self.update_stats()
            self.save_data()

    def show_stats(self):
        data = self.get_current_data()
        if data["total_chars"] == 0:
            self.show_info("没有练习数据！")
            return
        acc = (data["correct_chars"] / data["total_chars"]) * 100
        stats_message = f"方案: {self.scheme}\n总练习: {data['total_chars']}\n正确率: {acc:.1f}%"
        self.show_info(stats_message)

    def change_error_practice_mode(self):
        data = self.get_current_data()
        if not self._is_error_practice_mode:
            if not data["error_chars"]:
                self.show_info("没有错题！")
                return
            self._is_error_practice_mode = True
            self.error_practice_btn.configure(text="退出错题练习")
        else:
            self._is_error_practice_mode = False
            self.error_practice_btn.configure(text="错题练习")
        self.load_new_char()

    def flash_feedback(self, color):
        original_color = self.entry.cget("border_color")
        flash_color = "#2CC985" if color == "green" else "#E04F5F"
        self.entry.configure(border_color=flash_color, border_width=2)
        self.after(200, lambda: self.entry.configure(border_color=original_color))

    def update_stats(self):
        data = self.get_current_data()
        if data["total_chars"] > 0:
            acc = (data["correct_chars"] / data["total_chars"]) * 100
            self.acc_label.configure(text=f"正确率: {acc:.1f}%")

    def toggle_hint(self):
        self.show_hint = not self.show_hint
        self.toggle_hint_btn.configure(text="显示提示" if not self.show_hint else "隐藏提示")
        self.load_new_char()

    def reset_stats(self):
        self.practice_data[self.scheme] = {"error_chars": [], "error_analysis_data": [{}, {}], "total_chars": 0, "correct_chars": 0}
        self.update_stats()
        self.save_data()
        self.load_new_char()

    def switch_scheme(self):
        self.scheme = "xiaohe" if self.scheme == "microsoft" else "microsoft"
        self.scheme_btn.configure(text=f"当前方案: {'小鹤' if self.scheme == 'xiaohe' else '微软'}双拼")
        self._is_error_practice_mode = False
        self.error_practice_btn.configure(text="错题练习")
        self.update_stats()
        self.load_new_char()

    def show_info(self, message):
        popup = ctk.CTkToplevel(self)
        popup.title("提示")
        popup.geometry("300x150")
        popup.transient(self)
        popup.grab_set()
        ctk.CTkLabel(popup, text=message).pack(pady=20)
        ctk.CTkButton(popup, text="确定", command=popup.destroy).pack(pady=10)

    # --- 重点改进部分：反映射显示 ---
    def show_error_analysis(self):
        data = self.get_current_data()
        init_errs_raw = data["error_analysis_data"][0]
        final_errs_raw = data["error_analysis_data"][1]

        if not init_errs_raw and not final_errs_raw:
            self.show_info("当前方案没有错误数据！")
            return

        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        # 解决中文乱码
        plt.rcParams["font.sans-serif"] = ["SimHei"]
        plt.rcParams["axes.unicode_minus"] = False
        
        # --- 全局字号设置 ---
        TITLE_SIZE = 24       # 标题字号
        LABEL_SIZE = 18       # 坐标轴名称字号
        TICK_SIZE = 16        # 刻度（拼音字母）字号

        # 1. 转换声母显示标签
        init_labels = []
        init_counts = []
        sorted_inits = sorted(init_errs_raw.items(), key=lambda x: x[1]['error_count'], reverse=True)[:10]
        for key, val in sorted_inits:
            label = REVERSE_INITIALS_MAP.get(key, key)
            init_labels.append(label)
            init_counts.append(val['error_count'])

        # 2. 转换韵母显示标签
        final_labels = []
        final_counts = []
        sorted_finals = sorted(final_errs_raw.items(), key=lambda x: x[1]['error_count'], reverse=True)[:10]
        rev_final_map = REVERSE_XIAOHE_FINALS_MAP if self.scheme == "xiaohe" else REVERSE_MICROSOFT_FINALS_MAP
        for key, val in sorted_finals:
            label = rev_final_map.get(key, key)
            final_labels.append(label)
            final_counts.append(val['error_count'])

        # 创建显示窗口
        analysis_window = ctk.CTkToplevel(self)
        analysis_window.title(f"错误分析统计 - {self.scheme}")
        analysis_window.geometry("1200x700") # 稍微调大窗口尺寸以适应大字号
        analysis_window.transient(self)
        analysis_window.grab_set()

        fig = plt.Figure(figsize=(12, 6), dpi=100)
        
        # 绘制声母图
        if init_counts:
            ax1 = fig.add_subplot(121)
            ax1.bar(init_labels, init_counts, color="#E04F5F")
            ax1.set_title("易错声母 (Top 10)", fontsize=TITLE_SIZE, pad=20)
            ax1.set_ylabel("错误次数", fontsize=LABEL_SIZE)
            # 设置刻度字号
            ax1.tick_params(axis='x', labelsize=TICK_SIZE)
            ax1.tick_params(axis='y', labelsize=TICK_SIZE)

        # 绘制韵母图
        if final_counts:
            ax2 = fig.add_subplot(122)
            ax2.bar(final_labels, final_counts, color="#0BAD7F")
            ax2.set_title("易错韵母 (Top 10)", fontsize=TITLE_SIZE, pad=20)
            ax2.set_ylabel("错误次数", fontsize=LABEL_SIZE)
            # 设置刻度字号
            ax2.tick_params(axis='x', labelsize=TICK_SIZE)
            ax2.tick_params(axis='y', labelsize=TICK_SIZE)

        # 自动调整布局，防止标签重叠或溢出
        fig.tight_layout(pad=4.0)

        # 嵌入到 customtkinter
        canvas = FigureCanvasTkAgg(fig, master=analysis_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)

        # 关闭按钮也稍微做大一点
        ctk.CTkButton(
            analysis_window, 
            text="关闭分析", 
            width=120, 
            height=40, 
            font=("Microsoft YaHei", 16),
            command=analysis_window.destroy
        ).pack(pady=20)


if __name__ == "__main__":
    app = App()
    app.mainloop()