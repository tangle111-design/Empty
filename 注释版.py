# 这个文件是一个用Python编写的GUI应用程序，用于练习小鹤双拼输入法。
# 它使用CustomTkinter库创建界面，随机显示汉字，用户输入对应的双拼编码。
# 程序会统计正确率和每分钟字数（WPM），并提供提示和键位参考。
# 新手注意：代码分为导入、配置、映射表、逻辑类、GUI类和主程序部分。
# 导入语句引入了必要的库：ctk用于界面，random用于随机选择，time用于计时，pypinyin用于获取拼音。

import customtkinter as ctk  # CustomTkinter是Tkinter的现代化扩展，用于创建漂亮的GUI
import random  # random库用于从汉字库中随机选择字
import time  # time库用于记录时间，计算WPM
from pypinyin import pinyin, Style  # pypinyin库用于将汉字转换为拼音

# --- 配置部分 ---
# 这里设置CustomTkinter的全局外观和主题。
ctk.set_appearance_mode("system")  # 设置外观模式为系统默认（跟随操作系统）
ctk.set_default_color_theme("green")  # 设置默认颜色主题为绿色

# --- 小鹤双拼映射表 ---
# 小鹤双拼是一种输入法，将拼音映射到键盘字母。这里定义了声母和韵母的映射字典。
# 声母映射：只有多字母声母需要特殊映射，其他直接用原字母。
INITIALS_MAP = {"zh": "v", "ch": "i", "sh": "u"}  # 例如，zh映射到v

# 韵母映射：将韵母字符串映射到键盘上的字母。
FINALS_MAP = {
    "iu": "q",  # iu韵母对应q键
    "ei": "w",  # ei对应w
    "e": "e",   # e对应e
    "uan": "r", # uan对应r
    "ue": "t",  # ue对应t
    "ve": "t",  # ve（ü的变体）也对应t
    "un": "y",  # un对应y
    "u": "u",   # u对应u
    "i": "i",   # i对应i
    "o": "o",   # o对应o
    "uo": "o",  # uo对应o
    "ie": "p",  # ie对应p
    "a": "a",   # a对应a
    "ong": "s", # ong对应s
    "iong": "s",# iong对应s
    "ai": "d",  # ai对应d
    "ing": "k", # ing对应k
    "uai": "k", # uai对应k
    "ang": "h", # ang对应h
    "an": "j",  # an对应j
    "uang": "l",# uang对应l
    "iang": "l",# iang对应l
    "ou": "z",  # ou对应z
    "ia": "x",  # ia对应x
    "ua": "x",  # ua对应x
    "ao": "c",  # ao对应c
    "ui": "v",  # ui对应v
    "v": "v",   # v（ü）对应v
    "in": "b",  # in对应b
    "iao": "n", # iao对应n
    "m": "m",   # m对应m（罕见）
    "ian": "m", # ian对应m
    "en": "f",  # en对应f
    "eng": "g", # eng对应g
}

# 常用汉字库：一个字符串，包含500多个常用汉字，用于随机选择练习字。
COMMON_CHARS = (
    "的一是了我不人在他有这个上们来到时大地为子中你说生国年着就那和要她出也得里后自以会"
    "家可下而过天去能对小多然于心学么之都好看起发当没成只如事把还用第样道想作种开美总从"
    "无情己面最女但现前些所同日手又行意动方期它头经长儿回位分爱老因很给名法间斯知世什两"
    "次使身者被高已亲其进此话常与活正感见明问力理尔点文几定本公特做外孩相西果走将月十实"
    "向声车全信重三机工物气每并别真打太新比才便夫再书部水像眼等体却加电主界门利海受听表"
    "德少克代员许稜先口由死安写性马光白或住难望教命花结乐色更拉东神记处让母父应直字场平"
    "报友关放至张认接告入笑内英军候民岁往何度山息线产保务设式近强够曲质决指系形统干流眼"
    "连任量治师观象省元干感流连任量治师观象省元"  # 末尾重复可能是为了扩展
)


class XiaoheLogic:
    """处理汉字到小鹤双拼编码的转换逻辑"""
    # 这个类负责将单个汉字转换为小鹤双拼编码。它是静态类，只有一个方法。

    @staticmethod  # 静态方法，不需要实例化类就能调用
    def get_xiaohe_code(char):
        """获取单个汉字的小鹤双拼编码"""
        # 使用pypinyin获取汉字的声母和韵母。pinyin返回列表嵌套列表，如[['zh'], ['uang']]
        py_initial = pinyin(char, style=Style.INITIALS, strict=False)[0][0]  # 获取声母
        py_final = pinyin(char, style=Style.FINALS, strict=False)[0][0]     # 获取韵母

        # 步骤1：处理声母（第一码）
        code1 = ""  # 初始化第一码为空字符串
        if py_initial:  # 如果有声母
            code1 = INITIALS_MAP.get(py_initial, py_initial)  # 从映射表查找，如果没有就用原字母
        else:
            # 零声母情况：没有声母的字，如“安”，第一码取韵母首字母
            if py_final:  # 如果有韵母
                code1 = py_final[0]  # 取韵母的第一个字母
            else:
                return "??"  # 如果都没有，返回错误码

        # 步骤2：处理韵母（第二码）
        code2 = ""  # 初始化第二码
        if py_final in FINALS_MAP:  # 如果韵母在映射表中
            code2 = FINALS_MAP[py_final]  # 获取对应的字母
        else:
            # 如果不在表中，可能是单字母韵母，直接用自身；否则取最后一个字母作为fallback
            if len(py_final) == 1:  # 单字母
                code2 = py_final
            else:
                code2 = py_final[-1]  # 取末尾字母

        return (code1 + code2).lower()  # 返回两个字母的小写编码


class App(ctk.CTk):
    """小鹤双拼练习应用的主窗口类"""
    # 这个类继承自ctk.CTk，是应用程序的主窗口。它管理界面、事件和逻辑。

    def __init__(self):
        super().__init__()  # 调用父类构造函数，初始化窗口

        self.title("小鹤双拼极速练习")  # 设置窗口标题
        self.geometry("800x600")  # 设置窗口大小为800x600像素
        self.resizable(False, False)  # 禁止用户调整窗口大小

        # 状态变量：这些变量跟踪应用程序的状态
        self.current_char = ""  # 当前显示的汉字
        self.target_code = ""   # 当前汉字的正确编码
        self.total_chars = 0    # 用户输入的总字数
        self.correct_chars = 0  # 正确输入的字数
        self.start_time = None  # 开始练习的时间戳
        self.show_hint = True   # 是否显示编码提示

        # 初始化界面和事件
        self.create_widgets()  # 创建所有UI组件
        self.bind_events()     # 绑定事件监听器
        self.load_new_char()   # 加载第一个随机汉字

    def create_widgets(self):
        """创建界面组件"""
        # 方法用于构建GUI的所有部分。

        # 1. 顶部数据栏：显示WPM和正确率
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")  # 创建框架，透明背景
        self.top_frame.pack(pady=20, padx=20, fill="x")  # 打包到窗口顶部，填充x轴

        self.wpm_label = ctk.CTkLabel(  # WPM标签
            self.top_frame,
            text="WPM: 0",  # 初始文本
            font=("Arial", 20, "bold"),  # 字体
            text_color="#3B8ED0",  # 蓝色
        )
        self.wpm_label.pack(side="left", padx=20)  # 左侧对齐

        self.acc_label = ctk.CTkLabel(  # 正确率标签
            self.top_frame,
            text="正确率: 100%",  # 初始100%
            font=("Arial", 20, "bold"),
            text_color="#2CC985",  # 绿色
        )
        self.acc_label.pack(side="right", padx=20)  # 右侧对齐

        # 2. 中间显示区：显示汉字、拼音和编码提示
        self.center_frame = ctk.CTkFrame(self)  # 创建框架
        self.center_frame.pack(expand=True, fill="both", padx=50, pady=20)  # 扩展填充中间

        self.char_label = ctk.CTkLabel(  # 汉字标签
            self.center_frame, text="练", font=("SimHei", 120)  # 大字体显示汉字
        )
        self.char_label.place(relx=0.5, rely=0.4, anchor="center")  # 居中放置

        # 拼音提示标签
        self.hint_label = ctk.CTkLabel(
            self.center_frame, text="lian", font=("Arial", 24), text_color="gray"
        )
        self.hint_label.place(relx=0.5, rely=0.6, anchor="center")  # 下方居中

        # 编码提示标签（可隐藏）
        self.code_hint_label = ctk.CTkLabel(
            self.center_frame,
            text="[lm]",  # 示例编码
            font=("Arial", 20, "bold"),
            text_color="#E04F5F",  # 红色
        )
        self.code_hint_label.place(relx=0.5, rely=0.7, anchor="center")  # 更下方

        # 3. 底部输入和控制：输入框和按钮
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")  # 底部框架
        self.bottom_frame.pack(pady=30, fill="x")  # 底部打包

        # 输入框：用户输入编码的地方
        self.entry = ctk.CTkEntry(
            self.bottom_frame,
            placeholder_text="在此输入...",  # 占位符
            width=200,
            height=50,
            font=("Arial", 24),
            justify="center",  # 居中对齐
        )
        self.entry.pack(pady=10)  # 打包
        self.entry.focus()  # 启动时聚焦输入框

        # 按钮区
        self.btn_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")  # 按钮框架
        self.btn_frame.pack(pady=10)  # 打包

        self.toggle_hint_btn = ctk.CTkButton(  # 切换提示按钮
            self.btn_frame, text="隐藏提示", command=self.toggle_hint  # 点击调用toggle_hint
        )
        self.toggle_hint_btn.pack(side="left", padx=10)  # 左侧

        self.map_btn = ctk.CTkButton(  # 键位图按钮
            self.btn_frame,
            text="查看键位图",
            command=self.show_key_map,  # 点击调用show_key_map
            fg_color="gray",  # 灰色
        )
        self.map_btn.pack(side="left", padx=10)  # 中间

        self.reset_btn = ctk.CTkButton(  # 重置按钮
            self.btn_frame,
            text="重置数据",
            command=self.reset_stats,  # 点击调用reset_stats
            fg_color="#E04F5F",  # 红色
            hover_color="#C0392B",  # 悬停时颜色
        )
        self.reset_btn.pack(side="left", padx=10)  # 右侧

    def bind_events(self):
        """绑定事件监听"""
        # 将输入框的按键释放事件绑定到check_input方法
        self.entry.bind("<KeyRelease>", self.check_input)  # 每当用户释放按键时检查输入

    def load_new_char(self):
        """加载一个新的随机汉字"""
        # 从COMMON_CHARS中随机选择一个汉字
        self.current_char = random.choice(COMMON_CHARS)
        # 获取该汉字的小鹤编码
        self.target_code = XiaoheLogic.get_xiaohe_code(self.current_char)

        # 更新UI显示
        self.char_label.configure(text=self.current_char)  # 显示汉字

        # 获取完整拼音用于提示
        full_pinyin = pinyin(self.current_char, style=Style.NORMAL)[0][0]
        self.hint_label.configure(text=full_pinyin)  # 显示拼音

        # 根据show_hint决定是否显示编码
        if self.show_hint:
            self.code_hint_label.configure(text=f"[{self.target_code}]")  # 显示编码
        else:
            self.code_hint_label.configure(text="[??]")  # 隐藏

        # 清空输入框，准备新输入
        self.entry.delete(0, "end")

    def check_input(self, event):
        """检查用户输入"""
        # 获取输入框的内容，转小写并去空格
        user_input = self.entry.get().lower().strip()

        # 如果是第一次输入，记录开始时间
        if self.start_time is None and len(user_input) > 0:
            self.start_time = time.time()  # 记录当前时间

        # 小鹤双拼编码总是2个字母
        if len(user_input) >= 2:  # 当输入达到2个字符时
            self.total_chars += 1  # 总输入数+1
            if user_input == self.target_code:  # 如果匹配
                self.correct_chars += 1  # 正确数+1
                self.flash_feedback("green")  # 绿色反馈
                self.load_new_char()  # 加载新字
            else:
                self.flash_feedback("red")  # 红色反馈
                self.entry.delete(0, "end")  # 清空，让用户重输

            self.update_stats()  # 更新统计数据

    def flash_feedback(self, color):
        """简单的视觉反馈"""
        # 获取输入框的原始边框颜色
        original_color = self.entry.cget("border_color")
        # 根据参数选择反馈颜色
        flash_color = "#2CC985" if color == "green" else "#E04F5F"

        # 设置边框为反馈颜色，宽度2
        self.entry.configure(border_color=flash_color, border_width=2)
        # 200毫秒后恢复原始颜色
        self.after(200, lambda: self.entry.configure(border_color=original_color))

    def update_stats(self):
        """更新 WPM 和 正确率"""
        # 如果有输入，计算正确率
        if self.total_chars > 0:
            acc = (self.correct_chars / self.total_chars) * 100  # 百分比
            self.acc_label.configure(text=f"正确率: {acc:.1f}%")  # 更新标签，保留1位小数

        # 如果有开始时间，计算WPM
        if self.start_time:
            elapsed_min = (time.time() - self.start_time) / 60  # 经过分钟数
            if elapsed_min > 0:
                wpm = int(self.correct_chars / elapsed_min)  # 每分钟正确字数
                self.wpm_label.configure(text=f"WPM: {wpm}")  # 更新标签

    def toggle_hint(self):
        """切换提示显示"""
        # 切换show_hint状态
        self.show_hint = not self.show_hint
        # 更新按钮文本
        self.toggle_hint_btn.configure(
            text="显示提示" if not self.show_hint else "隐藏提示"
        )
        # 刷新当前汉字的提示显示
        if self.show_hint:
            self.code_hint_label.configure(text=f"[{self.target_code}]")
        else:
            self.code_hint_label.configure(text="[??]")

        self.entry.focus()  # 聚焦输入框

    def reset_stats(self):
        """重置统计数据"""
        # 重置所有统计变量
        self.total_chars = 0
        self.correct_chars = 0
        self.start_time = None
        # 重置标签
        self.wpm_label.configure(text="WPM: 0")
        self.acc_label.configure(text="正确率: 100%")
        # 加载新字
        self.load_new_char()
        self.entry.focus()  # 聚焦输入框

    def show_key_map(self):
        """弹窗显示口诀/键位"""
        # # 创建一个新的顶级窗口（弹窗）
        # dialog = ctk.CTkToplevel(self)
        # dialog.title("小鹤双拼键位参考")  # 标题
        # dialog.geometry("500x400")  # 大小

        # # 定义键位映射文本
        # text_map = (
        #     "【小鹤双拼口诀】\n\n"
        #     "Q - Qiu (秋)   |  W - Wei (卫)   |  R - Ruan (软)\n"
        #     "T - Tue (特)   |  Y - Yun (韵)   |  O - uO (窝)\n"
        #     "P - Pie (撇)   |  S - Song (松)  |  D - Dai (代)\n"
        #     "F - Fen (分)   |  G - Geng (更)  |  H - Hang (航)\n"
        #     "J - an (安)    |  K - Kuai (快)  |  L - Liang (两)\n"
        #     "Z - Zou (走)   |  X - Xia (夏)   |  C - Cao (草)\n"
        #     "V - Vui (追)   |  B - Bin (滨)   |  N - Niao (鸟)\n"
        #     "M - Mian (棉)\n\n"
        #     "【零声母规则】\n"
        #     "以元音开头的字，首字母为第一码，韵母所在键为第二码。\n"
        #     "例：安(an) -> aj | 欧(ou) -> oz | 啊(a) -> aa"
        # )

        # # 创建标签显示文本
        # label = ctk.CTkLabel(
        #     dialog, text=text_map, font=("SimHei", 16), justify="left", padx=20, pady=20
        # )
        # label.pack(expand=True, fill="both")  # 填充弹窗


if __name__ == "__main__":
    # 如果这个文件是直接运行的（不是被导入），则启动应用程序
    app = App()  # 创建App实例
    app.mainloop()  # 启动Tkinter主循环，显示窗口并处理事件