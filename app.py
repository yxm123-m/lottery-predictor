"""
彩票预测助手 v2.0 - 基于真实历史数据的专业分析
支持：体彩大乐透 & 福彩双色球
⚠️ 纯娱乐用途，彩票开奖为随机事件，请理性购彩！
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from lottery_logic import (
    LOTTERY_CONFIG,
    generate_prediction,
    generate_multiple,
    get_statistics,
    get_hot_cold_numbers,
    PREDICT_METHODS,
    METHOD_NAMES,
)


# ==================== 页面配置 ====================
st.set_page_config(
    page_title="🎱 彩票预测助手 Pro",
    page_icon="🎱",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================== 自定义样式 ====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .number-box {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 50px; height: 50px;
        border-radius: 50%;
        font-size: 20px; font-weight: bold;
        margin: 3px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .front-num { background: linear-gradient(135deg, #e74c3c, #c0392b); }
    .back-num { background: linear-gradient(135deg, #2980b9, #3498db); }
    .hot-num { background: linear-gradient(135deg, #f39c12, #e67e22); }
    .cold-num { background: linear-gradient(135deg, #1abc9c, #16a085); }
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 8px 16px;
    }
</style>
""", unsafe_allow_html=True)


def render_numbers(front: list, back: list, prefix: str = ""):
    """渲染号码球"""
    html = '<div style="margin: 10px 0;">'
    for n in front:
        html += f'<span class="number-box front-num">{n}</span>'
    html += '<span style="margin: 0 10px; font-size: 24px;">|</span>'
    for n in back:
        html += f'<span class="number-box back-num">{n}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_hot_cold(hot: list, cold: list, label_hot: str, label_cold: str):
    """渲染热门和冷门号码"""
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{label_hot}**")
        html = '<div>'
        for n in hot:
            html += f'<span class="number-box hot-num">{n}</span>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
    with col2:
        st.markdown(f"**{label_cold}**")
        html = '<div>'
        for n in cold:
            html += f'<span class="number-box cold-num">{n}</span>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)


# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1>🎱 彩票预测助手</h1>
        <p style="color: #666;">Pro v2.0</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 彩票类型选择
    lottery_type = st.radio(
        "🎯 选择彩票类型",
        ["大乐透", "双色球"],
        format_func=lambda x: f"{'🔴' if x == '大乐透' else '🔵'} {x}",
    )

    st.markdown("---")

    # 预测方法选择
    st.markdown("### 🔮 预测算法")
    method_options = ["🎲 综合推荐"] + METHOD_NAMES
    selected_method = st.selectbox(
        "选择分析方法",
        method_options,
        index=0,
    )

    st.markdown("---")

    # 生成组数
    num_groups = st.slider("📊 生成组数", 1, 10, 5)

    st.markdown("---")

    # 免责声明
    st.markdown("""
    ### ⚠️ 免责声明
    本应用基于**真实历史数据**进行统计分析，仅供娱乐参考。

    彩票开奖为**完全随机事件**，任何分析方法都**不能提高中奖概率**。

    请理性购彩，量力而行！
    """)

    st.markdown("---")
    st.caption("基于2024-2025年真实开奖数据")


# ==================== 主页面 ====================
config = LOTTERY_CONFIG[lottery_type]

# 标题区
st.markdown(f"""
<div class="main-header">
    <h1>🎱 {lottery_type}预测分析系统</h1>
    <p>前区选 {config['front_count']} 个（{config['front_range'][0]}-{config['front_range'][1]}） | 后区选 {config['back_count']} 个（{config['back_range'][0]}-{config['back_range'][1]}） | {config['draw_days']}</p>
</div>
""", unsafe_allow_html=True)


# ==================== 数据概览 ====================
st.subheader("📊 数据概览")
stats = get_statistics(lottery_type)
hot_cold = get_hot_cold_numbers(lottery_type)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📈 分析期数", f"{stats['total_periods']} 期")
with col2:
    st.metric("📐 前区平均和值", f"{stats['sum_stats']['front_avg']:.1f}")
with col3:
    st.metric("📏 前区平均跨度", f"{stats['span_stats']['front_avg']:.1f}")
with col4:
    st.metric("🔗 连号出现率", f"{stats['consecutive_rate']*100:.1f}%")

st.markdown("")

# 热门冷门号码
st.markdown("### 🔥 热门 vs ❄️ 冷门号码")
render_hot_cold(
    hot_cold["hot_front"], hot_cold["cold_front"],
    "🔥 前区热门 TOP5", "❄️ 前区冷门 TOP5"
)
st.markdown("")
render_hot_cold(
    hot_cold["hot_back"], hot_cold["cold_back"],
    "🔥 后区热门 TOP5", "❄️ 后区冷门 TOP5"
)


# ==================== 预测结果 ====================
st.markdown("---")
st.subheader("🎯 智能预测")

col1, col2 = st.columns([3, 1])
with col2:
    predict_btn = st.button("🔮 开始预测", type="primary", use_container_width=True)

if predict_btn:
    method_idx = None if selected_method == "🎲 综合推荐" else METHOD_NAMES.index(selected_method)

    with st.spinner("正在基于历史数据进行多维度分析..."):
        results = []
        for _ in range(num_groups):
            if method_idx is not None:
                r = generate_prediction(lottery_type, method_idx)
            else:
                r = generate_prediction(lottery_type)
            results.append(r)

    st.markdown("### 预测结果")
    for i, r in enumerate(results, 1):
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"**第 {i} 组**")
                st.caption(r['method'])
            with col2:
                render_numbers(r["front"], r["back"])
                st.caption(r['desc'])
        st.markdown("")


# ==================== 详细统计分析 ====================
st.markdown("---")
st.subheader("📈 详细统计分析")

tab1, tab2, tab3, tab4 = st.tabs(["📊 号码频率", "⏳ 遗漏分析", "🎯 区间分布", "📋 最近开奖"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**前区{'红球' if lottery_type == '双色球' else ''}号码频率**")
        front_freq = stats["front_freq"]
        fig = px.bar(
            x=[str(k) for k in front_freq.keys()],
            y=list(front_freq.values()),
            labels={"x": "号码", "y": "出现次数"},
            color=list(front_freq.values()),
            color_continuous_scale="Reds",
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            margin=dict(t=10, b=10),
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"**后区{'蓝球' if lottery_type == '双色球' else ''}号码频率**")
        back_freq = stats["back_freq"]
        fig = px.bar(
            x=[str(k) for k in back_freq.keys()],
            y=list(back_freq.values()),
            labels={"x": "号码", "y": "出现次数"},
            color=list(back_freq.values()),
            color_continuous_scale="Blues",
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            margin=dict(t=10, b=10),
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, use_container_width=True)


with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**前区号码遗漏期数**")
        front_om = stats["front_omission"]
        fig = px.bar(
            x=[str(k) for k in front_om.keys()],
            y=list(front_om.values()),
            labels={"x": "号码", "y": "遗漏期数"},
            color=list(front_om.values()),
            color_continuous_scale="Oranges",
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            margin=dict(t=10, b=10),
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**后区号码遗漏期数**")
        back_om = stats["back_omission"]
        fig = px.bar(
            x=[str(k) for k in back_om.keys()],
            y=list(back_om.values()),
            labels={"x": "号码", "y": "遗漏期数"},
            color=list(back_om.values()),
            color_continuous_scale="Purples",
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            margin=dict(t=10, b=10),
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, use_container_width=True)

    # 遗漏分析提示
    st.info("💡 **遗漏分析提示**：遗漏期数越长的号码，理论上回补概率越高，但彩票开奖是随机的，仅供参考。")


with tab3:
    st.markdown("**前区区间分布（平均每个区间的号码数量）**")
    zone_stats = stats["zone_stats"]
    zones = zone_stats["zones"]
    avg_counts = zone_stats["avg_counts"]

    zone_labels = [f"第{i+1}区 ({z[0]}-{z[1]})" for i, z in enumerate(zones)]

    fig = go.Figure(data=[
        go.Bar(
            x=zone_labels,
            y=avg_counts,
            marker_color=['#e74c3c', '#f39c12', '#2ecc71'],
            text=[f"{c:.2f}" for c in avg_counts],
            textposition='auto',
        )
    ])
    fig.update_layout(
        showlegend=False,
        height=350,
        margin=dict(t=10, b=10),
        yaxis_title="平均号码数",
    )
    st.plotly_chart(fig, use_container_width=True)

    # 区间平衡建议
    balance_score = 100 - (max(avg_counts) - min(avg_counts)) * 50
    st.metric("📊 区间平衡指数", f"{balance_score:.1f}分")
    if balance_score < 70:
        st.warning("⚠️ 近期区间分布不太均匀，选号时注意各区间的平衡。")
    else:
        st.success("✅ 近期区间分布较为均匀。")


with tab4:
    st.markdown(f"**最近 10 期{lottery_type}开奖号码**")

    recent = stats["recent_draws"]
    for draw in recent:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"**第 {draw['issue']} 期**")
        with col2:
            render_numbers(draw["front"], draw["back"])
    st.markdown("")

    # 和值统计
    st.markdown("---")
    st.markdown("**和值统计**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("前区最小和值", f"{stats['sum_stats']['front_min']}")
    with col2:
        st.metric("前区平均和值", f"{stats['sum_stats']['front_avg']:.1f}")
    with col3:
        st.metric("前区最大和值", f"{stats['sum_stats']['front_max']}")

    # 奇偶统计
    st.markdown("**奇偶比例统计**")
    st.metric("前区平均奇数个数", f"{stats['odd_even']['avg_odd']:.2f} 个")
    st.metric("前区平均偶数个数", f"{stats['odd_even']['avg_even']:.2f} 个")


# ==================== 玩法说明 ====================
st.markdown("---")
with st.expander("📖 玩法说明 & 预测方法详解"):
    if lottery_type == "大乐透":
        st.markdown("""
        ### 🎱 体彩大乐透

        | 项目 | 说明 |
        |------|------|
        | 前区 | 从 1-35 中选 5 个号码 |
        | 后区 | 从 1-12 中选 2 个号码 |
        | 开奖时间 | 每周一、三、六 20:30 |
        | 一等奖 | 前区5个 + 后区2个全中 |

        **奖级设置：**
        - 一等奖：5+2（浮动奖金）
        - 二等奖：5+1（浮动奖金）
        - 三等奖：5+0（10000元）
        - 四等奖：4+2（3000元）
        - 五等奖：4+1（300元）
        - 六等奖：3+2 或 4+0（200元）
        - 七等奖：3+1 或 2+2（100元）
        - 八等奖：3+0 或 2+1 或 1+2 或 0+2（15元）
        - 九等奖：任意中3+1以下（5元）
        """)
    else:
        st.markdown("""
        ### 🔵 福彩双色球

        | 项目 | 说明 |
        |------|------|
        | 红球 | 从 1-33 中选 6 个号码 |
        | 蓝球 | 从 1-16 中选 1 个号码 |
        | 开奖时间 | 每周二、四、日 21:15 |
        | 一等奖 | 6个红球 + 1个蓝球全中 |

        **奖级设置：**
        - 一等奖：6+1（浮动奖金）
        - 二等奖：6+0（浮动奖金）
        - 三等奖：5+1（3000元）
        - 四等奖：5+0 或 4+1（200元）
        - 五等奖：4+0 或 3+1（10元）
        - 六等奖：2+1 或 1+1 或 0+1（5元）
        """)

    st.markdown("""
    ### 🔮 预测方法说明

    | 方法 | 原理 | 适用场景 |
    |------|------|----------|
    | 🔥 热门号码法 | 选择历史上出现频率最高的号码 | 相信热门号会持续热 |
    | ❄️ 冷门回补法 | 选择长期未出的遗漏号码 | 相信冷号会回补 |
    | 📊 加权随机法 | 根据历史频率加权随机选号 | 平衡热门和冷门 |
    | ⚖️ 均衡分布法 | 注重奇偶、大小号码均衡 | 喜欢平衡的号码组合 |
    | 📈 和值跨度法 | 基于历史和值和跨度范围 | 追求和值在合理区间 |
    | 🎯 区间分布法 | 保证号码在各区间均匀分布 | 避免号码过于集中 |
    | 🔗 连号分析法 | 根据连号出现概率选号 | 考虑连号规律 |
    | 🌟 综合推荐法 | 多维度综合分析推荐 | 不知道选哪个方法时 |

    ### ⚠️ 重要提醒

    1. **彩票开奖是随机事件**，任何分析方法都只能提供参考
    2. 本应用基于**2024-2025年真实开奖数据**进行统计分析
    3. 历史数据**不能预测未来**，请理性对待
    4. 购彩需量力而行，**切勿沉迷**
    """)


# ==================== 底部 ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🎱 彩票预测助手 Pro v2.0 | 基于真实历史数据的专业分析</p>
    <p>⚠️ 纯娱乐参考，请理性购彩 | © 2024-2025</p>
</div>
""", unsafe_allow_html=True)
