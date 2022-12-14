import os
from chardet import detect
import time
import pandas as pd
from tqdm import tqdm

data_root = input("请输入csv文件所在的总文件夹路径： ")  # input输入地址自带双引号！！
output_path = input("请输入保存程序生成文件的路径： ")


# 定义预处理需要的操作
def get_filelist(dir_path):
    """遍历：遍历文件夹内文件：传入需要遍历的文件夹路径，返回其内所有文件的完整路径列表"""
    Filelist = []
    for home, dirs, files in os.walk(dir_path):
        for filename in files:
            # 文件名列表，包含完整路径
            Filelist.append(os.path.join(home, filename))
    return Filelist


def change_encode(file_list):
    """转码：路径列表里的csv文件批量转换为utf-8编码格式"""
    for file_path in tqdm(file_list):
        if ".CSV" in file_path:
            with open(file_path, 'rb+') as fp:
                content = fp.read()
                encoding = detect(content)['encoding']
                content = content.decode(encoding).encode('utf8')
                fp.seek(0)
                fp.write(content)


def get_string(path_string):
    """字符串处理：输入路径名，返回受试者姓名，测量日期，文件名"""
    filename = path_string.split("\\")[-1]
    # 提取姓名
    info = filename.split("_")
    person = info[0] + info[1]
    # 提取时间
    raw_time = time.strptime(info[3], "%d%m%Y")
    ftime = time.strftime("%Y/%m/%d", raw_time)
    return person, ftime, filename


# 开始处理
print("\nfilelist: begin to obtain")
filelist = get_filelist(data_root)
print("filelist: obtained\n")

print("encoding format change: begin to change")
change_encode(filelist)
print("encoding format change: complete\n")

# 批量提取KKS、QS status的值
colname = ('name', 'time', 'KKS', 'QS Status', 'K Max (Front)', 'filename')
total = pd.DataFrame(index=[0], columns=colname)

print("begin to extract kks&qs status values")
for file_path in tqdm(filelist):
    if ".CSV" in file_path:  # 如果是csv文件，进入处理
        df = pd.read_csv(file_path, sep=";", encoding="utf8")

        # 当文件中不存在KKS和QS status时，避免崩溃
        try:
            # 提取第一列为KKS的第二列值
            kks_bool = (df.iloc[:, 0] == 'KKS')  # KKS所在行为True
            kks = df[kks_bool].iloc[0, 1]
            kks = kks.split()[-1]
            # 提取第一列为QS Status的第二列值
            qs_bool = (df.iloc[:, 0] == 'QS Status')  # qs所在行为True
            qs = df[qs_bool].iloc[0, 1]
            # 提取第一列为K Max (Front)的第二列值
            kmax = (df.iloc[:, 0] == 'K Max (Front)')  # KKS所在行为True
            kmax = df[kmax].iloc[0, 1]
            # 得到图片名和日期
            str = get_string(file_path)

            s = pd.DataFrame({'name': str[0], 'time': str[1], 'KKS': kks, 'QS Status': qs,
                              'K Max (Front)': kmax, 'filename': str[2]},
                             index=[0])
            total = pd.concat([total, s], ignore_index=True)

        except IndexError:
            print("Cannot find KKS and QS status in {}!".format(file_path))

# 保存到“integration.csv”文件
total = total.drop(0)  # 删除初始创建的索引0
total.to_csv(os.path.join(output_path, 'integration.csv'), header=True)

print("\n提取完成|ω·)\n")
