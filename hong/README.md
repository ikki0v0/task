## 代码内容：
提取excel里KKS，QS Status，K Max (Front)的对应值，整合成一个新excel

## 使用方法：
1. 在.py所在文件夹内 shift+鼠标右键
2. 选择“在此处打开 Powershell窗口”
3. 输入"python ./mini_hong.py"   （双引号内为输入内容，请不要输入双引号）
4. 根据提示输入路径，windows默认使用单反斜杠连接（\），如从文件系统中复制路径，请记得更改

## 输入：
1. data_root：csv文件所在的总文件夹路径，程序以它为总目录向下遍历。
2. output_path：输出csv文件的路径（请不要设置在data_root文件夹以及它子目录下）。

## 输出：
|   |    name|     time|  KKS| QS Status|K Max (Front)|                            filename|
|---|--------|---------|-----|----------|-------------|------------------------------------|
|  1|ChenHeng|2017/7/18|    -|        OK|        44.26|Chen_Heng_OS_18072017_155337_ELE.CSV|

## 注意事项：
- 路径名称书写规范：请使用正斜杠"/"或双反斜杠"\\\\"进行连接。
  - 示例：F:/python/other/FFKC CSV文件
  - 示例：F:\\\\python/other/FFKC CSV文件  （混用也可以）
- 输入的第一个变量data_root文件夹内，请不要包含不相关csv文件。
- 运行程序时，请先关闭生成的intergration.csv文件，否则会无法更改导致报错。
- 请不要更改原始csv文件名，受试者姓名和检查时间是从文件名中提取。
