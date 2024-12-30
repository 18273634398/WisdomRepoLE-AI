# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2024-12-28
# Version   ：1.0
# Description：启动函数
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :None
# ===========================================================================================================
import os
import threading
from dashscope import Threads
from tkinter import filedialog
from tools.AssistantAPI import Assistant
import tkinter as tk
from tkinter import Frame, Scrollbar
from PIL import Image, ImageTk
from datetime import datetime
import markdown
from tkhtmlview import HTMLText

from tools.AssistantAPI.functions.uploadFile import upload

# 设置智库书韵助手ID
Assistant_ID = 'asst_62b7eb6a-2661-4244-97b7-d1f92845cd07'

class ChatApp:
    global Assistant_ID
    def __init__(self, root, thread, title='', subject=''):
        self.root = root
        self.thread = thread
        self.root.title(title)
        self.root.geometry("1000x600")  # 窗口大小保持不变
        self.root.configure(bg="#e8f4fa")  # 设置整体背景颜色
        self.assistant = Assistant.Assistant(Assistant_ID)  # 初始化智库书韵助手

        # 气泡背景色变量
        self.left_bubble_color = "#e6f3ff"  # 左侧气泡背景色
        self.right_bubble_color = "#C4F0C5"  # 右侧气泡背景色

        # 加载头像
        self.my_avatar = ImageTk.PhotoImage(Image.open("./Resource/pic/User.png").resize((50, 50)))
        self.other_avatar = ImageTk.PhotoImage(Image.open("./Resource/pic/Assistant.png").resize((50, 50)))

        # 聊天主题
        self.chat_topic = tk.Label(root, text=subject, font=("黑体", 16), bg="#d1e8ff", fg="#333333", padx=10, pady=5)
        self.chat_topic.pack(fill=tk.X)

        # 创建聊天区域及滚动条
        self.chat_area = Frame(root, width=1000)  # 设置聊天区域的宽度为800px
        self.chat_area.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)

        # 创建滚动条
        self.scrollbar = Scrollbar(self.chat_area)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建一个Canvas用于放置消息框Canvas的宽度为800px
        self.canvas = tk.Canvas(self.chat_area, yscrollcommand=self.scrollbar.set, width=1000)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 将滚动条与Canvas连接
        self.scrollbar.config(command=self.canvas.yview)

        # 创建提示信息
        self.info_label = tk.Label(root, text="智库书韵正在思考、回答...", font=("楷体", 12), bg="#e8f4fa", fg="#333333")
        self.info_label.pack(fill=tk.X, pady=(10, 0))  # 放置在输入框上方，并居中
        self.info_label.pack_forget()  # 隐藏Label
        # 创建上传提示信息
        self.upload_label = tk.Label(root, text="正在上传文件...", font=("楷体", 12), bg="#e8f4fa", fg="#333333")
        self.upload_label.pack(fill=tk.X, pady=(10, 0))  # 放置在输入框上方，并居中
        self.upload_label.pack_forget()  # 隐藏Label

        # 创建一个Frame用于放置消息内容
        self.messages_frame = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.messages_frame, anchor='nw')

        # 更新Canvas的高度
        self.messages_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # 绑定鼠标滚轮事件
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # 上传文件按钮
        self.upload_icon = ImageTk.PhotoImage(Image.open("./Resource/pic/file.png").resize((30, 30)))  # 加载上传图标
        self.upload_button = tk.Button(root, image=self.upload_icon, command=self.upload_file, bg="#e8f4fa", borderwidth=0)
        self.upload_button.pack(side=tk.LEFT, padx=(20, 0), pady=10)  # 较靠近输入框

        # 消息输入区
        self.msg_entry = tk.Entry(root, font=("楷体", 12), bg="#ffffff", fg="#333333", relief="flat", borderwidth=2)
        self.msg_entry.pack(fill=tk.X, side=tk.LEFT, padx=(20, 20), pady=10, expand=True, ipady=5)  # 增加左侧填充

        # 绑定回车事件
        self.msg_entry.bind("<Return>", self.send_message)

        # 发送按钮
        self.send_button = tk.Button(root, text="发送", command=self.send_message, bg="#d1e8ff", fg="#333333", relief="flat", borderwidth=2)
        self.send_button.pack(side=tk.RIGHT, padx=20, pady=10)
        self.root.update_idletasks()  # 强制更新窗口布局



    def upload_file(self):
        def show_dialog():
            # 创建一个新的对话框
            dialog = tk.Toplevel(root)
            dialog.title("确认上传文件")

            # 标签提示用户，设置文本左对齐
            label = tk.Label(dialog, text=f"您确定要上传该文件吗？\n文件名:{file_name}\n文件地址:{file_path}\n文件大小:{file_size}字节", font=("仿宋", 12), anchor="w")
            label.pack(pady=20, padx=10, fill="x")  # 设置填充和对齐

            # 确定按钮
            def on_confirm():
                # 上传逻辑
                # 在此处调用上传接口需要较长时间，因此使用线程异步处理
                def upload_task():
                    upload(file_path, '用户自定义上传', "藏书信息")
                    # 上传完成后，可以在这里添加一些后续操作，例如提示用户上传成功
                    self.upload_label.pack_forget()  # 隐藏Label


                # 创建并启动新线程
                self.upload_label.pack(fill=tk.X, pady=(10, 0))  # 显示Label
                dialog.destroy()  # 关闭弹窗
                upload_thread = threading.Thread(target=upload_task)
                upload_thread.start()

            confirm_button = tk.Button(dialog, text="确定", command=on_confirm)
            confirm_button.pack(side=tk.LEFT, padx=(20, 10), pady=20)

            # 取消按钮
            def on_cancel():
                dialog.destroy()  # 关闭弹窗
            cancel_button = tk.Button(dialog, text="取消", command=on_cancel)
            cancel_button.pack(side=tk.RIGHT, padx=(10, 20), pady=20)

            # 更新窗口以计算内容大小
            dialog.update()
            # 获取按钮的高度
            button_height = confirm_button.winfo_reqheight()
            # 根据内容动态调整窗口大小，额外加上按钮的高度和间距
            dialog.geometry(f"{dialog.winfo_reqwidth()}x{dialog.winfo_reqheight() + button_height + 40}")


        """上传文件的逻辑"""
        file_path = tk.filedialog.askopenfilename()  # 打开文件对话框
        if file_path:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            show_dialog()  # 显示确认上传文件的弹窗





    def toggle_info_label_visibility(self, visible=True):
        """控制提示信息的可见性"""
        if visible:
            self.info_label.pack(fill=tk.X, pady=(10, 0))  # 显示Label
        else:
            self.info_label.pack_forget()  # 隐藏Label

    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def send_message(self, event=None):
        msg = self.msg_entry.get()
        if msg:
            self.display_message(msg, "right")
            self.msg_entry.delete(0, tk.END)
            self.toggle_info_label_visibility(True)
            # 创建一个线程来处理消息接收
            threading.Thread(target=self.async_receive_message, args=(msg,)).start()

    def async_receive_message(self, msg):
        response = Assistant.send_message(self.thread, self.assistant, msg)
        self.receive_message(response)
        # 语音回复
        # text = text2voice(response)
        self.toggle_info_label_visibility(False)

    def receive_message(self, msg):
        if msg:
            self.display_message(msg, "left")

    def display_message(self, msg, side):
        # 创建一个新的Frame来放置时间戳、头像和气泡
        message_frame = Frame(self.messages_frame)

        # 添加时间戳
        timestamp = datetime.now().strftime("%H:%M:%S")
        timestamp_label = tk.Label(message_frame, text=timestamp, font=("楷体", 10), fg="gray")  # 修改为楷体
        timestamp_label.pack(anchor='w' if side == "left" else 'e')

        # 创建一个内嵌的Frame用于头像和气泡
        inner_frame = Frame(message_frame)
        inner_frame.pack(anchor='w' if side == "left" else 'e')

        # 使用grid布局来精确控制头像和气泡的位置
        inner_frame.grid_columnconfigure(0, weight=1)
        inner_frame.grid_columnconfigure(1, weight=1)

        # 将头像添加到内嵌的Frame中
        avatar_label = tk.Label(inner_frame, image=self.other_avatar if side == "left" else self.my_avatar)
        avatar_label.grid(row=0, column=0 if side == "left" else 1, sticky="n", padx=(0, 5) if side == "left" else (5, 0))  # 头像固定在顶部

        # 使用Label来显示消息气泡
        bubble_frame = Frame(inner_frame, bg=self.left_bubble_color if side == "left" else self.right_bubble_color)
        bubble_frame.grid(row=0, column=1 if side == "left" else 0, sticky="n", padx=(5, 0) if side == "left" else (0, 5))  # 气泡固定在顶部

        # 动态计算wraplength
        wraplength = (self.root.winfo_width()-200) /2

        # 判断是否为Markdown文本
        if self.is_markdown(msg):
            html = markdown.markdown(msg)  # 将Markdown转换为HTML
            message_label = HTMLText(bubble_frame, html=html, background=self.left_bubble_color if side == "left" else self.right_bubble_color, font=("楷体", 16))  # 修改为楷体
        else:
            # 普通文本
            message_label = tk.Label(bubble_frame, text=msg, bg=self.left_bubble_color if side == "left" else self.right_bubble_color, fg="#333333", font=("楷体", 16), padx=10, pady=5, wraplength=wraplength, justify="left")  # 修改为楷体，并设置左对齐
        message_label.pack(anchor='w')  # 确保文本左对齐

        message_frame.pack(anchor='w' if side == "left" else 'e', padx=5, pady=5)  # 根据消息方向对齐

        # 滚动到最新消息
        self.canvas.yview_moveto(1)  # 滚动到最底部



    def is_markdown(self, text):
        """判断文本是否为Markdown格式"""
        # 简单的Markdown特征检测
        markdown_patterns = ["# ", "**", "__", "*", "_", "`", "```", "![", "]("]
        for pattern in markdown_patterns:
            if pattern in text:
                return True
        return False

if __name__ == "__main__":
    root = tk.Tk()
    thread = Threads.create()
    app = ChatApp(root, thread,title="聊天界面", subject="智库书韵")
    app.receive_message("你好，欢迎使用智库书韵！有什么图书问题，可以随时咨询我。\n比如：\n1. 如何使用智库书韵？\n2. 《三体》这本书怎么样？\n3.鲁尚武是谁？")
    root.mainloop()



