"""
彩票预测助手 - 体彩大乐透 & 福彩双色球
⚠️ 纯娱乐用途，彩票开奖为随机事件，请理性购彩！
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from lottery_logic import (
    LOTTERY_CONFIG,
    generate_prediction,
    generate_multiple,
    get_statistics,
    PREDICT_METHODS,
)

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="🎱 彩票预测助手",
    page_icon="🎱",
    layout="centered",
)

# ==================== 样式 ====================
st.markdown("""
<style>
    .number-box {
        display: inline-block;
        width: 52px; height: 52px;
        line-height: 52px;
        text-align: center;
        border-radius: 50%;
        font-size: 22px; font-weight: bold;
        margin: 4px;
        color: white;
    }
    .front-num { background: linear-gradient(135deg, #e74c3c, #c0392b); }
    .back-num  { background: linear-gradient(135deg, #2980b9, #3498db); }
    .method-tag {
        display: inline-block;
        padding: 2px 12px;
        border-radius: 12px;
        font-size: 13px;
        background: #f0f0f0;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)


def render_numbers(front: list, back: list):
    """渲染号码球"""
    html = ""
    for n in front:
        html += f'<span class="number-box front-num">{n}</span>'
    html += '  '
    for n in back:
        html += f'<span class="number-box back-num">{n}</span>'
    st.markdown(html, unsafe_allow_html=True)


# ==================== 侧边栏 ====================
st.sidebar.title("🎱 彩票预测助手")
lottery_type = st.sidebar.radio("选择彩票类型", ["大乐透", "双色球"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 预测方法")
method_names = ["🔥 热门号码法", "❄️ 冷门回补法", "📊 加权随机法", "⚖️ 奇偶平衡法"]
selected_method = st.sidebar.radio(
    "选择算法",
    ["🎲 综合推荐"] + method_names,
    index=0,
)

st.sidebar.markdown("---")
num_groups = st.sidebar.slider("生成组数", 1, 10, 5)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### ⚠️ 免责声明
本应用仅供娱乐参考，所有预测基于统计分析，**不能提高中奖概率**。

彩票开奖为完全随机事件，请理性购彩，量力而行。
""")

# ==================== 主页面 ====================
config = LOTTERY_CONFIG[lottery_type]
st.title(f"🎱 {lottery_type}预测")
st.caption(f"前区选 {config['front_count']} 个（{config['front_range'][0]}-{config['front_range'][1]}） | "
           f"后区选 {config['back_count']} 个（{config['back_range'][0]}-{config['back_range'][1]}）")

st.markdown("---")

# ==================== 预测结果 ====================
st.subheader("🎯 今日预测")

if st.button("🔮 开始预测", type="primary", use_container_width=True):
    method_idx = None if selected_method == "🎲 综合推荐" else method_names.index(selected_method)

    with st.spinner("正在分析历史数据..."):
        results = []
        for _ in range(num_groups):
            if method_idx is not None:
                r = generate_prediction(lottery_type, method_idx)
            else:
                r = generate_prediction(lottery_type)
            results.append(r)

    for i, r in enumerate(results, 1):
        st.markdown(f"**第 {i} 组** `{r['method']}`")
        render_numbers(r["front"], r["back"])
        st.caption(r["desc"])
        st.markdown("")

# ==================== 统计分析 ====================
st.markdown("---")
st.subheader("📊 历史统计分析")

tab1, tab2 = st.tabs(["📈 号码频率", "⏳ 遗漏分析"])

with tab1:
    stats = get_statistics(lottery_type)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**前区/红球频率 TOP 15**")
        front_freq = stats["front_freq"]
        top_front = dict(sorted(front_freq.items(), key=lambda x: x[1], reverse=True)[:15])
        fig = px.bar(
            x=[str(k) for k in top_front.keys()],
            y=list(top_front.values()),
            labels={"x": "号码", "y": "出现次数"},
            color=list(top_front.values()),
            color_continuous_scale="Reds",
        )
        fig.update_layout(showlegend=False, height=350, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**后区/蓝球频率**")
        back_freq = stats["back_freq"]
        fig = px.bar(
            x=[str(k) for k in back_freq.keys()],
            y=list(back_freq.values()),
            labels={"x": "号码", "y": "出现次数"},
            color=list(back_freq.values()),
            color_continuous_scale="Blues",
        )
        fig.update_layout(showlegend=False, height=350, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    stats = get_statistics(lottery_type)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**前区/红球遗漏期数**")
        front_om = stats["front_omission"]
        fig = px.bar(
            x=[str(k) for k in front_om.keys()],
            y=list(front_om.values()),
            labels={"x": "号码", "y": "遗漏期数"},
            color=list(front_om.values()),
            color_continuous_scale="Oranges",
        )
        fig.update_layout(showlegend=False, height=350, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**后区/蓝球遗漏期数**")
        back_om = stats["back_omission"]
        fig = px.bar(
            x=[str(k) for k in back_om.keys()],
            y=list(back_om.values()),
            labels={"x": "号码", "y": "遗漏期数"},
            color=list(back_om.values()),
            color_continuous_scale="Purples",
        )
        fig.update_layout(showlegend=False, height=350, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

# ==================== 玩法说明 ====================
st.markdown("---")
with st.expander("📖 玩法说明"):
    if lottery_type == "大乐透":
        st.markdown("""
        ### 体彩大乐透
        - **前区**: 从 1-35 中选 5 个号码
        - **后区**: 从 1-12 中选 2 个号码
        - 每周一、三、六开奖
        - 一等奖：前区5个 + 后区2个全中
        """)
    else:
        st.markdown("""
        ### 福彩双色球
        - **红球**: 从 1-33 中选 6 个号码
        - **蓝球**: 从 1-16 中选 1 个号码
        - 每周二、四、日开奖
        - 一等奖：6个红球 + 1个蓝球全中
        """)

    st.markdown("""
    ### 预测方法说明
    | 方法 | 原理 |
    |------|------|
    | 🔥 热门号码法 | 选择历史上出现频率最高的号码 |
    | ❄️ 冷门回补法 | 选择长期未出现的号码 |
    | 📊 加权随机法 | 根据历史频率加权随机选号 |
    | ⚖️ 奇偶平衡法 | 注重奇偶、大小号码均衡分布 |
    """)

# ==================== 底部 ====================
st.markdown("---")
st.caption("🎱 彩票预测助手 | 纯娱乐参考，请理性购彩 | © 2024")
