'''
为了实现本地数据存储，我对你的原始代码进行了以下 6 处具体改动：
1. 扩展标准库导入 (Imports)
在代码最顶部的导入部分，新增了 json 和 os。
改动前：import sys, subprocess, importlib, random, time
改动后：import sys, subprocess, importlib, random, time, json, os
2. 新增数据文件常量 (Constants)
在配置部分添加了存储文件路径的定义。
新增代码：DATA_FILE = "practice_data.json"
3. 在 App.__init__ 中新增数据加载
在窗口初始化时，确保先从本地读取历史数据，再渲染界面。
改动内容：在 self.create_widgets() 之前插入了 self.load_data()。这样界面上的“正确率”和“总字数”一打开就是历史累计值。
4. 新增两个数据管理方法 (New Methods)
在 App 类中完整添加了这两个方法，负责磁盘读写：
save_data(self)：将 ERROR_CHARS（错题列表）、ERROR_ANALYSIS_DATA（错误统计字典）、total_chars 和 correct_chars 封装进一个大字典，并写入 practice_data.json。
load_data(self)：检查文件是否存在。如果存在，使用 json.load 读取并更新全局变量和类属性。特别注意： 这里使用了 global 关键字来更新外部定义的 ERROR_CHARS 和 ERROR_ANALYSIS_DATA。
5. 修改 check_input 输入检查逻辑
为了实现“实时保存”，在处理完用户输入后立即写入硬盘。
改动内容：在 check_input 方法的最后一行（self.update_stats() 之后）添加了 self.save_data()。
逻辑优化：在记录声母/韵母错误时，增加了字典键（Key）是否存在判断的逻辑。如果本地读取的字典里没有某个键，程序会自动初始化它，防止 KeyError 崩溃。
6. 修改 reset_stats 重置逻辑
确保“重置”不仅仅是清空当前内存，还要抹除本地文件。
改动内容：
清空 ERROR_CHARS 和 ERROR_ANALYSIS_DATA。
添加了 if os.path.exists(DATA_FILE): os.remove(DATA_FILE)。这意味着点击重置后，下次启动软件也会是全新的状态。'''
import sys, subprocess, importlib, random, time, json, os

# 自动安装库
for p in ["customtkinter", "pypinyin", "matplotlib"]:
    try: importlib.import_module(p)
    except: subprocess.check_call([sys.executable, "-m", "pip", "install", p])

import customtkinter as ctk
from pypinyin import pinyin, Style

# --- 配置与数据路径 ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
DATA_FILE = "practice_data.json"

# 声母/韵母映射表 (保持不变)
INITIALS_MAP = {"zh": "v", "ch": "i", "sh": "u"}
XIAOHE_FINALS_MAP = [{"ai":"d","an":"j","ao":"c","ei":"w","en":"f","er":"r","ou":"z"},{"a":"a","o":"o","e":"e","i":"i","u":"u","v":"v","ang":"h","eng":"g","ia":"x","ian":"m","iang":"l","iao":"n","ie":"p","in":"b","ing":"k","iong":"s","iu":"q","ong":"s","ua":"x","uai":"k","uan":"r","uang":"l","ue":"t","ui":"v","un":"y","uo":"o"}]
MICROSOFT_FINALS_MAP = {"a":"a","o":"o","e":"e","i":"i","u":"u","v":"y","ü":"y","ai":"l","ei":"z","ui":"v","ao":"k","ou":"b","iu":"q","ie":"x","ve":"t","üe":"t","ue":"t","er":"r","an":"j","en":"f","in":"n","un":"p","vn":"p","ün":"p","ang":"h","eng":"g","ing":";","ong":"s","iong":"s","ia":"w","iao":"c","ian":"m","iang":"d","ua":"w","uai":"y","uan":"r","uang":"d","uo":"o"}

# 初始全局变量
ERROR_CHARS = []
ERROR_ANALYSIS_DATA = [{"target_initial": {"error_count": 0}}, {"target_final": {"error_count": 0}}]
COMMON_CHARS = "八把波伯百白北被班半本奔帮榜崩蹦比必别憋表标边变宾滨兵病不布爬怕婆破拍派陪配盘判盆喷旁胖朋碰皮批撇瞥票飘片偏品贫平苹普铺妈马摸莫么买卖每美满慢门们忙盲梦猛米密灭蔑秒妙谬面棉民敏明名母目发法佛飞非反饭分份方房风封父服大打的得代带得到道斗豆但单扥当党等邓地第爹跌掉调丢点电定顶读度多朵对队顿盾东动他它特太台套讨头偷谈探躺趟疼腾体提铁贴条跳天田听停土图脱托退推吞屯同通那拿呢哪乃奶内馁脑闹耨男难嫩囊囔能你泥聂捏鸟尿牛纽年念您娘酿宁凝努怒诺挪女虐黁弄农拉啦了乐来赖类累老劳楼漏兰蓝浪朗冷愣里力列烈了聊六流连联林临两量领另路陆落罗绿旅略论伦龙笼嘎尬个哥改该给高搞够狗感干跟根刚港更耕古故挂瓜国果怪拐贵鬼关管光广工公卡咖可科开凯尅考靠口扣看刊肯恳抗康坑吭哭库跨夸阔括快块亏愧款宽况狂空孔哈蛤和喝还海黑嘿好号后厚汉含很恨行航横恒湖虎话化或活坏怀会回换欢黄皇红洪几机家假姐接叫教九就见间进今将讲经竟句剧觉决卷捐军君七起恰掐且切桥巧求秋前钱亲琴强枪请情去取却确全权群裙西喜下夏写谢小笑休秀现先新心想香星行需许学雪选宣寻训查扎这着摘宅这找照周洲战站真针张长正整只之主住抓爪桌捉拽追坠转专装状查差车扯柴拆超朝抽丑产缠称晨唱常成程吃迟出处欻戳绰揣踹吹垂传船创窗杀沙社设晒筛谁少烧手收山闪什身上商生声是时书数刷耍说硕帅摔水谁栓涮双爽热惹绕扰肉柔然染人认让嚷仍扔日如入若弱瑞锐软阮润闰容荣杂砸则责子自在再贼早造走奏咱暂怎谮脏葬增赠组族做作最罪尊遵总宗擦嚓册侧此次才菜操草凑参残岑涔藏仓层曾粗促错措催脆村存从聪撒洒色塞四思赛塞扫嫂搜艘三散森桑丧僧素速所锁岁随孙损送松啊阿哦噢额恶爱埃欸奥澳欧偶安按恩昂盎鞥而儿衣一呀压也爷要药有又眼言因音样洋应英无五哇挖我握外歪为位完万文问王忘与于月越云运"

# 逻辑类保持不变...
class XiaohePinyinLogic:
    @staticmethod
    def get_xiaohe_code(char):
        py_initial = pinyin(char, style=Style.INITIALS, strict=False)[0][0]
        py_final = pinyin(char, style=Style.FINALS, strict=False)[0][0]
        code1 = INITIALS_MAP.get(py_initial, py_initial) if py_initial else ""
        if code1 == "":
            if py_final in XIAOHE_FINALS_MAP[0]: code2 = py_final
            else: code1, code2 = py_final[0], XIAOHE_FINALS_MAP[1].get(py_final, "")
        else:
            code2 = XIAOHE_FINALS_MAP[1].get(py_final, XIAOHE_FINALS_MAP[0].get(py_final, ""))
        return code1, code2

class MicrosoftPinyinLogic:
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
        self.scheme = "microsoft"
        self._is_error_practice_mode = False
        self.current_char = ""
        self.target_code = ""
        self.total_chars = 0
        self.correct_chars = 0
        self.start_time = None
        self.show_hint = True

        # 加载本地历史数据
        self.load_data()
        
        self.create_widgets()
        self.bind_events()
        self.load_new_char()
        self.update_stats()

    def save_data(self):
        """将数据保存到本地JSON文件"""
        data = {
            "error_chars": ERROR_CHARS,
            "error_analysis_data": ERROR_ANALYSIS_DATA,
            "total_chars": self.total_chars,
            "correct_chars": self.correct_chars
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_data(self):
        """从本地JSON文件加载数据"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    global ERROR_CHARS, ERROR_ANALYSIS_DATA
                    ERROR_CHARS = data.get("error_chars", [])
                    ERROR_ANALYSIS_DATA = data.get("error_analysis_data", ERROR_ANALYSIS_DATA)
                    self.total_chars = data.get("total_chars", 0)
                    self.correct_chars = data.get("correct_chars", 0)
            except Exception as e:
                print(f"加载数据失败: {e}")

    def create_widgets(self):
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(pady=20, padx=20, fill="x")
        self.acc_label = ctk.CTkLabel(self.top_frame, text="正确率: 100%", font=("Arial", 20, "bold"), text_color="#2CC985")
        self.acc_label.pack(side="right", padx=20)

        self.center_frame = ctk.CTkFrame(self)
        self.center_frame.pack(expand=True, fill="both", padx=50, pady=20)
        self.char_label = ctk.CTkLabel(self.center_frame, text="练", font=("SimHei", 120))
        self.char_label.place(relx=0.5, rely=0.35, anchor="center")
        self.hint_label = ctk.CTkLabel(self.center_frame, text="lian", font=("Arial", 24), text_color="gray")
        self.hint_label.place(relx=0.5, rely=0.6, anchor="center")
        self.code_hint_label = ctk.CTkLabel(self.center_frame, text="[lm]", font=("Arial", 20, "bold"), text_color="#E04F5F")
        self.code_hint_label.place(relx=0.5, rely=0.7, anchor="center")

        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(pady=30, fill="x")
        self.entry = ctk.CTkEntry(self.bottom_frame, width=200, height=50, font=("Arial", 24), justify="center")
        self.entry.pack(pady=30)

        self.btn_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.btn_frame.pack(pady=20, padx=20, fill="x")
        ctk.CTkButton(self.btn_frame, text="隐藏提示", command=self.toggle_hint).pack(side="left", padx=5)
        ctk.CTkButton(self.btn_frame, text="错题分析", command=self.show_error_analysis, fg_color="#0BAD7F").pack(side="left", padx=5)
        self.scheme_btn = ctk.CTkButton(self.btn_frame, text="当前方案: 微软双拼", command=self.switch_scheme, fg_color="#3498DB")
        self.scheme_btn.pack(side="left", padx=5)
        self.error_practice_btn = ctk.CTkButton(self.btn_frame, text="错题练习", command=self.change_error_practice_mode, fg_color="#F39C12")
        self.error_practice_btn.pack(side="left", padx=5)
        ctk.CTkButton(self.btn_frame, text="查看统计", command=self.show_stats, fg_color="#0BAD7F").pack(side="left", padx=5)
        ctk.CTkButton(self.top_frame, text="重置数据", command=self.reset_stats, fg_color="#E04F5F").place(relx=0.01, rely=0.5, anchor="w")

    def bind_events(self):
        self.entry.bind("<KeyRelease>", self.check_input)

    def load_new_char(self):
        if self._is_error_practice_mode and ERROR_CHARS:
            self.current_char = random.choice(ERROR_CHARS)
        else:
            self.current_char = random.choice(COMMON_CHARS)

        logic = MicrosoftPinyinLogic if self.scheme == "microsoft" else XiaohePinyinLogic
        c1, c2 = logic.get_microsoft_code(self.current_char) if self.scheme == "microsoft" else logic.get_xiaohe_code(self.current_char)
        self.target_code = (c1 + c2).lower()
        
        self.char_label.configure(text=self.current_char)
        full_py = pinyin(self.current_char, style=Style.NORMAL)[0][0]
        self.hint_label.configure(text=full_py)
        self.code_hint_label.configure(text=f"[{self.target_code}]" if self.show_hint else "[??]")
        self.entry.delete(0, "end")

    def check_input(self, event):
        user_input = self.entry.get().lower().strip()
        if not self.start_time and user_input: self.start_time = time.time()
        
        if len(user_input) > 2:
            self.flash_feedback("red")
            self.entry.delete(0, "end")
            return

        if len(user_input) == 2:
            self.total_chars += 1
            if user_input == self.target_code:
                self.correct_chars += 1
                self.flash_feedback("green")
                self.load_new_char()
            else:
                self.flash_feedback("red")
                self.entry.delete(0, "end")
                if not self._is_error_practice_mode:
                    if self.current_char not in ERROR_CHARS: ERROR_CHARS.append(self.current_char)
                    # 记录详细错误
                    for i, key in enumerate(["initial", "final"]):
                        if user_input[i] != self.target_code[i]:
                            target = self.target_code[i]
                            if target not in ERROR_ANALYSIS_DATA[i]:
                                ERROR_ANALYSIS_DATA[i][target] = {"error_count": 0, "timestamps": []}
                            ERROR_ANALYSIS_DATA[i][target]["error_count"] += 1
                            ERROR_ANALYSIS_DATA[i][target]["timestamps"].append(time.time())
            self.update_stats()
            self.save_data() # 每次输入后保存

    def update_stats(self):
        if self.total_chars > 0:
            acc = (self.correct_chars / self.total_chars) * 100
            self.acc_label.configure(text=f"正确率: {acc:.1f}%")

    def reset_stats(self):
        self.total_chars = 0
        self.correct_chars = 0
        ERROR_CHARS.clear()
        ERROR_ANALYSIS_DATA[0].clear()
        ERROR_ANALYSIS_DATA[1].clear()
        ERROR_ANALYSIS_DATA[0]["target_initial"] = {"error_count": 0}
        ERROR_ANALYSIS_DATA[1]["target_final"] = {"error_count": 0}
        self.acc_label.configure(text="正确率: 100%")
        if os.path.exists(DATA_FILE): os.remove(DATA_FILE) # 删除本地文件
        self.load_new_char()

    def show_stats(self):
        if self.total_chars == 0: return
        acc = (self.correct_chars / self.total_chars) * 100
        stats = f"总字数: {self.total_chars}\n正确率: {acc:.1f}%"
        self.show_info(stats)

    def switch_scheme(self):
        self.scheme = "xiaohe" if self.scheme == "microsoft" else "microsoft"
        self.scheme_btn.configure(text=f"当前方案: {'小鹤双拼' if self.scheme=='xiaohe' else '微软双拼'}")
        self.load_new_char()

    def toggle_hint(self):
        self.show_hint = not self.show_hint
        self.code_hint_label.configure(text=f"[{self.target_code}]" if self.show_hint else "[??]")

    def flash_feedback(self, color):
        orig = self.entry.cget("border_color")
        new_c = "#2CC985" if color == "green" else "#E04F5F"
        self.entry.configure(border_color=new_c, border_width=2)
        self.after(200, lambda: self.entry.configure(border_color=orig))

    def show_info(self, message):
        pop = ctk.CTkToplevel(self)
        pop.geometry("300x150")
        pop.attributes("-topmost", True)
        ctk.CTkLabel(pop, text=message).pack(pady=20)
        ctk.CTkButton(pop, text="确定", command=pop.destroy).pack()

    def change_error_practice_mode(self):
        if not self._is_error_practice_mode and not ERROR_CHARS:
            self.show_info("没有错题！")
            return
        self._is_error_practice_mode = not self._is_error_practice_mode
        self.error_practice_btn.configure(text="退出错题练习" if self._is_error_practice_mode else "错题练习")
        self.load_new_char()

    def show_error_analysis(self):
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        # 准备排序数据
        initials = {k: v["error_count"] for k, v in ERROR_ANALYSIS_DATA[0].items() if k != "target_initial"}
        finals = {k: v["error_count"] for k, v in ERROR_ANALYSIS_DATA[1].items() if k != "target_final"}
        
        if not initials and not finals:
            self.show_info("数据不足！")
            return

        initials = dict(sorted(initials.items(), key=lambda x: x[1], reverse=True)[:10])
        finals = dict(sorted(finals.items(), key=lambda x: x[1], reverse=True)[:10])

        win = ctk.CTkToplevel(self)
        win.title("分析")
        win.geometry("1000x600")
        win.attributes("-topmost", True)
        
        plt.rcParams["font.sans-serif"] = ["SimHei"]
        fig = plt.Figure(figsize=(8, 5))
        ax1, ax2 = fig.add_subplot(121), fig.add_subplot(122)
        
        if initials:
            ax1.bar(initials.keys(), initials.values(), color="#E04F5F")
            ax1.set_title("声母Top10")
        if finals:
            ax2.bar(finals.keys(), finals.values(), color="#0BAD7F")
            ax2.set_title("韵母Top10")

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()