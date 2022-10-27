# 把excel的数字复制进BUII并计算（左右眼无差异）
# 不要debug，会卡死
import os
import time
from selenium import webdriver
from chardet import detect
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait  # 导入显性等待的包
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from tqdm import tqdm

path = 'D:\\Program Files\\chromedriver.exe'  # chromedriver.exe不在python安装目录，则需要手动设置位置
data_root = "F:\\deep learning\\other\\公式计算"
data_path = os.path.join(data_root, "CTR补.csv")  # 病人参数读取路径
web_path = os.path.join(data_root, "web_xpath.csv")


# 定义预处理操作
def change_encode(file_path):
    """转码：路径列表里的csv文件批量转换为utf-8编码格式"""
    with open(file_path, 'rb+') as fp:
        content = fp.read()
        encoding = detect(content)['encoding']
        content = content.decode(encoding).encode('utf_8_sig')
        fp.seek(0)
        fp.write(content)


def init_info():
    """填写初始无关信息"""
    driver.find_element_by_xpath(xpath.loc['surgeon', f]).send_keys(1)  # Doctor name
    driver.find_element_by_xpath(xpath.loc['patient', f]).send_keys(1)  # Patient name
    driver.find_element_by_xpath(xpath.loc['patientid', f]).send_keys(1)  # Patient ID


def fill_parameters(series):
    """填写眼部生物学参数，传入series"""
    driver.find_element_by_xpath(xpath.loc['constant', f]).send_keys(str(series['constant']))  # 以字符串格式输入！！

    driver.find_element_by_xpath(xpath.loc['AL', f]).send_keys(str(series['AL']))  # AL
    driver.find_element_by_xpath(xpath.loc['K1', f]).send_keys(str(series['K1']))  # K1
    driver.find_element_by_xpath(xpath.loc['K2', f]).send_keys(str(series['K2']))  # K2
    driver.find_element_by_xpath(xpath.loc['ACD', f]).send_keys(str(series['ACD']))  # ACD

    driver.find_element_by_xpath(xpath.loc['LT', f]).send_keys(str(series['LT']))  # LT
    driver.find_element_by_xpath(xpath.loc['CCT', f]).send_keys(str(series['CCT']))  # CCT


def get_result():
    """点击计算并切换到结果界面，获取IOL度数和对应的refraction"""

    driver.find_element_by_xpath(xpath.loc['calculate', f]).click()  # 点击计算
    # 等待结果加载出来
    WebDriverWait(driver, 10, 0.5).until(
        EC.visibility_of_element_located((By.XPATH, xpath.loc['result', f]))
    )

    # 获取结果列表
    d = driver.find_element_by_xpath(xpath.loc['result', f]).text
    list = d.split()
    # list = list[34:44]
    return list


# 读取excel
change_encode(data_path)
df = pd.read_csv(data_path, header=0, encoding="utf-8")  # 读取数据
# 读取对应公式网站的xpath
f = 'kane'  # 确定计算的公式
xpath = pd.read_csv(web_path, header=0, index_col=0, encoding="utf-8")  # 读取每个网站对应的xpath


# 打开网页
driver = webdriver.Chrome(executable_path=path)
url = "https://www.iolformula.com/"
driver.get(url)

driver.find_element_by_xpath('//*[@id="post-30"]/div/div/div').click()  # 点击接受
time.sleep(2)

# 遍历数据框
for i in tqdm(range(df.shape[0])):
    series = df.iloc[i]
    val = 0  # 用与调整结果的晶体度数范围

    if df.loc[i, 'CCT']>650:
        continue

    # 填写信息
    init_info()   # 初始病人信息填写
    fill_parameters(series)  # 把数据输进网页
    # 选择病人的性别
    if series['gender'] == 'm':
        driver.find_element_by_xpath(xpath.loc['male', f]).click()
    elif series['gender'] == 'f':
        driver.find_element_by_xpath(xpath.loc['female', f]).click()

    list = get_result()  # 计算并得到结果列表

    power = float(series['power'])
    # kane的结果里整数power也是float的形式
    # if power%1 == 0:   # 如果是整数，转换为int类型，否则barret会对不上
    #     power = int(power)

    # 不断调整，直到结果列表里有对应的晶体power
    while power > float(list[5]):
        val = val - 1
        driver.find_element_by_xpath(xpath.loc['back', f]).click()  # 返回填写页面
        driver.find_element_by_xpath(xpath.loc['refraction', f]).clear()
        driver.find_element_by_xpath(xpath.loc['refraction', f]).send_keys(val)  # Refraction
        # 计算
        list = get_result()

    if str(power) in list:  # 记得索引字符串！！
        refraction = list[list.index(str(power)) + 1]

    df.loc[i, f] = refraction
    print(df.iloc[i, :])

    # 初始化回原来的界面
    driver.find_element_by_xpath(xpath.loc['back', f]).click()  # 返回填写页面
    time.sleep(1)
    driver.find_element_by_xpath(xpath.loc['clear', f]).click()  # 清空页面

df.to_csv(os.path.join(data_root, 'result.csv'), header=True, encoding='utf_8_sig')
print("计算完成！")


