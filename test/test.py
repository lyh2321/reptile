import os


def get_dir(path):  # 获取目录路径
    print("所有目录路径是：")
    for root, dirs, files in os.walk(path):  # 遍历path及每个目录，有3个参数，root表示目录路径，dirs表示当前目录的目录名，files代表当前目录的文件名
        print(root)


if os.path.exists(str('/access')):
    print(1)
else:
    print(2)
