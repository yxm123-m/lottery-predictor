"""彩票预测核心逻辑 - 基于统计学分析"""

import random
from collections import Counter


# ==================== 号码池定义 ====================
LOTTERY_CONFIG = {
    "大乐透": {
        "front_range": (1, 35),   # 前区 1-35 选5
        "back_range": (1, 12),    # 后区 1-12 选2
        "front_count": 5,
        "back_count": 2,
    },
    "双色球": {
        "front_range": (1, 33),   # 红球 1-33 选6
        "back_range": (1, 16),    # 蓝球 1-16 选1
        "front_count": 6,
        "back_count": 1,
    },
}


# ==================== 模拟历史数据 ====================
def generate_history(lottery_type: str, periods: int = 100):
    """生成模拟历史开奖数据用于统计分析"""
    config = LOTTERY_CONFIG[lottery_type]
    fr, br = config["front_range"], config["back_range"]
    fc, bc = config["front_count"], config["back_count"]

    history = []
    for i in range(periods):
        front = sorted(random.sample(range(fr[0], fr[1] + 1), fc))
        back = sorted(random.sample(range(br[0], br[1] + 1), bc))
        history.append({"front": front, "back": back})
    return history


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
        for i, draw in enumerate(reversed(history)):
            if num in draw["front"]:
                front_omission[num] = i
                break
        else:
            front_omission[num] = len(history)

    for num in range(br[0], br[1] + 1):
        for i, draw in enumerate(reversed(history)):
            if num in draw["back"]:
                back_omission[num] = i
                break
        else:
            back_omission[num] = len(history)

    return front_omission, back_omission


# ==================== 预测方法 ====================

def predict_by_frequency(history: list, lottery_type: str) -> dict:
    """基于频率的预测 - 选热门号码"""
    config = LOTTERY_CONFIG[lottery_type]
    fc, bc = config["front_count"], config["back_count"]

    front_counter, back_counter = frequency_analysis(history)
    # 按频率从高到低排序，取前N个
    hot_front = [n for n, _ in front_counter.most_common(fc)]
    hot_back = [n for n, _ in back_counter.most_common(bc)]

    return {
        "front": sorted(hot_front[:fc]),
        "back": sorted(hot_back[:bc]),
        "method": "🔥 热门号码法",
        "desc": "选择历史上出现频率最高的号码",
    }


def predict_by_cold(history: list, lottery_type: str) -> dict:
    """基于冷门的预测 - 选长期未出号码"""
    config = LOTTERY_CONFIG[lottery_type]
    fc, bc = config["front_count"], config["back_count"]

    front_omission, back_omission = omission_analysis(history, lottery_type)
    # 按遗漏期数从大到小排序
    cold_front = sorted(front_omission, key=front_omission.get, reverse=True)[:fc]
    cold_back = sorted(back_omission, key=back_omission.get, reverse=True)[:bc]

    return {
        "front": sorted(cold_front),
        "back": sorted(cold_back),
        "method": "❄️ 冷门回补法",
        "desc": "选择长期未出现的号码（遗漏回补）",
    }


def predict_by_weighted(history: list, lottery_type: str) -> dict:
    """加权随机预测 - 基于历史频率的加权随机"""
    config = LOTTERY_CONFIG[lottery_type]
    fr, br = config["front_range"], config["back_range"]
    fc, bc = config["front_count"], config["back_count"]

    front_counter, back_counter = frequency_analysis(history)

    # 构建加权列表
    front_nums = list(range(fr[0], fr[1] + 1))
    front_weights = [front_counter.get(n, 1) for n in front_nums]
    back_nums = list(range(br[0], br[1] + 1))
    back_weights = [back_counter.get(n, 1) for n in back_nums]

    # 加权随机抽取
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
        "desc": "根据历史频率加权随机选号",
    }


def predict_by_pattern(history: list, lottery_type: str) -> dict:
    """奇偶大小平衡预测"""
    config = LOTTERY_CONFIG[lottery_type]
    fr, br = config["front_range"], config["back_range"]
    fc, bc = config["front_count"], config["back_count"]

    front_mid = (fr[0] + fr[1]) / 2
    back_mid = (br[0] + br[1]) / 2

    # 尝试奇偶平衡
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
        "method": "⚖️ 奇偶平衡法",
        "desc": "注重奇偶、大小号码的均衡分布",
    }


# ==================== 主预测函数 ====================
PREDICT_METHODS = [
    predict_by_frequency,
    predict_by_cold,
    predict_by_weighted,
    predict_by_pattern,
]


def generate_prediction(lottery_type: str, method_index: int = None) -> dict:
    """生成一组预测号码"""
    history = generate_history(lottery_type, periods=100)

    if method_index is not None:
        return PREDICT_METHODS[method_index](history, lottery_type)
    # 默认随机选一种方法
    return random.choice(PREDICT_METHODS)(history, lottery_type)


def generate_multiple(lottery_type: str, count: int = 5) -> list:
    """生成多组预测号码"""
    history = generate_history(lottery_type, periods=100)
    results = []
    for _ in range(count):
        method = random.choice(PREDICT_METHODS)
        results.append(method(history, lottery_type))
    return results


def get_statistics(lottery_type: str) -> dict:
    """获取统计数据用于图表展示"""
    history = generate_history(lottery_type, periods=200)
    front_counter, back_counter = frequency_analysis(history)

    front_omission, back_omission = omission_analysis(history, lottery_type)

    return {
        "front_freq": dict(front_counter.most_common()),
        "back_freq": dict(back_counter.most_common()),
        "front_omission": front_omission,
        "back_omission": back_omission,
    }
