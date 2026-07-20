"""
彩票预测核心逻辑 - 基于真实历史数据的统计分析
支持：体彩大乐透 & 福彩双色球
"""

import random
from collections import Counter
from datetime import datetime


# ==================== 号码池定义 ====================
LOTTERY_CONFIG = {
    "大乐透": {
        "front_range": (1, 35),
        "back_range": (1, 12),
        "front_count": 5,
        "back_count": 2,
        "draw_days": "每周一、三、六 20:30",
    },
    "双色球": {
        "front_range": (1, 33),
        "back_range": (1, 16),
        "front_count": 6,
        "back_count": 1,
        "draw_days": "每周二、四、日 21:15",
    },
}


# ==================== 真实历史开奖数据（2026年） ====================
# 数据来源：500彩票网、中国福彩官网（自动抓取）
REAL_HISTORY = {
    "大乐透": [
        # 2026年真实开奖数据（更新于 2026-07-21）
        {"issue": "081", "front": [8, 16, 18, 24, 34], "back": [9, 12]},
        {"issue": "080", "front": [5, 10, 15, 21, 23], "back": [7, 8]},
        {"issue": "079", "front": [6, 8, 23, 26, 27], "back": [5, 12]},
        {"issue": "078", "front": [2, 13, 20, 25, 32], "back": [8, 11]},
        {"issue": "077", "front": [4, 14, 19, 24, 27], "back": [6, 7]},
        {"issue": "076", "front": [15, 20, 27, 28, 35], "back": [2, 11]},
        {"issue": "075", "front": [1, 6, 16, 18, 26], "back": [4, 10]},
        {"issue": "074", "front": [1, 4, 10, 23, 25], "back": [1, 12]},
        {"issue": "073", "front": [4, 10, 22, 23, 33], "back": [2, 12]},
        {"issue": "072", "front": [1, 13, 26, 29, 30], "back": [9, 11]},
        {"issue": "071", "front": [5, 13, 22, 26, 32], "back": [2, 3]},
        {"issue": "070", "front": [4, 5, 15, 21, 32], "back": [2, 11]},
        {"issue": "069", "front": [12, 19, 21, 24, 29], "back": [3, 10]},
        {"issue": "068", "front": [3, 11, 12, 21, 22], "back": [6, 10]},
        {"issue": "067", "front": [6, 16, 18, 19, 28], "back": [7, 11]},
        {"issue": "066", "front": [10, 13, 19, 21, 30], "back": [4, 5]},
        {"issue": "065", "front": [4, 11, 12, 13, 25], "back": [4, 8]},
        {"issue": "064", "front": [3, 13, 15, 17, 21], "back": [2, 7]},
        {"issue": "063", "front": [3, 15, 20, 29, 31], "back": [1, 12]},
        {"issue": "062", "front": [7, 15, 20, 24, 29], "back": [4, 10]},
        {"issue": "061", "front": [10, 12, 26, 31, 35], "back": [2, 12]},
        {"issue": "060", "front": [22, 28, 30, 31, 34], "back": [1, 5]},
        {"issue": "059", "front": [6, 13, 17, 19, 26], "back": [7, 8]},
        {"issue": "058", "front": [7, 12, 13, 18, 34], "back": [1, 5]},
        {"issue": "057", "front": [23, 25, 26, 27, 34], "back": [4, 10]},
        {"issue": "056", "front": [6, 7, 18, 21, 30], "back": [1, 5]},
        {"issue": "055", "front": [9, 10, 20, 33, 35], "back": [4, 11]},
        {"issue": "054", "front": [2, 6, 14, 22, 24], "back": [8, 11]},
        {"issue": "053", "front": [2, 9, 14, 20, 31], "back": [5, 9]},
        {"issue": "052", "front": [2, 3, 20, 28, 33], "back": [2, 12]},
        {"issue": "051", "front": [13, 18, 28, 32, 33], "back": [2, 11]},
        {"issue": "050", "front": [6, 10, 14, 23, 33], "back": [8, 10]},
        {"issue": "049", "front": [1, 6, 14, 15, 17], "back": [2, 3]},
        {"issue": "048", "front": [11, 17, 20, 23, 35], "back": [1, 10]},
        {"issue": "047", "front": [9, 20, 21, 23, 28], "back": [6, 11]},
        {"issue": "046", "front": [1, 13, 18, 27, 33], "back": [4, 7]},
        {"issue": "045", "front": [1, 15, 21, 26, 33], "back": [4, 7]},
        {"issue": "044", "front": [3, 8, 22, 26, 29], "back": [7, 10]},
        {"issue": "043", "front": [8, 12, 14, 19, 22], "back": [11, 12]},
        {"issue": "042", "front": [2, 7, 13, 19, 24], "back": [3, 8]},
        {"issue": "041", "front": [24, 25, 27, 29, 34], "back": [2, 6]},
        {"issue": "040", "front": [6, 12, 13, 21, 34], "back": [8, 9]},
        {"issue": "039", "front": [9, 11, 20, 26, 27], "back": [6, 9]},
        {"issue": "038", "front": [8, 17, 21, 33, 35], "back": [6, 7]},
        {"issue": "037", "front": [7, 12, 13, 28, 32], "back": [6, 8]},
        {"issue": "036", "front": [4, 7, 16, 26, 32], "back": [5, 8]},
        {"issue": "035", "front": [2, 22, 30, 33, 34], "back": [8, 12]},
        {"issue": "034", "front": [11, 12, 25, 26, 27], "back": [8, 11]},
        {"issue": "033", "front": [3, 5, 7, 9, 18], "back": [2, 10]},
        {"issue": "032", "front": [3, 4, 19, 26, 32], "back": [1, 12]},
        {"issue": "031", "front": [6, 8, 22, 29, 34], "back": [5, 7]},
        {"issue": "030", "front": [2, 13, 22, 28, 34], "back": [5, 12]},
        {"issue": "029", "front": [3, 5, 17, 33, 35], "back": [5, 7]},
        {"issue": "028", "front": [15, 27, 29, 30, 34], "back": [1, 10]},
        {"issue": "027", "front": [9, 10, 11, 12, 16], "back": [1, 11]},
        {"issue": "026", "front": [10, 11, 22, 26, 32], "back": [1, 8]},
        {"issue": "025", "front": [3, 15, 24, 28, 29], "back": [3, 7]},
        {"issue": "024", "front": [2, 4, 8, 10, 21], "back": [9, 12]},
        {"issue": "023", "front": [9, 25, 26, 27, 28], "back": [1, 8]},
        {"issue": "022", "front": [5, 9, 10, 18, 26], "back": [5, 6]},
        {"issue": "021", "front": [5, 8, 12, 14, 17], "back": [4, 5]},
        {"issue": "020", "front": [1, 10, 21, 23, 29], "back": [10, 12]},
        {"issue": "019", "front": [12, 13, 14, 16, 31], "back": [4, 12]},
        {"issue": "018", "front": [9, 11, 19, 30, 35], "back": [1, 12]},
        {"issue": "017", "front": [4, 5, 10, 23, 31], "back": [7, 12]},
        {"issue": "016", "front": [8, 9, 12, 19, 24], "back": [1, 6]},
        {"issue": "015", "front": [1, 4, 10, 13, 17], "back": [3, 11]},
        {"issue": "014", "front": [16, 18, 23, 34, 35], "back": [1, 6]},
        {"issue": "013", "front": [3, 5, 6, 23, 26], "back": [1, 4]},
        {"issue": "012", "front": [1, 2, 9, 22, 25], "back": [1, 6]},
        {"issue": "011", "front": [14, 21, 23, 29, 33], "back": [2, 10]},
        {"issue": "010", "front": [2, 3, 13, 18, 26], "back": [2, 9]},
        {"issue": "009", "front": [5, 12, 13, 14, 33], "back": [5, 8]},
        {"issue": "008", "front": [3, 6, 17, 21, 33], "back": [5, 11]},
        {"issue": "007", "front": [1, 3, 13, 20, 26], "back": [3, 10]},
        {"issue": "006", "front": [5, 12, 18, 23, 35], "back": [6, 12]},
        {"issue": "005", "front": [2, 4, 16, 23, 35], "back": [6, 11]},
        {"issue": "004", "front": [5, 18, 23, 25, 32], "back": [5, 9]},
        {"issue": "003", "front": [2, 9, 11, 15, 16], "back": [2, 4]},
        {"issue": "002", "front": [4, 8, 15, 20, 31], "back": [7, 8]},
        {"issue": "001", "front": [7, 9, 23, 27, 32], "back": [2, 8]},
    ],

    "双色球": [
        # 2026年真实开奖数据（更新于 2026-07-21）
        {"issue": "082", "front": [5, 7, 10, 14, 21, 28], "back": [4]},
        {"issue": "081", "front": [6, 10, 12, 15, 24, 27], "back": [12]},
        {"issue": "080", "front": [4, 5, 11, 19, 27, 32], "back": [1]},
        {"issue": "079", "front": [1, 11, 17, 22, 24, 29], "back": [4]},
        {"issue": "078", "front": [7, 11, 14, 16, 27, 28], "back": [6]},
        {"issue": "077", "front": [1, 4, 5, 14, 18, 25], "back": [4]},
        {"issue": "076", "front": [1, 3, 19, 20, 24, 25], "back": [7]},
        {"issue": "075", "front": [8, 12, 18, 21, 24, 30], "back": [1]},
        {"issue": "074", "front": [2, 23, 24, 26, 28, 32], "back": [4]},
        {"issue": "073", "front": [9, 10, 13, 16, 19, 21], "back": [8]},
        {"issue": "072", "front": [7, 8, 12, 15, 17, 21], "back": [1]},
        {"issue": "071", "front": [3, 8, 19, 25, 31, 33], "back": [5]},
        {"issue": "070", "front": [3, 6, 8, 14, 26, 27], "back": [8]},
        {"issue": "069", "front": [12, 14, 16, 17, 18, 32], "back": [8]},
        {"issue": "068", "front": [3, 5, 16, 18, 29, 32], "back": [4]},
        {"issue": "067", "front": [4, 19, 27, 29, 30, 32], "back": [13]},
        {"issue": "066", "front": [5, 11, 21, 23, 24, 29], "back": [16]},
        {"issue": "065", "front": [7, 8, 16, 24, 30, 32], "back": [2]},
        {"issue": "064", "front": [1, 9, 15, 18, 29, 33], "back": [15]},
        {"issue": "063", "front": [2, 8, 25, 28, 30, 31], "back": [2]},
        {"issue": "062", "front": [2, 4, 7, 14, 28, 29], "back": [9]},
        {"issue": "061", "front": [1, 4, 5, 15, 23, 28], "back": [7]},
        {"issue": "060", "front": [7, 9, 10, 16, 22, 27], "back": [11]},
        {"issue": "059", "front": [8, 16, 26, 28, 29, 30], "back": [15]},
        {"issue": "058", "front": [1, 4, 7, 21, 29, 30], "back": [1]},
        {"issue": "057", "front": [1, 10, 22, 24, 28, 30], "back": [7]},
        {"issue": "056", "front": [10, 19, 21, 22, 31, 33], "back": [5]},
        {"issue": "055", "front": [4, 11, 24, 25, 32, 33], "back": [13]},
        {"issue": "054", "front": [13, 20, 25, 29, 30, 33], "back": [2]},
        {"issue": "053", "front": [1, 2, 3, 8, 13, 14], "back": [2]},
        {"issue": "052", "front": [1, 3, 11, 22, 26, 31], "back": [11]},
        {"issue": "051", "front": [9, 14, 15, 16, 29, 30], "back": [10]},
        {"issue": "050", "front": [6, 9, 25, 27, 28, 30], "back": [3]},
        {"issue": "049", "front": [3, 4, 14, 15, 18, 20], "back": [2]},
        {"issue": "048", "front": [9, 15, 18, 24, 28, 33], "back": [1]},
        {"issue": "047", "front": [7, 16, 21, 24, 27, 30], "back": [7]},
        {"issue": "046", "front": [2, 9, 10, 24, 31, 33], "back": [16]},
        {"issue": "045", "front": [4, 11, 15, 17, 24, 30], "back": [15]},
        {"issue": "044", "front": [2, 14, 17, 18, 22, 30], "back": [1]},
        {"issue": "043", "front": [6, 9, 14, 16, 25, 32], "back": [16]},
        {"issue": "042", "front": [2, 7, 12, 19, 24, 31], "back": [10]},
        {"issue": "041", "front": [2, 8, 10, 17, 19, 24], "back": [13]},
        {"issue": "040", "front": [3, 4, 14, 22, 23, 33], "back": [4]},
        {"issue": "039", "front": [8, 17, 18, 21, 25, 30], "back": [5]},
        {"issue": "038", "front": [1, 2, 13, 23, 25, 27], "back": [5]},
        {"issue": "037", "front": [11, 22, 27, 29, 31, 33], "back": [12]},
        {"issue": "036", "front": [6, 10, 12, 15, 22, 28], "back": [8]},
        {"issue": "035", "front": [2, 6, 12, 24, 25, 32], "back": [2]},
        {"issue": "034", "front": [1, 3, 7, 13, 22, 23], "back": [7]},
        {"issue": "033", "front": [3, 6, 13, 21, 28, 29], "back": [6]},
        {"issue": "032", "front": [1, 3, 11, 18, 31, 33], "back": [2]},
        {"issue": "031", "front": [3, 10, 12, 13, 18, 33], "back": [8]},
        {"issue": "030", "front": [10, 11, 14, 19, 22, 24], "back": [4]},
        {"issue": "029", "front": [6, 19, 22, 23, 28, 31], "back": [5]},
        {"issue": "028", "front": [2, 6, 9, 17, 25, 28], "back": [15]},
        {"issue": "027", "front": [2, 13, 17, 18, 25, 26], "back": [13]},
        {"issue": "026", "front": [2, 9, 16, 22, 25, 29], "back": [3]},
        {"issue": "025", "front": [2, 3, 15, 20, 23, 24], "back": [10]},
        {"issue": "024", "front": [1, 2, 13, 21, 23, 29], "back": [14]},
        {"issue": "023", "front": [1, 3, 8, 10, 23, 29], "back": [6]},
        {"issue": "022", "front": [15, 18, 23, 25, 28, 32], "back": [11]},
        {"issue": "021", "front": [3, 13, 25, 26, 30, 31], "back": [4]},
        {"issue": "020", "front": [1, 13, 14, 21, 24, 30], "back": [2]},
        {"issue": "019", "front": [7, 8, 16, 17, 18, 30], "back": [1]},
        {"issue": "018", "front": [11, 15, 17, 22, 25, 30], "back": [7]},
        {"issue": "017", "front": [1, 3, 5, 18, 29, 32], "back": [4]},
        {"issue": "016", "front": [4, 5, 9, 10, 27, 30], "back": [13]},
        {"issue": "015", "front": [7, 10, 13, 22, 27, 31], "back": [12]},
        {"issue": "014", "front": [7, 13, 19, 22, 26, 32], "back": [1]},
        {"issue": "013", "front": [4, 9, 12, 13, 16, 20], "back": [1]},
        {"issue": "012", "front": [3, 5, 7, 16, 20, 24], "back": [8]},
        {"issue": "011", "front": [2, 3, 4, 20, 31, 32], "back": [4]},
        {"issue": "010", "front": [4, 9, 10, 15, 19, 26], "back": [12]},
        {"issue": "009", "front": [3, 6, 13, 19, 23, 25], "back": [10]},
        {"issue": "008", "front": [6, 9, 16, 27, 31, 33], "back": [10]},
        {"issue": "007", "front": [9, 13, 19, 27, 29, 30], "back": [1]},
        {"issue": "006", "front": [2, 6, 22, 23, 24, 28], "back": [15]},
        {"issue": "005", "front": [1, 20, 22, 27, 30, 33], "back": [10]},
        {"issue": "004", "front": [3, 7, 8, 9, 18, 32], "back": [10]},
        {"issue": "003", "front": [5, 6, 9, 21, 28, 30], "back": [16]},
        {"issue": "002", "front": [1, 5, 7, 18, 30, 32], "back": [2]},
        {"issue": "001", "front": [2, 6, 11, 12, 13, 33], "back": [15]},
    ],

}


# ==================== 频率分析 ====================
def frequency_analysis(history: list):
    """统计号码出现频率"""
    front_counter = Counter()
    back_counter = Counter()
    for draw in history:
        front_counter.update(draw["front"])
        back_counter.update(draw["back"])
    return front_counter, back_counter


# ==================== 遗漏分析 ====================
def omission_analysis(history: list, lottery_type: str):
    """计算每个号码距上次出现的期数"""
    config = LOTTERY_CONFIG[lottery_type]
    fr, br = config["front_range"], config["back_range"]

    front_omission = {}
    back_omission = {}

    for num in range(fr[0], fr[1] + 1):
        for i, draw in enumerate(history):
            if num in draw["front"]:
                front_omission[num] = i
                break
        else:
            front_omission[num] = len(history)

    for num in range(br[0], br[1] + 1):
        for i, draw in enumerate(history):
            if num in draw["back"]:
                back_omission[num] = i
                break
        else:
            back_omission[num] = len(history)

    return front_omission, back_omission


# ==================== 和值分析 ====================
def sum_analysis(history: list):
    """分析号码和值分布"""
    front_sums = [sum(d["front"]) for d in history]
    back_sums = [sum(d["back"]) for d in history]
    return {
        "front_avg": sum(front_sums) / len(front_sums),
        "front_min": min(front_sums),
        "front_max": max(front_sums),
        "back_avg": sum(back_sums) / len(back_sums),
        "back_min": min(back_sums),
        "back_max": max(back_sums),
    }


# ==================== 跨度分析 ====================
def span_analysis(history: list):
    """分析号码跨度（最大号-最小号）"""
    front_spans = [max(d["front"]) - min(d["front"]) for d in history]
    back_spans = [max(d["back"]) - min(d["back"]) for d in history] if len(history[0]["back"]) > 1 else [0] * len(history)
    return {
        "front_avg": sum(front_spans) / len(front_spans),
        "back_avg": sum(back_spans) / len(back_spans),
    }


# ==================== 区间分析 ====================
def zone_analysis(history: list, lottery_type: str):
    """分析号码在各区间的分布"""
    config = LOTTERY_CONFIG[lottery_type]
    fr = config["front_range"]
    fc = config["front_count"]

    # 将前区分为3个区间
    range_size = (fr[1] - fr[0] + 1) // 3
    zones = [
        (fr[0], fr[0] + range_size - 1),
        (fr[0] + range_size, fr[0] + 2 * range_size - 1),
        (fr[0] + 2 * range_size, fr[1]),
    ]

    zone_counts = []
    for draw in history:
        counts = [0, 0, 0]
        for num in draw["front"]:
            for i, (z_min, z_max) in enumerate(zones):
                if z_min <= num <= z_max:
                    counts[i] += 1
                    break
        zone_counts.append(counts)

    avg_counts = [0, 0, 0]
    for counts in zone_counts:
        for i in range(3):
            avg_counts[i] += counts[i]
    avg_counts = [c / len(history) for c in avg_counts]

    return {
        "zones": zones,
        "avg_counts": avg_counts,
    }


# ==================== 奇偶分析 ====================
def odd_even_analysis(history: list):
    """分析奇偶比例"""
    front_ratios = []
    for draw in history:
        odd_count = sum(1 for n in draw["front"] if n % 2 == 1)
        even_count = len(draw["front"]) - odd_count
        front_ratios.append((odd_count, even_count))

    avg_odd = sum(r[0] for r in front_ratios) / len(front_ratios)
    avg_even = sum(r[1] for r in front_ratios) / len(front_ratios)

    return {
        "avg_odd": avg_odd,
        "avg_even": avg_even,
    }


# ==================== 连号分析 ====================
def consecutive_analysis(history: list):
    """分析连号出现概率"""
    has_consecutive = 0
    for draw in history:
        front_sorted = sorted(draw["front"])
        for i in range(len(front_sorted) - 1):
            if front_sorted[i + 1] - front_sorted[i] == 1:
                has_consecutive += 1
                break

    return {
        "consecutive_rate": has_consecutive / len(history),
    }


# ==================== 预测方法 ====================

def predict_by_frequency(history: list, lottery_type: str) -> dict:
    """热门号码法 - 选择出现频率最高的号码"""
    config = LOTTERY_CONFIG[lottery_type]
    fc, bc = config["front_count"], config["back_count"]

    front_counter, back_counter = frequency_analysis(history)
    hot_front = [n for n, _ in front_counter.most_common(fc)]
    hot_back = [n for n, _ in back_counter.most_common(bc)]

    return {
        "front": sorted(hot_front[:fc]),
        "back": sorted(hot_back[:bc]),
        "method": "🔥 热门号码法",
        "desc": "基于历史数据，选择出现频率最高的号码",
    }


def predict_by_cold(history: list, lottery_type: str) -> dict:
    """冷门回补法 - 选择长期未出的号码"""
    config = LOTTERY_CONFIG[lottery_type]
    fc, bc = config["front_count"], config["back_count"]

    front_omission, back_omission = omission_analysis(history, lottery_type)
    cold_front = sorted(front_omission, key=front_omission.get, reverse=True)[:fc]
    cold_back = sorted(back_omission, key=back_omission.get, reverse=True)[:bc]

    return {
        "front": sorted(cold_front),
        "back": sorted(cold_back),
        "method": "❄️ 冷门回补法",
        "desc": "选择遗漏期数最长的号码，等待回补",
    }


def predict_by_weighted(history: list, lottery_type: str) -> dict:
    """加权随机法 - 基于频率加权随机选号"""
    config = LOTTERY_CONFIG[lottery_type]
    fr, br = config["front_range"], config["back_range"]
    fc, bc = config["front_count"], config["back_count"]

    front_counter, back_counter = frequency_analysis(history)

    front_nums = list(range(fr[0], fr[1] + 1))
    front_weights = [front_counter.get(n, 1) for n in front_nums]
    back_nums = list(range(br[0], br[1] + 1))
    back_weights = [back_counter.get(n, 1) for n in back_nums]

    selected_front = []
    nums_pool = front_nums.copy()
    weights_pool = front_weights.copy()
    for _ in range(fc):
        idx = random.choices(range(len(nums_pool)), weights=weights_pool, k=1)[0]
        selected_front.append(nums_pool.pop(idx))
        weights_pool.pop(idx)

    selected_back = []
    nums_pool = back_nums.copy()
    weights_pool = back_weights.copy()
    for _ in range(bc):
        idx = random.choices(range(len(nums_pool)), weights=weights_pool, k=1)[0]
        selected_back.append(nums_pool.pop(idx))
        weights_pool.pop(idx)

    return {
        "front": sorted(selected_front),
        "back": sorted(selected_back),
        "method": "📊 加权随机法",
        "desc": "根据历史频率进行加权随机，热门号概率更高",
    }


def predict_by_balanced(history: list, lottery_type: str) -> dict:
    """均衡分布法 - 综合奇偶、大小、区间平衡"""
    config = LOTTERY_CONFIG[lottery_type]
    fr, br = config["front_range"], config["back_range"]
    fc, bc = config["front_count"], config["back_count"]

    # 奇偶平衡
    front_odds = [n for n in range(fr[0], fr[1] + 1) if n % 2 == 1]
    front_evens = [n for n in range(fr[0], fr[1] + 1) if n % 2 == 0]

    odd_count = fc // 2 + random.randint(0, 1)
    even_count = fc - odd_count

    selected_front = sorted(
        random.sample(front_odds, min(odd_count, len(front_odds))) +
        random.sample(front_evens, min(even_count, len(front_evens)))
    )[:fc]

    back_all = list(range(br[0], br[1] + 1))
    selected_back = sorted(random.sample(back_all, bc))

    return {
        "front": selected_front,
        "back": selected_back,
        "method": "⚖️ 均衡分布法",
        "desc": "注重奇偶、大小号码的均衡分布",
    }


def predict_by_sum_span(history: list, lottery_type: str) -> dict:
    """和值跨度法 - 基于历史和值和跨度范围选号"""
    config = LOTTERY_CONFIG[lottery_type]
    fr, br = config["front_range"], config["back_range"]
    fc, bc = config["front_count"], config["back_count"]

    sum_stats = sum_analysis(history)
    span_stats = span_analysis(history)

    # 目标和值在平均值附近波动
    target_front_sum = int(sum_stats["front_avg"] + random.randint(-5, 5))
    target_back_sum = int(sum_stats["back_avg"] + random.randint(-2, 2))

    # 尝试生成符合和值范围的号码组合
    for _ in range(100):
        front = sorted(random.sample(range(fr[0], fr[1] + 1), fc))
        if abs(sum(front) - target_front_sum) <= 10:
            break

    for _ in range(100):
        back = sorted(random.sample(range(br[0], br[1] + 1), bc))
        if abs(sum(back) - target_back_sum) <= 5:
            break

    return {
        "front": front,
        "back": back,
        "method": "📈 和值跨度法",
        "desc": f"目标和值：前区{target_front_sum} 后区{target_back_sum}",
    }


def predict_by_zone(history: list, lottery_type: str) -> dict:
    """区间分布法 - 保证号码在各区间均匀分布"""
    config = LOTTERY_CONFIG[lottery_type]
    fr, br = config["front_range"], config["back_range"]
    fc, bc = config["front_count"], config["back_count"]

    zone_stats = zone_analysis(history, lottery_type)
    zones = zone_stats["zones"]

    selected_front = []
    for i, (z_min, z_max) in enumerate(zones):
        zone_nums = list(range(z_min, z_max + 1))
        # 每个区间选1-2个
        count = 2 if i == 1 else random.randint(1, 2)
        count = min(count, len(zone_nums), fc - len(selected_front))
        selected_front.extend(random.sample(zone_nums, count))

    # 如果不够，从中间区间补充
    while len(selected_front) < fc:
        mid_zone = zones[1]
        remaining = [n for n in range(mid_zone[0], mid_zone[1] + 1) if n not in selected_front]
        if remaining:
            selected_front.append(random.choice(remaining))
        else:
            selected_front.append(random.randint(fr[0], fr[1]))

    selected_front = sorted(selected_front[:fc])
    back_all = list(range(br[0], br[1] + 1))
    selected_back = sorted(random.sample(back_all, bc))

    return {
        "front": selected_front,
        "back": selected_back,
        "method": "🎯 区间分布法",
        "desc": "保证号码在前区各区间均匀分布",
    }


def predict_by_consecutive(history: list, lottery_type: str) -> dict:
    """连号分析法 - 根据连号出现概率选号"""
    config = LOTTERY_CONFIG[lottery_type]
    fr, br = config["front_range"], config["back_range"]
    fc, bc = config["front_count"], config["back_count"]

    consec_stats = consecutive_analysis(history)
    should_have_consec = random.random() < consec_stats["consecutive_rate"]

    for _ in range(100):
        front = sorted(random.sample(range(fr[0], fr[1] + 1), fc))
        has_consec = any(front[i+1] - front[i] == 1 for i in range(len(front)-1))
        if has_consec == should_have_consec:
            break

    back_all = list(range(br[0], br[1] + 1))
    selected_back = sorted(random.sample(back_all, bc))

    return {
        "front": front,
        "back": selected_back,
        "method": "🔗 连号分析法",
        "desc": f"基于历史连号概率{'含' if should_have_consec else '不含'}连号",
    }


def predict_by_combined(history: list, lottery_type: str) -> dict:
    """综合推荐法 - 多维度综合分析"""
    config = LOTTERY_CONFIG[lottery_type]
    fr, br = config["front_range"], config["back_range"]
    fc, bc = config["front_count"], config["back_count"]

    # 获取各维度分析结果
    front_counter, back_counter = frequency_analysis(history)
    front_omission, back_omission = omission_analysis(history, lottery_type)
    odd_even = odd_even_analysis(history)
    sum_stats = sum_analysis(history)

    # 为每个号码计算综合得分
    front_scores = {}
    for num in range(fr[0], fr[1] + 1):
        score = 0
        # 频率得分（热门号加分）
        freq = front_counter.get(num, 0)
        score += freq * 0.3
        # 遗漏得分（遗漏久的加分）
        omission = front_omission.get(num, 0)
        score += omission * 0.2
        # 奇偶平衡（当前偏向哪边就选另一边）
        avg_odd = odd_even["avg_odd"]
        if num % 2 == 1 and avg_odd < fc / 2:
            score += 2
        elif num % 2 == 0 and avg_odd > fc / 2:
            score += 2
        front_scores[num] = score

    # 选取得分最高的号码
    sorted_front = sorted(front_scores, key=front_scores.get, reverse=True)
    selected_front = sorted(sorted_front[:fc])

    # 后区同样逻辑
    back_scores = {}
    for num in range(br[0], br[1] + 1):
        score = 0
        freq = back_counter.get(num, 0)
        score += freq * 0.3
        omission = back_omission.get(num, 0)
        score += omission * 0.2
        back_scores[num] = score

    sorted_back = sorted(back_scores, key=back_scores.get, reverse=True)
    selected_back = sorted(sorted_back[:bc])

    return {
        "front": selected_front,
        "back": selected_back,
        "method": "🌟 综合推荐法",
        "desc": "综合频率、遗漏、奇偶、和值等多维度分析",
    }


# ==================== 主预测函数 ====================
PREDICT_METHODS = [
    predict_by_frequency,
    predict_by_cold,
    predict_by_weighted,
    predict_by_balanced,
    predict_by_sum_span,
    predict_by_zone,
    predict_by_consecutive,
    predict_by_combined,
]

METHOD_NAMES = [
    "🔥 热门号码法",
    "❄️ 冷门回补法",
    "📊 加权随机法",
    "⚖️ 均衡分布法",
    "📈 和值跨度法",
    "🎯 区间分布法",
    "🔗 连号分析法",
    "🌟 综合推荐法",
]


def generate_prediction(lottery_type: str, method_index: int = None) -> dict:
    """生成一组预测号码"""
    history = REAL_HISTORY[lottery_type]

    if method_index is not None:
        return PREDICT_METHODS[method_index](history, lottery_type)
    return random.choice(PREDICT_METHODS)(history, lottery_type)


def generate_multiple(lottery_type: str, count: int = 5) -> list:
    """生成多组预测号码"""
    history = REAL_HISTORY[lottery_type]
    results = []
    used_methods = set()

    for _ in range(count):
        # 尽量使用不同方法
        available = [i for i in range(len(PREDICT_METHODS)) if i not in used_methods]
        if not available:
            available = list(range(len(PREDICT_METHODS)))
            used_methods.clear()

        method_idx = random.choice(available)
        used_methods.add(method_idx)
        results.append(PREDICT_METHODS[method_idx](history, lottery_type))

    return results


def get_statistics(lottery_type: str) -> dict:
    """获取统计数据用于图表展示"""
    history = REAL_HISTORY[lottery_type]

    front_counter, back_counter = frequency_analysis(history)
    front_omission, back_omission = omission_analysis(history, lottery_type)
    sum_stats = sum_analysis(history)
    span_stats = span_analysis(history)
    odd_even = odd_even_analysis(history)
    consec_stats = consecutive_analysis(history)
    zone_stats = zone_analysis(history, lottery_type)

    # 最近10期开奖号码
    recent_draws = history[:10]

    return {
        "front_freq": dict(front_counter.most_common()),
        "back_freq": dict(back_counter.most_common()),
        "front_omission": front_omission,
        "back_omission": back_omission,
        "sum_stats": sum_stats,
        "span_stats": span_stats,
        "odd_even": odd_even,
        "consecutive_rate": consec_stats["consecutive_rate"],
        "zone_stats": zone_stats,
        "recent_draws": recent_draws,
        "total_periods": len(history),
    }


def get_hot_cold_numbers(lottery_type: str, top_n: int = 5) -> dict:
    """获取热门和冷门号码"""
    history = REAL_HISTORY[lottery_type]
    front_counter, back_counter = frequency_analysis(history)
    front_omission, back_omission = omission_analysis(history, lottery_type)

    hot_front = [n for n, _ in front_counter.most_common(top_n)]
    cold_front = sorted(front_omission, key=front_omission.get, reverse=True)[:top_n]

    hot_back = [n for n, _ in back_counter.most_common(top_n)]
    cold_back = sorted(back_omission, key=back_omission.get, reverse=True)[:top_n]

    return {
        "hot_front": sorted(hot_front),
        "cold_front": sorted(cold_front),
        "hot_back": sorted(hot_back),
        "cold_back": sorted(cold_back),
    }
