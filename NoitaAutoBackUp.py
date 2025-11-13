'''
形如noita这样的少数独立游戏不支持游戏内的读档与存档备份功能，导致玩家在游戏过程中一旦存档损坏或误操作时将面临全部游戏进度丢失的风险。尤其是noita还是高难度游戏，频繁的存档备份与读档需求尤为迫切。
本代码用于实现游戏存档自动保存与读档
目前功能以实现：
1.自动备份当前存档至指定目录，支持自定义备份数量上限，超过上限自动删除最早备份
2.恢复存档至最近备份或指定时间点备份
待完成：
3.支持回滚功能，即恢复存档前自动备份当前存档，支持自定义回滚备份数量上限
4.支持自定义预设体，方便不同游戏存档的备份与恢复
5.图形界面
6.多档选择功能

os进阶练习
'''

'''
日志
20251112
    - 创建文件，创立基本框架
    - Todo：备份与恢复功能待实现
20251113
    - 实现备份与恢复功能
    - Todo：
        1.回滚备份与备份功能重叠，可修正，简化代码
        2.保存预设体
        3.多档选择功能
        4.图形界面
    - 经验：
        1.shutil.copytree()函数用于复制文件夹内的子文件，第二个参数目录对应需要新创建的文件夹
'''

import os
import shutil
import datetime

#CurrentSaveDirectory
csd = r""

#BackupSaveDirectory
bsd = r""

#ToBackupFileName
tbn = ""

#BackupNumberLimit
bnl = 5

#RollbackDirectory
rd = r""

#RestoreNumberLimit
rnl = 2

#本模块预实现内容：1.修改上述内容并预存一定游戏的对应数据 2.支持添加新预设
def ChangeVarContent():
    global csd, bsd, tbn

    def TempContent():
        global csd, bsd, tbn, rd

        print("已选择临时输入模式")

        newpathcsd = input("请输入当前存档目录路径：\n")
        csd = rf"{newpathcsd}"
        newpathbsd = input("请输入备份存档目录路径：\n")
        bsd = rf"{newpathbsd}"
        newpathrd = input("请输入回滚备份目录路径：\n")
        rd = rf"{newpathrd}"
        tbn = input("请输入备份存档文件名：\n")

    def DefineContent():
        global csd, bsd, tbn ,rd

        print("已选择自定义预设体模式")

        Prefabs = []
        '''
        添加预设实现方法如下：
        1.创建txt文件存储数据
        2.每次运行程序时读取txt文件内容至Prefabs列表
        3.提供接口供用户添加新预设至Prefabs列表并写入txt文件
        '''
        op = input("选择对应预设体\n")
        csd = Prefabs[op][0]
        bsd = Prefabs[op][1]
        tbn = Prefabs[op][2]
        rd  = Prefabs[op][3]

    def NoitaContent():
        global csd, bsd, tbn,rd

        print("已选择Noita预设体")
        csd = r"C:\Users\17903\AppData\LocalLow\Nolla_Games_Noita"
        bsd = r"C:\Users\17903\AppData\LocalLow\Nolla_Games_Noita\BackUp"
        rd  = r"C:\Users\17903\AppData\LocalLow\Nolla_Games_Noita\RockBack"
        tbn = "Save00"

    while True:
        op = input("请选择备份模式 1.TempContent 2.DefineContent 3.NoitaContent \n")
        if ("1" in op):
            TempContent()
            return
        elif ("2" in op):
            DefineContent()
            return
        elif ("3" in op):
            NoitaContent()
            return
        else:
            warning("输入错误")

def warning(str):
    print(str)

def IsExist():
    if not (os.path.exists(csd)):
        return False

    # 创建备份基础目录（如果不存在）
    elif not (os.path.exists(bsd)): 
        print(f"正在创建备份目录: {bsd}")
        os.makedirs(bsd)
        print("备份目录创建成功")
    print("路径检测通过")
    return True

#本模块预实现内容：1.备份且保存时间戳 2.用户自定义备份数目，超过上限备份自动删除 
def BackUp():
    print("正在执行备份操作...")
    
    if not (os.path.exists(os.path.join(csd,tbn))):
        print("存档文件不存在，备份失败")
        return False

    #生成带时间戳的备份文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    NewName = timestamp + "_" + tbn

    #检测是否已存在备份文件
    if (os.path.exists(os.path.join(bsd,NewName))):
        warning("已存在同名备份文件，备份失败")
        return False
    else:
        print("正在备份存档文件...")
        shutil.copytree(os.path.join(csd,tbn),os.path.join(bsd,NewName))
        print(f"已成功备份至 {bsd}\{NewName}\n")

        #检测备份文件列表并排序删除多余备份
        if(len(os.listdir(bsd)) > bnl):
            print("检测到多余备份文件，正在删除...")
            BackUpList = os.listdir(bsd)
            BackUpList.sort()
            for i in range(len(BackUpList)-bnl):
                shutil.rmtree(os.path.join(bsd,BackUpList[i]))
                print(f"已删除多余备份文件 {BackUpList[i]}")
            print("多余备份文件删除完成\n")
    return

#本模块预实现内容：1.恢复存档至指定时间，默认最近 2.保留最近被恢复的两次操作（可自定义），以实现撤销
def Restore():
    #获取备份列表并排序
    BackUpList = os.listdir(bsd)
    BackUpList.sort(reverse=True)

    def RockBack():
        print("正在创建回滚备份...")
        
        #检测是否存在回滚备份
        if not (os.path.exists(rd)):
            os.makedirs(rd)
            print("不存在回滚备份目录，正在创建新目录")
            print(f"创建回滚备份目录: {rd}")

        #创建当前存档回滚备份
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        NewName = timestamp + "_" + tbn

        #检测是否已存在回滚备份文件
        if (os.path.exists(os.path.join(rd,NewName))):
            warning("已存在同名备份文件，备份失败")
            return False
        else:
            print("正在备份当前存档文件作为回滚备份...")
            shutil.copytree(os.path.join(csd,tbn),os.path.join(rd,NewName))
            print(f"已成功备份至回滚目录 {rd}\{NewName}")

        #检测回滚备份数量并删除多余备份
        if(len(os.listdir(rd)) >= rnl):
            RockBackList = os.listdir(rd)
            RockBackList.sort()
            shutil.rmtree(os.path.join(rd,RockBackList[0]))
            print(f"已删除多余回滚备份文件 {RockBackList[0]}")

    def restore(num):
        RockBack()
        LatestBackUp = BackUpList[num]
        shutil.rmtree(os.path.join(csd,tbn),ignore_errors=True)
        print(f"已删除现有存档 {tbn} ")
        shutil.copytree(os.path.join(bsd,LatestBackUp),os.path.join(csd,tbn))

    while True:
        print("请选择恢复方式：")
        op = input("1.恢复至最近备份 \n2.恢复至指定时间备份\n3.取消恢复\n")
        if ("1" in op):
            #检测是否存在备份
            if(len(BackUpList) == 0):
                warning("不存在任何备份文件，恢复失败")
                return False
            else:
                #恢复最近备份
                restore(0)
                print(f"已成功恢复至最近备份")
                return True

        elif ("2" in op):

            for i in range(len(BackUpList)):
                print(f"{i+1}. {BackUpList[i]}")

            while True:
                num = int(input("请输入需要恢复的备份序号：\n")) - 1

                #检测输入序号合法性
                if(num < 0 or num >= len(BackUpList) or not isinstance(num,int)):
                    warning("输入序号有误，请重新输入")
                else:
                    break

            restore(num)
            print(f"已成功恢复至指定备份 {BackUpList[num]}")
            return True
        elif ("3" in op):
            print("已取消恢复操作")
            return False
        else:
            warning("输入错误")

#本模块预实现内容：1.根据传入内容决定执行模块
def Main():
    while True:
        print("欢迎使用存档自动备份与恢复工具！")

        while True:
            ChangeVarContent()
            if not (IsExist()):
                warning("路径不存在")
            else:
                break

        while True:
            print(f"\n存档路径：{csd} \n备份路径：{bsd} \n备份文件名：{tbn} \n回滚备份路径{rd}\n")
            op = input("选择操作1.BackUp  2.Restore  3.Quit\n")
            if ("3" in op):    break
            elif ("1" in op):  BackUp()
            elif ("2" in op):  Restore()
            else:          warning("输入错误")
Main()