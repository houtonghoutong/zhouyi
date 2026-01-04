"""
六爻占卜服务

六爻占卜规则：
1. 掷3枚铜钱6次
2. 每次记录正反面数量：
   - 3正0反 = 老阳（9）⚊ → 变为阴
   - 2正1反 = 少阳（7）⚊
   - 1正2反 = 少阴（8）⚋
   - 0正3反 = 老阴（6）⚋ → 变为阳
3. 从下往上排列，得到六爻
4. 根据六爻组成八卦，下三爻为下卦（内卦），上三爻为上卦（外卦）
"""
from typing import List, Dict, Optional


class LiuYaoService:
    """六爻占卜服务"""
    
    # 八卦基础数据 - 爻序从下到上：初爻、二爻、三爻
    TRIGRAMS = {
        (1, 1, 1): {"name": "乾", "symbol": "☰", "nature": "天", "attribute": "刚健"},
        (0, 0, 0): {"name": "坤", "symbol": "☷", "nature": "地", "attribute": "柔顺"},
        (1, 0, 0): {"name": "震", "symbol": "☳", "nature": "雷", "attribute": "动"},
        (0, 1, 0): {"name": "坎", "symbol": "☵", "nature": "水", "attribute": "险"},
        (0, 0, 1): {"name": "艮", "symbol": "☶", "nature": "山", "attribute": "止"},
        (0, 1, 1): {"name": "巽", "symbol": "☴", "nature": "风", "attribute": "入"},
        (1, 0, 1): {"name": "离", "symbol": "☲", "nature": "火", "attribute": "丽"},
        (1, 1, 0): {"name": "兑", "symbol": "☱", "nature": "泽", "attribute": "悦"},
    }
    
    # 六十四卦数据 - key格式：(上卦名, 下卦名)
    # 卦名格式：上卦象+下卦象+卦名，如"天地否"=上乾下坤
    HEXAGRAMS = {
        # 乾宫八卦
        ("乾", "乾"): {"name": "乾为天", "number": 1, "judgment": "元亨利贞"},
        ("乾", "巽"): {"name": "天风姤", "number": 44, "judgment": "女壮，勿用取女"},
        ("乾", "离"): {"name": "天火同人", "number": 13, "judgment": "同人于野，亨"},
        ("乾", "艮"): {"name": "天山遁", "number": 33, "judgment": "亨，小利贞"},
        ("乾", "坤"): {"name": "天地否", "number": 12, "judgment": "否之匪人"},
        ("乾", "兑"): {"name": "天泽履", "number": 10, "judgment": "履虎尾，不咥人"},
        ("乾", "震"): {"name": "天雷无妄", "number": 25, "judgment": "元亨利贞"},
        ("乾", "坎"): {"name": "天水讼", "number": 6, "judgment": "有孚窒惕，中吉"},
        
        # 坤宫八卦
        ("坤", "坤"): {"name": "坤为地", "number": 2, "judgment": "元亨，利牝马之贞"},
        ("坤", "震"): {"name": "地雷复", "number": 24, "judgment": "亨，出入无疾"},
        ("坤", "坎"): {"name": "地水师", "number": 7, "judgment": "贞，丈人吉"},
        ("坤", "兑"): {"name": "地泽临", "number": 19, "judgment": "元亨利贞"},
        ("坤", "乾"): {"name": "地天泰", "number": 11, "judgment": "小往大来，吉亨"},
        ("坤", "巽"): {"name": "地风升", "number": 46, "judgment": "元亨"},
        ("坤", "离"): {"name": "地火明夷", "number": 36, "judgment": "利艰贞"},
        ("坤", "艮"): {"name": "地山谦", "number": 15, "judgment": "亨，君子有终"},
        
        # 震宫八卦
        ("震", "震"): {"name": "震为雷", "number": 51, "judgment": "亨，震来虩虩"},
        ("震", "离"): {"name": "雷火丰", "number": 55, "judgment": "亨，王假之"},
        ("震", "兑"): {"name": "雷泽归妹", "number": 54, "judgment": "征凶，无攸利"},
        ("震", "乾"): {"name": "雷天大壮", "number": 34, "judgment": "利贞"},
        ("震", "坎"): {"name": "雷水解", "number": 40, "judgment": "利西南"},
        ("震", "艮"): {"name": "雷山小过", "number": 62, "judgment": "亨，利贞"},
        ("震", "坤"): {"name": "雷地豫", "number": 16, "judgment": "利建侯行师"},
        ("震", "巽"): {"name": "雷风恒", "number": 32, "judgment": "亨，无咎，利贞"},
        
        # 巽宫八卦
        ("巽", "巽"): {"name": "巽为风", "number": 57, "judgment": "小亨，利有攸往"},
        ("巽", "兑"): {"name": "风泽中孚", "number": 61, "judgment": "豚鱼吉"},
        ("巽", "艮"): {"name": "风山渐", "number": 53, "judgment": "女归吉，利贞"},
        ("巽", "坤"): {"name": "风地观", "number": 20, "judgment": "盥而不荐"},
        ("巽", "乾"): {"name": "风天小畜", "number": 9, "judgment": "亨，密云不雨"},
        ("巽", "离"): {"name": "风火家人", "number": 37, "judgment": "利女贞"},
        ("巽", "坎"): {"name": "风水涣", "number": 59, "judgment": "亨，王假有庙"},
        ("巽", "震"): {"name": "风雷益", "number": 42, "judgment": "利有攸往"},
        
        # 坎宫八卦
        ("坎", "坎"): {"name": "坎为水", "number": 29, "judgment": "习坎，有孚"},
        ("坎", "艮"): {"name": "水山蹇", "number": 39, "judgment": "利西南"},
        ("坎", "坤"): {"name": "水地比", "number": 8, "judgment": "吉，原筮元永贞"},
        ("坎", "震"): {"name": "水雷屯", "number": 3, "judgment": "元亨利贞，勿用有攸往"},
        ("坎", "巽"): {"name": "水风井", "number": 48, "judgment": "改邑不改井"},
        ("坎", "离"): {"name": "水火既济", "number": 63, "judgment": "亨小，利贞"},
        ("坎", "兑"): {"name": "水泽节", "number": 60, "judgment": "亨，苦节不可贞"},
        ("坎", "乾"): {"name": "水天需", "number": 5, "judgment": "有孚，光亨，贞吉"},
        
        # 离宫八卦
        ("离", "离"): {"name": "离为火", "number": 30, "judgment": "利贞，亨"},
        ("离", "震"): {"name": "火雷噬嗑", "number": 21, "judgment": "亨，利用狱"},
        ("离", "乾"): {"name": "火天大有", "number": 14, "judgment": "元亨"},
        ("离", "兑"): {"name": "火泽睽", "number": 38, "judgment": "小事吉"},
        ("离", "巽"): {"name": "火风鼎", "number": 50, "judgment": "元吉，亨"},
        ("离", "坎"): {"name": "火水未济", "number": 64, "judgment": "亨，小狐汔济"},
        ("离", "艮"): {"name": "火山旅", "number": 56, "judgment": "小亨，旅贞吉"},
        ("离", "坤"): {"name": "火地晋", "number": 35, "judgment": "康侯用锡马蕃庶"},
        
        # 艮宫八卦
        ("艮", "艮"): {"name": "艮为山", "number": 52, "judgment": "艮其背，不获其身"},
        ("艮", "离"): {"name": "山火贲", "number": 22, "judgment": "亨，小利有攸往"},
        ("艮", "坎"): {"name": "山水蒙", "number": 4, "judgment": "亨，匪我求童蒙"},
        ("艮", "巽"): {"name": "山风蛊", "number": 18, "judgment": "元亨，利涉大川"},
        ("艮", "坤"): {"name": "山地剥", "number": 23, "judgment": "不利有攸往"},
        ("艮", "兑"): {"name": "山泽损", "number": 41, "judgment": "有孚，元吉"},
        ("艮", "乾"): {"name": "山天大畜", "number": 26, "judgment": "利贞，不家食吉"},
        ("艮", "震"): {"name": "山雷颐", "number": 27, "judgment": "贞吉，观颐"},
        
        # 兑宫八卦
        ("兑", "兑"): {"name": "兑为泽", "number": 58, "judgment": "亨，利贞"},
        ("兑", "艮"): {"name": "泽山咸", "number": 31, "judgment": "亨，利贞"},
        ("兑", "乾"): {"name": "泽天夬", "number": 43, "judgment": "扬于王庭"},
        ("兑", "震"): {"name": "泽雷随", "number": 17, "judgment": "元亨利贞"},
        ("兑", "巽"): {"name": "泽风大过", "number": 28, "judgment": "栋桡，利有攸往"},
        ("兑", "坎"): {"name": "泽水困", "number": 47, "judgment": "亨，贞大人吉"},
        ("兑", "离"): {"name": "泽火革", "number": 49, "judgment": "己日乃孚"},
        ("兑", "坤"): {"name": "泽地萃", "number": 45, "judgment": "亨，王假有庙"},
    }
    
    # 爻位名称
    LINE_NAMES = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
    
    def calculate_line(self, coins: List[int]) -> Dict:
        """
        根据三枚铜钱的正反面计算单爻
        
        参数：
            coins: 3枚铜钱结果，1=正面，0=反面
        
        返回：
            爻的信息，包含类型、是否变爻等（使用 camelCase 以匹配前端）
        """
        heads = sum(coins)  # 正面数量
        
        if heads == 3:
            # 老阳：3正0反，阳爻且为变爻
            return {
                "value": 1,
                "type": "old_yang",
                "name": "老阳",
                "symbol": "⚊",
                "number": 9,
                "changing": True,
                "changedValue": 0  # camelCase
            }
        elif heads == 2:
            # 少阳：2正1反，阳爻
            return {
                "value": 1,
                "type": "young_yang",
                "name": "少阳",
                "symbol": "⚊",
                "number": 7,
                "changing": False,
                "changedValue": 1  # camelCase
            }
        elif heads == 1:
            # 少阴：1正2反，阴爻
            return {
                "value": 0,
                "type": "young_yin",
                "name": "少阴",
                "symbol": "⚋",
                "number": 8,
                "changing": False,
                "changedValue": 0  # camelCase
            }
        else:
            # 老阴：0正3反，阴爻且为变爻
            return {
                "value": 0,
                "type": "old_yin",
                "name": "老阴",
                "symbol": "⚋",
                "number": 6,
                "changing": True,
                "changedValue": 1  # camelCase
            }
    
    def get_trigram(self, lines: tuple) -> Dict:
        """根据三爻获取八卦信息"""
        trigram = self.TRIGRAMS.get(lines)
        if trigram:
            return trigram
        return {"name": "未知", "symbol": "?", "nature": "未知", "attribute": "未知"}
    
    def get_hexagram(self, upper_trigram_name: str, lower_trigram_name: str) -> Dict:
        """根据上下卦获取六十四卦信息"""
        key = (upper_trigram_name, lower_trigram_name)
        hexagram = self.HEXAGRAMS.get(key)
        
        if hexagram:
            return hexagram.copy()
        
        # 如果没找到，返回默认值
        return {
            "name": f"{upper_trigram_name}{lower_trigram_name}卦",
            "number": 0,
            "judgment": "卦辞待查"
        }
    
    def calculate_hexagram(self, coin_results: List[List[int]]) -> Dict:
        """
        根据6次掷铜钱结果计算完整卦象
        
        参数：
            coin_results: 6次掷铜钱结果
        
        返回：
            卦象信息，包含本卦、变卦（如有）、六爻详情（使用 camelCase 以匹配前端）
        """
        # 计算六爻
        lines = []
        has_changing = False
        
        for i, coins in enumerate(coin_results):
            line = self.calculate_line(coins)
            line["position"] = i + 1
            line["positionName"] = self.LINE_NAMES[i]  # camelCase
            lines.append(line)
            
            if line["changing"]:
                has_changing = True
        
        # 提取爻值（从下到上）
        original_values = tuple(line["value"] for line in lines)
        
        # 计算下卦（内卦）和上卦（外卦）
        # 下卦：初爻、二爻、三爻
        # 上卦：四爻、五爻、上爻
        lower_lines = original_values[:3]
        upper_lines = original_values[3:]
        
        lower_trigram = self.get_trigram(lower_lines)
        upper_trigram = self.get_trigram(upper_lines)
        
        # 获取本卦（使用 camelCase）
        original_hexagram = self.get_hexagram(upper_trigram["name"], lower_trigram["name"])
        original_hexagram["lowerTrigram"] = lower_trigram  # camelCase
        original_hexagram["upperTrigram"] = upper_trigram  # camelCase
        original_hexagram["lines"] = list(original_values)
        
        result = {
            "original_hexagram": original_hexagram,
            "lines": lines,
            "has_changing": has_changing
        }
        
        # 如果有变爻，计算变卦
        if has_changing:
            changed_values = tuple(line["changedValue"] for line in lines)  # camelCase
            changed_lower_lines = changed_values[:3]
            changed_upper_lines = changed_values[3:]
            
            changed_lower_trigram = self.get_trigram(changed_lower_lines)
            changed_upper_trigram = self.get_trigram(changed_upper_lines)
            
            changed_hexagram = self.get_hexagram(changed_upper_trigram["name"], changed_lower_trigram["name"])
            changed_hexagram["lowerTrigram"] = changed_lower_trigram  # camelCase
            changed_hexagram["upperTrigram"] = changed_upper_trigram  # camelCase
            changed_hexagram["lines"] = list(changed_values)
            
            result["changed_hexagram"] = changed_hexagram
        
        return result
