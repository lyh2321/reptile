from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor  # 线程池，进程池
import threading, time


def test(arg):
    print(arg, threading.current_thread().name)
    time.sleep(1)


if __name__ == "__main__":
    thread_pool = ThreadPoolExecutor(5)  # 定义5个线程执行此任务
    process_pool = ProcessPoolExecutor(5)  # 定义5个进程
    for i in range(20):
        thread_pool.submit(test, i)
