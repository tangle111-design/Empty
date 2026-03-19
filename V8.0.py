import sys, subprocess, importlib, random, time, json, os

# 自动安装库
for p in ["customtkinter", "pypinyin", "matplotlib"]:
    try:
        importlib.import_module(p)
    except:
        subprocess.check_call([sys.executable, "-m", "pip", "install", p])

import customtkinter as ctk
from pypinyin import pinyin, Style

"""
TODO
微软双拼方案   DONE
增加错题分析      DONE
增加错题练习      DONE
增加小鹤方案      DONE
将错误分析数据持久化到本地（文件或数据库）DONE
增加练习统计数据（总练习时间、平均每字输入时间等） DONE
修复图片里面的错误显示，以区分小鹤和微软方案的方式来储存本地错误数据 DONE
建立错误消除玩法
"""

# --- 配置部分 ---
ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
DATA_FILE = "practice_data_v2.json"

# 声母映射 (只有非单字符的声母需要转换，其余即为键盘对应字母)
INITIALS_MAP = {"zh": "v", "ch": "i", "sh": "u"}

# 韵母映射
XIAOHE_FINALS_MAP = [
    # 二字成词的先拿出来
    {
        "ai": "d",
        "an": "j",
        "ao": "c",
        "ei": "w",
        "en": "f",
        "er": "r",
        "ou": "z",
    },
    {
        "a": "a",
        "o": "o",
        "e": "e",
        "i": "i",
        "u": "u",
        "v": "v",
        "ang": "h",
        "eng": "g",
        "ia": "x",
        "ian": "m",
        "iang": "l",
        "iao": "n",
        "ie": "p",
        "in": "b",
        "ing": "k",
        "iong": "s",
        "iu": "q",
        "ong": "s",
        "ua": "x",
        "uai": "k",
        "uan": "r",
        "uang": "l",
        "ue": "t",
        "ui": "v",
        "un": "y",
        "uo": "o",
    },
]

MICROSOFT_FINALS_MAP = {
    "a": "a", "o": "o", "e": "e", "i": "i", "u": "u", "v": "y", "ü": "y",
    "ai": "l", "ei": "z", "ui": "v", "ao": "k", "ou": "b", "iu": "q",
    "ie": "x", "ve": "t", "üe": "t", "ue": "t", "er": "r", "an": "j",
    "en": "f", "in": "n", "un": "p", "vn": "p", "ün": "p", "ang": "h",
    "eng": "g", "ing": ";", "ong": "s", "iong": "s", "ia": "w",
    "iao": "c", "ian": "m", "iang": "d", "ua": "w", "uai": "y",
    "uan": "r", "uang": "d", "uo": "o",
}

# 汉字库 包含所有常见拼音组合
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

        # 状态变量
        self.scheme = "microsoft"  # 默认使用微软双拼方案
        self._is_error_practice_mode = False
        self.current_char = ""
        self.target_code = ""
        self.start_time = None
        self.show_hint = True

        # 初始化数据容器，区分两种方案
        self.practice_data = {
            "microsoft": {
                "error_chars": [],
                "error_analysis_data": [{}, {}], # 0:声母, 1:韵母
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

        # 加载本地历史数据
        self.load_data()

        # 界面布局
        self.create_widgets()
        self.bind_events()
        self.load_new_char()
        self.update_stats()

    def get_current_data(self):
        """获取当前方案的数据引用"""
        return self.practice_data[self.scheme]

    def save_data(self):
        """将数据保存到本地JSON文件"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.practice_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存数据失败: {e}")

    def load_data(self):
        """从本地JSON文件加载数据"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                    # 深度更新，确保旧格式数据迁移或新方案字段存在
                    for s in ["microsoft", "xiaohe"]:
                        if s in loaded_data:
                            self.practice_data[s].update(loaded_data[s])
            except Exception as e:
                print(f"加载数据失败，将使用初始值: {e}")

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
        self.char_label.place(relx=0.5, rely=0.35, anchor="center")

        # 提示区
        self.hint_label = ctk.CTkLabel(
            self.center_frame, text="lian", font=("Arial", 24), text_color="gray"
        )
        self.hint_label.place(relx=0.5, rely=0.6, anchor="center")

        # 编码提示
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
            width=200,
            height=50,
            font=("Arial", 24),
            justify="center",
        )
        self.entry.pack(pady=30)

        # 按钮区
        self.btn_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.btn_frame.pack(pady=20, padx=20, fill="x")

        self.toggle_hint_btn = ctk.CTkButton(
            self.btn_frame, text="隐藏提示", command=self.toggle_hint
        )
        self.toggle_hint_btn.pack(side="left", padx=10)

        self.error_analysis_btn = ctk.CTkButton(
            self.btn_frame,
            text="错题分析",
            command=self.show_error_analysis,
            fg_color="#0BAD7F",
            hover_color="#42AF24",
        )
        self.error_analysis_btn.pack(side="left", padx=10)

        # 切换双拼方案
        self.scheme_btn = ctk.CTkButton(
            self.btn_frame,
            text="当前方案: 微软双拼",
            command=self.switch_scheme,
            fg_color="#3498DB",
            hover_color="#2980B9",
        )
        self.scheme_btn.pack(side="left", padx=10)

        # 错题模式
        self.error_practice_btn = ctk.CTkButton(
            self.btn_frame,
            text="错题练习",
            command=self.change_error_practice_mode,
            fg_color="#F39C12",
            hover_color="#D35400",
        )
        self.error_practice_btn.pack(side="left", padx=10)

        # 查看统计数据
        self.stats_btn = ctk.CTkButton(
            self.btn_frame,
            text="查看统计",
            command=self.show_stats,
            fg_color="#0BAD7F",
            hover_color="#42AF24",
        )
        self.stats_btn.pack(side="left", padx=10)

        self.reset_btn = ctk.CTkButton(
            self.top_frame,
            text="重置数据",
            command=self.reset_stats,
            fg_color="#E04F5F",
            hover_color="#C0392B",
        )
        self.reset_btn.place(relx=0.01, rely=0.5, anchor="w")

    def bind_events(self):
        self.entry.bind("<KeyRelease>", self.check_input)

    def load_new_char(self):
        """加载一个新的随机汉字"""
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

        # 更新UI
        self.char_label.configure(text=self.current_char)
        full_pinyin = pinyin(self.current_char, style=Style.NORMAL)[0][0]
        self.hint_label.configure(text=full_pinyin)

        if self.show_hint:
            self.code_hint_label.configure(text=f"[{self.target_code}]")
        else:
            self.code_hint_label.configure(text="[??]")

        self.entry.delete(0, "end")

    def check_input(self, event):
        """检查用户输入"""
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
                # 输入正确
                data["correct_chars"] += 1
                self.flash_feedback("green")
                self.load_new_char()
            else:
                # 输入错误
                self.flash_feedback("red")
                self.entry.delete(0, "end")

                if not self._is_error_practice_mode:
                    if self.current_char not in data["error_chars"]:
                        data["error_chars"].append(self.current_char)
                    
                    # 记录详细错误 (声母/零声母)
                    target_init = self.target_code[0]
                    if user_input[0] != target_init:
                        if target_init not in data["error_analysis_data"][0]:
                            data["error_analysis_data"][0][target_init] = {"error_count": 0, "timestamps": []}
                        data["error_analysis_data"][0][target_init]["error_count"] += 1
                        data["error_analysis_data"][0][target_init]["timestamps"].append(time.time())

                    # 记录详细错误 (韵母)
                    target_final = self.target_code[1]
                    if user_input[1] != target_final:
                        if target_final not in data["error_analysis_data"][1]:
                            data["error_analysis_data"][1][target_final] = {"error_count": 0, "timestamps": []}
                        data["error_analysis_data"][1][target_final]["error_count"] += 1
                        data["error_analysis_data"][1][target_final]["timestamps"].append(time.time())

            self.update_stats()
            self.save_data()

    def show_stats(self):
        """显示练习统计数据的弹窗"""
        data = self.get_current_data()
        if data["total_chars"] == 0:
            self.show_info("当前方案还没有练习数据！")
            return

        acc = (data["correct_chars"] / data["total_chars"]) * 100
        # 简单估算速度 (仅限本次打开软件的会话)
        avg_speed = 0
        if self.start_time:
            duration_min = (time.time() - self.start_time) / 60
            if duration_min > 0:
                avg_speed = data["total_chars"] / duration_min

        stats_message = (
            f"【{self.scheme_btn.cget('text')}】\n"
            f"总练习字数: {data['total_chars']}\n"
            f"正确率: {acc:.1f}%\n"
            f"本次会话速度: {avg_speed:.1f} 字/分"
        )
        self.show_info(stats_message)

    def change_error_practice_mode(self):
        """切换错题练习模式"""
        data = self.get_current_data()
        if not self._is_error_practice_mode:
            if not data["error_chars"]:
                self.show_info(f"当前方案没有错题可练习！")
                return
            self.error_practice_btn.configure(text="退出错题练习", fg_color="#E67E22")
            self._is_error_practice_mode = True
        else:
            self.error_practice_btn.configure(text="错题练习", fg_color="#F39C12")
            self._is_error_practice_mode = False
        
        self.load_new_char()

    def flash_feedback(self, color):
        original_color = self.entry.cget("border_color")
        flash_color = "#2CC985" if color == "green" else "#E04F5F"
        self.entry.configure(border_color=flash_color, border_width=2)
        self.after(200, lambda: self.entry.configure(border_color=original_color))

    def update_stats(self):
        """更新正确率"""
        data = self.get_current_data()
        if data["total_chars"] > 0:
            acc = (data["correct_chars"] / data["total_chars"]) * 100
            self.acc_label.configure(text=f"正确率: {acc:.1f}%")
        else:
            self.acc_label.configure(text="正确率: 100%")

    def toggle_hint(self):
        self.show_hint = not self.show_hint
        self.toggle_hint_btn.configure(text="显示提示" if not self.show_hint else "隐藏提示")
        if self.show_hint:
            self.code_hint_label.configure(text=f"[{self.target_code}]")
        else:
            self.code_hint_label.configure(text="[??]")

    def reset_stats(self):
        scheme_key = self.scheme
        self.practice_data[scheme_key] = {
            "error_chars": [],
            "error_analysis_data": [{}, {}],
            "total_chars": 0,
            "correct_chars": 0
        }
        self._is_error_practice_mode = False
        self.error_practice_btn.configure(text="错题练习", fg_color="#F39C12")
        self.start_time = None
        self.update_stats()
        self.save_data()
        self.load_new_char()

    def switch_scheme(self):
        # 切换方案
        if self.scheme == "microsoft":
            self.scheme = "xiaohe"
            self.scheme_btn.configure(text="当前方案: 小鹤双拼", fg_color="#8E44AD")
        else:
            self.scheme = "microsoft"
            self.scheme_btn.configure(text="当前方案: 微软双拼", fg_color="#3498DB")
        
        # 状态重置
        self._is_error_practice_mode = False
        self.error_practice_btn.configure(text="错题练习", fg_color="#F39C12")
        self.start_time = None
        
        # 刷新UI
        self.update_stats()
        self.load_new_char()

    def show_info(self, message):
        popup = ctk.CTkToplevel(self)
        popup.title("提示")
        popup.geometry("350x200")
        popup.transient(self)
        popup.grab_set()

        label = ctk.CTkLabel(popup, text=message, wraplength=300, font=("Microsoft YaHei", 14))
        label.pack(pady=30)

        btn_ok = ctk.CTkButton(popup, text="确定", command=popup.destroy)
        btn_ok.pack(pady=10)

    def show_error_analysis(self):
        data = self.get_current_data()
        initial_errors = data["error_analysis_data"][0]
        final_errors = data["error_analysis_data"][1]

        if not initial_errors and not final_errors:
            self.show_info("当前方案没有错误数据可分析！")
            return

        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        plt.rcParams["font.sans-serif"] = ["SimHei"]
        plt.rcParams["axes.unicode_minus"] = False

        # 排序并取Top 10
        init_sorted = dict(sorted(initial_errors.items(), key=lambda x: x[1]['error_count'], reverse=True)[:10])
        final_sorted = dict(sorted(final_errors.items(), key=lambda x: x[1]['error_count'], reverse=True)[:10])

        analysis_window = ctk.CTkToplevel(self)
        analysis_window.title(f"错题统计 - {self.scheme}")
        analysis_window.geometry("1000x600")
        analysis_window.transient(self)
        analysis_window.grab_set()

        fig = plt.Figure(figsize=(10, 5), dpi=100)
        
        if init_sorted:
            ax1 = fig.add_subplot(121)
            ax1.bar(init_sorted.keys(), [v['error_count'] for v in init_sorted.values()], color="#E04F5F")
            ax1.set_title("易错声母 (Top 10)")
        
        if final_sorted:
            ax2 = fig.add_subplot(122)
            ax2.bar(final_sorted.keys(), [v['error_count'] for v in final_sorted.values()], color="#0BAD7F")
            ax2.set_title("易错韵母 (Top 10)")

        canvas = FigureCanvasTkAgg(fig, master=analysis_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkButton(analysis_window, text="关闭", command=analysis_window.destroy).pack(pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()