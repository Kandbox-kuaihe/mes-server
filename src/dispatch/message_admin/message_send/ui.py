import asyncio
import datetime
import random
import threading
from tkinter import *
from tkinter.ttk import *
from dispatch.message_admin.message_send.db import MessageLogDB
from dispatch.message_admin.message_send.http_server import AsyncHttpClient, SendMessage


class WinGUI(Tk):
    def __init__(self):
        super().__init__()
        self.__win()
        self.tk_frame_m91w9y80 = self.__tk_frame_m91w9y80(self)
        self.tk_frame_m91waltl = self.__tk_frame_m91waltl(self.tk_frame_m91w9y80)
        self.tk_label_m91way9h = self.__tk_label_m91way9h(self.tk_frame_m91waltl)
        self.tk_select_box_message_list = self.__tk_select_box_message_list(self.tk_frame_m91waltl)
        self.tk_frame_m91we8fo = self.__tk_frame_m91we8fo(self.tk_frame_m91w9y80)
        self.tk_label_from_time_input = self.__tk_label_from_time_input(self.tk_frame_m91we8fo)
        self.tk_input_from_time_input = self.__tk_input_from_time_input(self.tk_frame_m91we8fo)
        self.tk_frame_m91wiuc8 = self.__tk_frame_m91wiuc8(self.tk_frame_m91w9y80)
        self.tk_label_m91wiuc9 = self.__tk_label_m91wiuc9(self.tk_frame_m91wiuc8)
        self.tk_input_to_time_input = self.__tk_input_to_time_input(self.tk_frame_m91wiuc8)
        self.tk_frame_m91wl8qi = self.__tk_frame_m91wl8qi(self.tk_frame_m91w9y80)
        self.tk_label_m91wl8qj = self.__tk_label_m91wl8qj(self.tk_frame_m91wl8qi)
        self.tk_select_box_is_sequential_list = self.__tk_select_box_is_sequential_list(self.tk_frame_m91wl8qi)
        self.tk_label_frame_m91wodem = self.__tk_label_frame_m91wodem(self.tk_frame_m91w9y80)
        self.tk_label_m91wvpd3 = self.__tk_label_m91wvpd3(self.tk_label_frame_m91wodem)
        self.tk_label_total_messages = self.__tk_label_total_messages(self.tk_label_frame_m91wodem)
        self.tk_label_m91wwuln = self.__tk_label_m91wwuln(self.tk_label_frame_m91wodem)
        self.tk_label_send_successfully = self.__tk_label_send_successfully(self.tk_label_frame_m91wodem)
        self.tk_label_m91wy4cg = self.__tk_label_m91wy4cg(self.tk_label_frame_m91wodem)
        self.tk_label_send_fail = self.__tk_label_send_fail(self.tk_label_frame_m91wodem)
        self.tk_button_send_message = self.__tk_button_send_message(self.tk_frame_m91w9y80)
        self.tk_button_look_number = self.__tk_button_look_number(self.tk_frame_m91w9y80)
        self.mb = MessageLogDB()
        self.send = SendMessage()
        self.loading_window = None  # 用于全局的 loading 窗口

        # 创建异步事件循环
        self.loop = asyncio.new_event_loop()
        # 创建并启动事件循环线程
        self.thread = threading.Thread(target=self.start_loop, args=(self.loop,), daemon=True)
        self.thread.start()

        # 绑定窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_close)


    def start_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    # def on_close(self):
    #     """窗口关闭时的清理操作"""
    #     # 关闭异步资源
    #     self.close_async()
    #     # 停止事件循环
    #     self.loop.call_soon_threadsafe(self.loop.stop)
    #     # 销毁窗口
    #     self.destroy()

    def __win(self):
        self.title("Message Send ")
        self.mb = MessageLogDB()
        self.send = SendMessage()
        # 设置窗口大小、居中
        width = 862
        height = 270
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)

        self.resizable(width=False, height=False)

    def scrollbar_autohide(self, vbar, hbar, widget):
        """自动隐藏滚动条"""

        def show():
            if vbar: vbar.lift(widget)
            if hbar: hbar.lift(widget)

        def hide():
            if vbar: vbar.lower(widget)
            if hbar: hbar.lower(widget)

        hide()
        widget.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Leave>", lambda e: hide())
        if hbar: hbar.bind("<Enter>", lambda e: show())
        if hbar: hbar.bind("<Leave>", lambda e: hide())
        widget.bind("<Leave>", lambda e: hide())

    def v_scrollbar(self, vbar, widget, x, y, w, h, pw, ph):
        widget.configure(yscrollcommand=vbar.set)
        vbar.config(command=widget.yview)
        vbar.place(relx=(w + x) / pw, rely=y / ph, relheight=h / ph, anchor='ne')

    def h_scrollbar(self, hbar, widget, x, y, w, h, pw, ph):
        widget.configure(xscrollcommand=hbar.set)
        hbar.config(command=widget.xview)
        hbar.place(relx=x / pw, rely=(y + h) / ph, relwidth=w / pw, anchor='sw')

    def create_bar(self, master, widget, is_vbar, is_hbar, x, y, w, h, pw, ph):
        vbar, hbar = None, None
        if is_vbar:
            vbar = Scrollbar(master)
            self.v_scrollbar(vbar, widget, x, y, w, h, pw, ph)
        if is_hbar:
            hbar = Scrollbar(master, orient="horizontal")
            self.h_scrollbar(hbar, widget, x, y, w, h, pw, ph)
        self.scrollbar_autohide(vbar, hbar, widget)

    def __tk_frame_m91w9y80(self, parent):
        frame = Frame(parent, )
        frame.place(x=0, y=0, width=861, height=265)
        return frame

    def __tk_frame_m91waltl(self, parent):
        frame = Frame(parent, )
        frame.place(x=0, y=0, width=260, height=81)
        return frame

    def __tk_label_m91way9h(self, parent):
        label = Label(parent, text="message id:", anchor="center", )
        label.place(x=0, y=20, width=97, height=38)
        return label

    def __tk_select_box_message_list(self, parent):
        cb = Combobox(parent, state="normal")  # 允许输入
        values = self.mb.query_all_message_id()  # 获取所有选项
        cb['values'] = values
        cb.place(x=100, y=20, width=160, height=40)
        cb.set(7001)

        # 绑定输入事件，实现搜索功能
        def on_entry_change(event):
            input_text = cb.get()
            filtered_values = [value for value in values if input_text.lower() in str(value).lower()]
            cb['values'] = filtered_values

        cb.bind("<KeyRelease>", on_entry_change)  # 监听键盘输入
        return cb

    def __tk_frame_m91we8fo(self, parent):
        frame = Frame(parent, )
        frame.place(x=299, y=1, width=260, height=81)
        return frame

    def __tk_label_from_time_input(self, parent):
        label = Label(parent, text="from_time: ", anchor="center", )
        label.place(x=0, y=20, width=97, height=38)
        return label

    def __tk_input_from_time_input(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=104, y=20, width=154, height=38)
        # 设置默认值
        ipt.insert(0, str(datetime.datetime.today().date()))  # 默认值为 "2025-04-04"，可以根据需要修改
        return ipt

    def __tk_frame_m91wiuc8(self, parent):
        frame = Frame(parent, )
        frame.place(x=601, y=0, width=260, height=81)
        return frame

    def __tk_label_m91wiuc9(self, parent):
        label = Label(parent, text="to_time: ", anchor="center", )
        label.place(x=0, y=20, width=97, height=38)
        return label

    def __tk_input_to_time_input(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=104, y=20, width=154, height=38)
        ipt.insert(0, str(datetime.datetime.today().date()))
        return ipt

    def __tk_frame_m91wl8qi(self, parent):
        frame = Frame(parent, )
        frame.place(x=0, y=117, width=260, height=81)
        return frame

    def __tk_label_m91wl8qj(self, parent):
        label = Label(parent, text="sequential:", anchor="center", )
        label.place(x=0, y=20, width=97, height=38)
        return label

    def __tk_select_box_is_sequential_list(self, parent):
        cb = Combobox(parent, state="readonly", )
        cb['values'] = ("True", "False")
        cb.place(x=100, y=20, width=160, height=40)
        cb.set('True')
        return cb

    def __tk_label_frame_m91wodem(self, parent):
        frame = LabelFrame(parent, text="number", )
        frame.place(x=601, y=95, width=241, height=167)
        return frame

    def __tk_label_m91wvpd3(self, parent):
        label = Label(parent, text="total messages: ", anchor="center", )
        label.place(x=1, y=0, width=112, height=30)
        return label

    def __tk_label_total_messages(self, parent):
        label = Label(parent, text="", anchor="center", )
        label.place(x=129, y=0, width=112, height=30)
        return label

    def __tk_label_m91wwuln(self, parent):
        label = Label(parent, text="failed to send: ", anchor="center", )
        label.place(x=1, y=97, width=112, height=30)
        return label

    def __tk_label_send_successfully(self, parent):
        label = Label(parent, text="", anchor="center", )
        label.place(x=129, y=49, width=112, height=30)
        return label

    def __tk_label_m91wy4cg(self, parent):
        label = Label(parent, text="send successfully: ", anchor="center", )
        label.place(x=0, y=50, width=112, height=30)
        return label

    def __tk_label_send_fail(self, parent):
        label = Label(parent, text="", anchor="center", )
        label.place(x=129, y=97, width=112, height=30)
        return label

    def show_loading(self):
        """创建并显示 loading 窗口（固定位置）"""
        self.loading_window = Toplevel(self)
        self.loading_window.title("Loading")
        self.loading_window.geometry("300x100")  # 先设置大小，不指定位置

        # 禁止窗口调整
        self.loading_window.resizable(False, False)

        # 添加加载标签
        label = Label(self.loading_window, text="Loading... Please wait", font=("Arial", 14))
        label.pack(expand=True)

        # 窗口显示后强制居中（通过 update_idletasks 确保窗口已渲染）
        self.loading_window.update_idletasks()
        width = self.loading_window.winfo_width()
        height = self.loading_window.winfo_height()
        x = (self.loading_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.loading_window.winfo_screenheight() // 2) - (height // 2)
        self.loading_window.geometry(f"+{x}+{y}")

    def hide_loading(self):
        """关闭 loading 窗口"""
        if self.loading_window:
            self.loading_window.destroy()
            self.loading_window = None

    def __tk_button_send_message(self, parent):
        btn = Button(parent, text="send message", takefocus=False, command=self.run_async)
        btn.place(x=424, y=137, width=119, height=44)
        return btn

    def __tk_button_look_number(self, parent):
        btn = Button(parent, text="message number", takefocus=False, command=self.query_total_number)
        btn.place(x=280, y=137, width=119, height=44)
        return btn

    def run_async(self):
        """将异步任务提交到事件循环"""
        future = asyncio.run_coroutine_threadsafe(self.send_messages(), self.loop)
        # 添加完成回调
        future.add_done_callback(self.update_ui_after_send)

    def update_ui_after_send(self, future):
        """异步操作完成后更新UI"""
        try:
            # 获取协程结果
            success_count, failure_count = future.result()
            # 使用after方法在主线程更新UI
            self.after(0, self.update_labels, success_count, failure_count)
        except Exception as e:
            print("Error during sending messages:", e)

    def update_labels(self, success_count, failure_count):
        """更新成功和失败计数标签"""
        self.tk_label_send_successfully.config(text=str(success_count))
        self.tk_label_send_fail.config(text=str(failure_count))
        if self.loading_window:
            self.loading_window.destroy()
            self.loading_window = None

    async def send_messages(self):
        self.show_loading()
        try:
            if int(self.tk_select_box_message_list.get()) in [7001, 7104, 7108, 7118]:
                data_list = self.send.get_date_7xxx(
                    message_id=int(self.tk_select_box_message_list.get()),
                    from_time=self.tk_input_from_time_input.get(),
                    to_time=self.tk_input_to_time_input.get()
                )
                success_count, failure_count = await self.send.resend_7xxx(
                    data=data_list,
                    sequential=bool(self.tk_select_box_is_sequential_list.get())
                )
            else:
                data_list = self.send.get_date_srsm(
                    message_id=int(self.tk_select_box_message_list.get()),
                    from_time=self.tk_input_from_time_input.get(),
                    to_time=self.tk_input_to_time_input.get()
                )
                success_count, failure_count = await self.send.resend_srsm(
                    data=data_list,
                    sequential=bool(self.tk_select_box_is_sequential_list.get())
                )
            return success_count, failure_count
        finally:
            self.after(0, self.hide_loading)

    def close_async(self):
        """安全关闭异步客户端"""
        try:
            if hasattr(self.send, 'close'):
                coro = self.send.close()
                future = asyncio.run_coroutine_threadsafe(coro, self.loop)
                future.result(timeout=5)  # 等待最多5秒
        except Exception as e:
            print(f"Error closing async client: {e}")

    def on_close(self):
        """安全的窗口关闭处理"""
        try:
            # 取消所有运行中的任务
            asyncio.run_coroutine_threadsafe(self._cancel_all_tasks(), self.loop).result(timeout=2)

            # 关闭资源
            self.close_async()

            # 停止事件循环
            self.loop.call_soon_threadsafe(self.loop.stop)
        finally:
            self.destroy()

    async def _cancel_all_tasks(self):
        """取消所有运行中的异步任务"""
        for task in asyncio.all_tasks(self.loop):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    def query_total_number(self):
        # print(self.tk_select_box_message_list.get())
        if int(self.tk_select_box_message_list.get()) in [7001, 7104, 7108, 7118]:
            total = len(self.mb.query_7xxx_message(message_id=int(self.tk_select_box_message_list.get()),
                                                   from_time=self.tk_input_from_time_input.get(),
                                                   to_time=self.tk_input_to_time_input.get()))
        else:
            total = len(self.mb.query_srsm_message(message_id=int(self.tk_select_box_message_list.get()),
                                                   from_time=self.tk_input_from_time_input.get(),
                                                   to_time=self.tk_input_to_time_input.get()))

        self.tk_label_total_messages.config(text=str(total))

    # async def send_messages(self):
    #     # 显示 loading
    #     # self.show_loading()
    #     if int(self.tk_select_box_message_list.get()) in [7001, 7104, 7108, 7110]:
    #         data_list = self.send.get_date_7xxx(message_id=int(self.tk_select_box_message_list.get()),
    #                                             from_time=self.tk_input_from_time_input.get(),
    #                                             to_time=self.tk_input_to_time_input.get())
    #         success_count, failure_count = await self.send.resend_7xxx(data=data_list, sequential=bool(
    #             self.tk_select_box_is_sequential_list.get()))
    #     else:
    #         data_list = self.send.get_date_srsm(message_id=int(self.tk_select_box_message_list.get()),
    #                                             from_time=self.tk_input_from_time_input.get(),
    #                                             to_time=self.tk_input_to_time_input.get())
    #         success_count, failure_count = await self.send.resend_srsm(data=data_list, sequential=bool(
    #             self.tk_select_box_is_sequential_list.get()))
    #
    #     self.tk_label_send_successfully.config(text=str(success_count))
    #     self.tk_label_send_fail.config(text=str(failure_count))
    #     # 隐藏 loading
    #     # self.hide_loading()
    #
    # def run_async(self):
    #     # 调用异步函数
    #     asyncio.run(self.send_messages())
    #
    # def close_async(self):
    #     self.send.close()


class Win(WinGUI):
    def __init__(self, controller):
        self.ctl = controller
        super().__init__()
        self.__event_bind()
        self.__style_config()
        self.ctl.init(self)

    def __event_bind(self):
        pass

    def __style_config(self):
        pass


if __name__ == "__main__":
    win = WinGUI()
    win.mainloop()
