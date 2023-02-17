import threading


def thread_Timer():
    print("该起床啦...5秒之后再次呼叫你起床...")

    # 声明全局变量
    global t1
    # 创建并初始化线程
    t1 = threading.Timer(5, thread_Timer)
    # 启动线程
    t1.start()


if __name__ == "__main__":
    # 创建并初始化线程
    t1 = threading.Timer(5, thread_Timer)
    # 启动线程
    t1.start()