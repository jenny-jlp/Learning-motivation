import streamlit as st
import random
import time

# --- 1. 页面全局配置 ---
st.set_page_config(page_title="专属奖励小助手", page_icon="🎁", layout="centered")

# --- 2. 初始化简易数据库 (Session State) ---
# 保证在页面刷新和交互时，数据不会丢失
if 'draw_count' not in st.session_state:
    st.session_state.draw_count = 0
if 'small_prizes' not in st.session_state:
    st.session_state.small_prizes = ["奶茶报销券 🧋", "洗碗一次 🍽️", "疯狂夸夸三分钟 💬", "肩膀按摩10分钟 💆‍♀️"]
if 'big_prizes' not in st.session_state:
    st.session_state.big_prizes = ["清空购物车(限额500) 🛒", "周末浪漫大餐 🥩", "免生气金牌一张 🥇", "神秘盲盒礼物 🎁"]
if 'pity_threshold' not in st.session_state:
    st.session_state.pity_threshold = 5
if 'task_status' not in st.session_state:
    st.session_state.task_status = "none"  # 状态机：none(未提交), pending(待审核), approved(已通过)
if 'current_task' not in st.session_state:
    st.session_state.current_task = ""

# --- 3. 侧边栏：角色切换 ---
st.sidebar.title("🔐 身份切换")
role = st.sidebar.radio("请选择你的身份：", ["我是女朋友 👑", "我是男朋友 👨‍💻"])

# ==========================================
# --- 4. 视图 A：女朋友界面 (用户端) ---
# ==========================================
if role == "我是女朋友 👑":
    st.title("💖 宝宝的专属奖励系统")

    # 进度与保底看板
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="累计抽奖次数", value=st.session_state.draw_count)
    with col2:
        # 计算距离下次保底还需要几次
        draws_to_pity = st.session_state.pity_threshold - (
                    st.session_state.draw_count % st.session_state.pity_threshold)
        st.metric(label="距离大奖保底还需", value=f"{draws_to_pity} 次")

    st.divider()

    # 状态 1：未提交任务
    if st.session_state.task_status == "none":
        st.subheader("📝 提交新进度")
        task_desc = st.text_input("今天完成了什么？(例如：OPPO视觉图排版第一版搞定啦！)")
        uploaded_file = st.file_uploader("上传打卡照片或截图证明 (选填)", type=['png', 'jpg', 'jpeg'])

        if st.button("🚀 提交审核"):
            if task_desc:
                st.session_state.current_task = task_desc
                st.session_state.task_status = "pending"
                st.success("提交成功！快去催男朋友审核吧~")
                time.sleep(1)
                st.rerun()  # 刷新页面更新状态
            else:
                st.warning("提示：要写一下完成了什么才能提交哦！")

    # 状态 2：审核中
    elif st.session_state.task_status == "pending":
        st.info(f"⏳ 当前进度正在审核中：\n\n**{st.session_state.current_task}**")
        st.write("请耐心等待男朋友批准...")

    # 状态 3：审核通过，准备抽奖
    elif st.session_state.task_status == "approved":
        st.success("🎉 审核通过！你获得了一次抽奖机会！")

        if st.button("🎁 立即开始抽奖！", use_container_width=True):
            with st.spinner("幸运转盘疯狂转动中..."):
                time.sleep(1.5)  # 模拟一点延迟，增加期待感

                # 抽奖次数 +1
                st.session_state.draw_count += 1

                # 核心逻辑：保底判定
                if st.session_state.draw_count % st.session_state.pity_threshold == 0:
                    prize = random.choice(st.session_state.big_prizes)
                    st.balloons()  # 满屏气球动画
                    st.error(f"🌟 触发 SSR 保底大奖！恭喜获得：\n\n### 【{prize}】")
                else:
                    prize = random.choice(st.session_state.small_prizes)
                    st.success(f"✨ 抽奖成功！恭喜获得：\n\n### 【{prize}】")

                # 抽完奖后，重置任务状态，以便进行下一次提交
                st.session_state.task_status = "none"
                st.session_state.current_task = ""


# ==========================================
# --- 5. 视图 B：男朋友界面 (管理端) ---
# ==========================================
elif role == "我是男朋友 👨‍💻":
    st.title("⚙️ 奖励系统后台管理")

    # 审核中心模块
    st.header("📋 审核中心")
    if st.session_state.task_status == "pending":
        st.warning("⚠️ 收到新的进度提交！")
        st.write(f"**对方提交的任务描述：** {st.session_state.current_task}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 批准 (发放抽奖资格)", use_container_width=True):
                st.session_state.task_status = "approved"
                st.rerun()
        with col2:
            if st.button("❌ 驳回 (让她重写)", use_container_width=True):
                st.session_state.task_status = "none"
                st.session_state.current_task = ""
                st.rerun()
    else:
        st.info("目前没有待审核的任务，你可以去喝杯水。")

    st.divider()

    # 规则与参数配置模块
    st.header("🛠️ 规则与奖池动态设置")

    # 保底阈值设置
    new_pity = st.number_input("多少次保底必出大奖？", min_value=1, max_value=20, value=st.session_state.pity_threshold)
    st.session_state.pity_threshold = new_pity

    # 小奖池管理 (使用逗号分隔的字符串来简易管理列表，方便在网页上直接修改)
    st.subheader("🎈 小奖池 (日常奖励)")
    small_prizes_str = st.text_area("编辑小奖池 (用英文逗号 , 隔开)", value=",".join(st.session_state.small_prizes))
    st.session_state.small_prizes = [p.strip() for p in small_prizes_str.split(",") if p.strip()]

    # 大奖池管理
    st.subheader("💎 大奖池 (SSR 保底专属)")
    big_prizes_str = st.text_area("编辑大奖池 (用英文逗号 , 隔开)", value=",".join(st.session_state.big_prizes))
    st.session_state.big_prizes = [p.strip() for p in big_prizes_str.split(",") if p.strip()]