# 把excel的数字复制进BUII并计算（左右眼无差异）
# 不要debug，会卡死
import os
import time
from selenium import webdriver
from chardet import detect
from selenium.webdriver.common.keys import Keys
import pandas as pd
from tqdm import tqdm

path = 'D:\\Program Files\\chromedriver.exe'  # chromedriver.exe不在python安装目录，则需要手动设置位置
data_root = "F:\\deep learning\\other\\公式计算"
data_path = os.path.join(data_root, "CTR_after.csv")


# 定义预处理操作
def ChangeEncode(file_path):
    """转码：路径列表里的csv文件批量转换为utf-8编码格式"""
    with open(file_path, 'rb+') as fp:
        content = fp.read()
        encoding = detect(content)['encoding']
        content = content.decode(encoding).encode('utf_8_sig')
        fp.seek(0)
        fp.write(content)


def InitInfo():
    """填写初始无关信息"""
    driver.find_element_by_xpath('//*[@id="MainContent_DoctorName"]').send_keys(1)  # Doctor name
    driver.find_element_by_xpath('//*[@id="MainContent_PatientName"]').send_keys(1)  # Patient name
    driver.find_element_by_xpath('//*[@id="MainContent_PatientNo"]').send_keys(1)  # Patient ID


def FillParameters(series):
    """填写眼部生物学参数，传入series"""
    driver.find_element_by_xpath('//*[@id="MainContent_Aconstant"]').send_keys(str(series['constant']))  # 以字符串格式输入！！

    driver.find_element_by_xpath('//*[@id="MainContent_Axlength"]').send_keys(str(series['AL']))  # AL
    driver.find_element_by_xpath('//*[@id="MainContent_MeasuredK1"]').send_keys(str(series['K1']))  # K1
    driver.find_element_by_xpath('//*[@id="MainContent_MeasuredK2"]').send_keys(str(series['K2']))  # K2
    driver.find_element_by_xpath('//*[@id="MainContent_OpticalACD"]').send_keys(str(series['ACD']))  # ACD

    driver.find_element_by_xpath('//*[@id="MainContent_LensThickness"]').send_keys(str(series['LT']))  # LT
    driver.find_element_by_xpath('//*[@id="MainContent_WTW"]').send_keys(str(series['WTW']))  # WTW


def Calculate():
    """点击计算并切换到结果界面"""
    driver.find_element_by_xpath('//*[@id="MainContent_Button1"]').click()  # 点击计算
    driver.find_element_by_xpath('//*[@id="MainContent_menuTabs"]/ul/li[2]').click()  # 切换到结果界面
    time.sleep(1)


# 读取excel
ChangeEncode(data_path)
df = pd.read_csv(data_path, header=0, encoding="utf-8")

# 打开网页
driver = webdriver.Chrome(executable_path=path)
url = "https://calc.apacrs.org/barrett_universal2105/"
driver.get(url)

# 遍历数据框
for i in tqdm(range(df.shape[0])):
    series = df.iloc[i]
    val = 0  # 用与调整结果的晶体度数范围

    # 填写信息
    InitInfo()   # 初始病人信息填写
    FillParameters(series)  # 把数据输进网页
    Calculate()

    # 判断power是否在列表里
    d = driver.find_element_by_xpath('//*[@id="MainContent_GridView1"]/tbody').text
    list = d.split()

    power = series['power']
    if power%1 == 0:   # 如果是整数，转换为int类型，否则barret会对不上
        power = int(power)

    # 不断调整，直到结果列表里有对应的晶体power
    while power > float(list[4]):
        val = val - 1
        driver.find_element_by_xpath('//*[@id="MainContent_menuTabs"]/ul/li[1]').click()  # 返回填写页面
        driver.find_element_by_xpath('//*[@id="MainContent_Refraction"]').clear()
        driver.find_element_by_xpath('//*[@id="MainContent_Refraction"]').send_keys(val)  # Refraction
        # 计算
        Calculate()

        d = driver.find_element_by_xpath('//*[@id="MainContent_GridView1"]/tbody').text
        list = d.split()

    if str(power) in list:  # 记得索引字符串！！
        refraction = list[list.index(str(power)) + 2]

    df.loc[i, 'BUII'] = refraction
    print(df.iloc[i, :])

    # 初始化回原来的界面
    driver.find_element_by_xpath('//*[@id="MainContent_menuTabs"]/ul/li[1]').click()  # 返回填写页面
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="MainContent_btnReset"]').click()  # 清空页面

df.to_csv(os.path.join(data_root, 'result.csv'), header=True, encoding='utf_8_sig')

