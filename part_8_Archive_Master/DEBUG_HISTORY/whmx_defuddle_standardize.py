# -*- coding: utf-8 -*-
import time
import os
from curl_cffi import requests

# 全量名单
character_list = ["酒帐", "赤壁赋页", "麟趾马蹄金", "天球仪", "莫高窟记", "铜壶滴漏", "太阳神鸟", "真珠宝幢", "微缩家具", "午门", "青瓷莲花尊", "铜坐龙", "曾侯乙编钟", "铜奔马", "鎏金骑士", "毛公鼎", "溪山行旅图", "水晶杯", "鹿王本生图", "海错图", "卷云金喇叭", "亚长牛尊", "上阳台帖", "兔形陶埙", "四龙四凤座", "越王勾践剑", "金瓯永固杯", "铜车马", "雪景寒林图", "星月夜", "三兔藻井", "万工轿", "小宋香炉", "青铜仙鹤", "云雷纹大铙", "狸猫盘", "金蝉玉叶", "宋金项饰", "彩凤鸣岐", "愿望杯", "金石录", "睡莲", "王氏书翰卷", "素纱单衣", "百花图卷", "秦公镈", "T形帛画", "银香囊", "千里江山图", "洛神赋图", "贾湖骨笛", "白石散乐", "芙蓉炉", "莫高窟220", "五弦琵琶", "断臂维纳斯", "向日葵", "银雀山汉简", "敦煌飞天", "海水江崖炉", "浑天仪", "商周十供", "鸟音山水钟", "十二花卉杯", "利簋", "五星出东方", "莲塘乳鸭图", "琉璃塔拱门", "阴山岩画", "宴猎攻战壶", "妇好鸮尊", "吴王夫差矛", "大盂鼎", "夜行铜牌", "样式雷", "商鞅方升", "战国铜冰鉴", "少虡剑", "鎏金银壶", "制盐砖", "天亡簋", "七盘舞砖", "扯淡碑", "跪射俑", "克拉克瓷", "外销壁纸", "茶叶生产画", "鹿角立鹤", "格萨尔唐卡", "自来火二号", "大神龛", "万国全图", "粉白双耳瓶", "针铺铜版", "商周铜人", "聊斋图说", "长信宫灯", "玉琮王", "蝠桃瓶", "天蓝瓶", "诗文执壶", "皇后之玺", "晋侯鸟尊", "白龙梅瓶", "丙午神钩", "玛雅陶碗", "战国铜餐具", "人头瓶", "白釉绿彩瓶", "驿使图砖", "宝石冠", "蒙医药袋", "蛙锣", "可爱花束", "山水人物镜", "心形枪", "龙纹陶盘", "鹦鹉银罐", "天气卜骨", "冷暖自知印", "果树双管瓶", "舞蹈陶盆", "五柱器"]

output_dir = r"C:\Users\Wwaiting\PycharmProjects\WuHuaMiXin\whmx\wiki_data\markdown_archives"

def sync_defuddle(name):
    target_url = f"https://wiki.biligame.com/whmx/{name}"
    reader_url = f"https://defuddle.md/{target_url}"
    print(f"Defuddle Sync: {name} ...", flush=True)
    
    try:
        r = requests.get(reader_url, impersonate="chrome", timeout=40)
        if r.status_code == 200:
            with open(os.path.join(output_dir, f"{name}.md"), "w", encoding="utf-8") as f:
                f.write(r.text)
            return True
        else:
            print(f"  Failed {name}: {r.status_code}", flush=True)
            return False
    except Exception as e:
        print(f"  Error {name}: {str(e)}", flush=True)
        return False

if __name__ == "__main__":
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for char in character_list:
        sync_defuddle(char)
        time.sleep(1) # defuddle 非常快，只需极短延迟
    print("\nDefuddle Sync Finished!")
