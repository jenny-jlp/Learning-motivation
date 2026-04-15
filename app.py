import streamlit as st
import random
import time

# --- 1. 页面全局配置 ---
st.set_page_config(page_title="专属奖励小助手", page_icon="🎁", layout="centered")

# --- 2. 初始化简易数据库 (Session State) ---
if 'draw_count' not in st.session_state:
    st.session_state.draw_count = 0
# 小奖池 (已替换为吃喝玩乐版)
if 'small_prizes' not in st.session_state:
    st.session_state.small_prizes = ["王者荣耀精美皮肤任选一个 👗", "无条件上号陪打三局(我包打辅助) 🛡️",
                                     "游戏连败免背锅特权一次 🙅‍♀️", "立刻马上外卖投喂一杯奶茶 🧋",
                                     "随机掉落的惊喜宵夜盲盒 🍢", "连麦同步看一部你想看的电影 🍿",
                                     "获得一次真心话强制回答权 🤫", "24小时电子宠物随叫随到体验卡 🐶"]
# 大奖池
if 'big_prizes' not in st.session_state:
    st.session_state.big_prizes = ["周末全套肩颈头部马杀鸡 💆‍♀️", "周末约会行程全包(我做攻略买单) 🗺️",
                                   "清空购物车(限额500) 🛒", "报销一件高颜值设计好物 🎁", "周末两天家务点餐全包特权 🧹",
                                   "免生气及无条件认错金牌 🥇", "周末见面的神秘实体盲盒 💝"]
if 'pity_threshold' not in st.session_state:
    st.session_state.pity_threshold = 15
if 'task_status' not in st.session_state:
    st.session_state.task_status = "none"
if 'current_task' not in st.session_state:
    st.session_state.current_task = ""

# --- 3. 侧边栏：角色切换与密码验证 ---
st.sidebar.title("🔐 身份切换")
role = st.sidebar.radio("请选择你的身份：", ["我是女朋友 👑", "我是男朋友 👨‍💻"])

# 密码验证逻辑
is_admin = False
if role == "我是男朋友 👨‍💻":
    # 在这里修改你的专属密码，目前是 "520"
    admin_password = st.sidebar.text_input("请输入专属暗号解锁后台：", type="password")
    if admin_password == "520":
        is_admin = True
        st.sidebar.success("暗号正确，欢迎老板！")
    elif admin_password != "":
        st.sidebar.error("暗号不对哦，你是不是想偷看后台！")

# ==========================================
# --- 4. 视图 A：女朋友界面 (用户端) ---
# ==========================================
if role == "我是女朋友 👑":
    st.title("💖 宝宝的专属奖励系统")

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="累计抽奖次数", value=st.session_state.draw_count)
    with col2:
        draws_to_pity = st.session_state.pity_threshold - (
                    st.session_state.draw_count % st.session_state.pity_threshold)
        st.metric(label="距离大奖保底还需", value=f"{draws_to_pity} 次")

    st.divider()

    if st.session_state.task_status == "none":
        st.subheader("📝 提交今日打卡/进度")
        task_desc = st.text_input("今天干了点啥？(比如：今天按时吃早饭啦！)")
        uploaded_file = st.file_uploader("上传打卡照片或截图证明 (选填)", type=['png', 'jpg', 'jpeg'])

        if st.button("🚀 提交给男朋友审核"):
            if task_desc:
                st.session_state.current_task = task_desc
                st.session_state.task_status = "pending"
                st.success("提交成功！快去微信滴滴他审核吧~")
                time.sleep(1)
                st.rerun()
            else:
                st.warning("提示：随便写点什么才能提交哦！")

    elif st.session_state.task_status == "pending":
        st.info(f"⏳ 当前进度正在审核中：\n\n**{st.session_state.current_task}**")
        st.write("请耐心等待男朋友批准...")

    elif st.session_state.task_status == "approved":
        st.success("🎉 审核通过！你获得了一次抽奖机会！")
        if st.button("🎁 立即开始抽奖！", use_container_width=True):
            with st.spinner("幸运转盘疯狂转动中..."):
                time.sleep(1.5)

                st.session_state.draw_count += 1

                if st.session_state.draw_count % st.session_state.pity_threshold == 0:
                    prize = random.choice(st.session_state.big_prizes)
                    st.balloons()
                    st.error(f"🌟 触发 SSR 保底大奖！恭喜宝宝获得：\n\n### 【{prize}】")
                else:
                    prize = random.choice(st.session_state.small_prizes)
                    st.success(f"✨ 抽奖成功！恭喜宝宝获得：\n\n### 【{prize}】")

                st.session_state.task_status = "none"
                st.session_state.current_task = ""


# ==========================================
# --- 5. 视图 B：男朋友界面 (管理端 - 需要密码) ---
# ==========================================
elif role == "我是男朋友 👨‍💻":
    if not is_admin:
        st.warning("👆 请在左侧输入专属暗号解锁管理后台！")
    else:
        st.title("⚙️ 奖励系统后台管理")

        # 审核中心
        st.header("📋 审核中心")
        if st.session_state.task_status == "pending":
            st.warning("⚠️ 收到新的进度提交！")
            st.write(f"**宝宝提交的描述：** {st.session_state.current_task}")

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
            st.info("目前没有待审核的任务。")

        st.divider()

        # 规则与参数配置
        st.header("🛠️ 规则与奖池动态设置")
        new_pity = st.number_input("多少次保底必出大奖？", min_value=1, max_value=50,
                                   value=st.session_state.pity_threshold)
        st.session_state.pity_threshold = new_pity

        st.subheader("🎈 小奖池 (日常奖励)")
        small_prizes_str = st.text_area("编辑小奖池 (用英文逗号 , 隔开)", value=",".join(st.session_state.small_prizes))
        st.session_state.small_prizes = [p.strip() for p in small_prizes_str.split(",") if p.strip()]

        st.subheader("💎 大奖池 (SSR 保底专属)")
        big_prizes_str = st.text_area("编辑大奖池 (用英文逗号 , 隔开)", value=",".join(st.session_state.big_prizes))
        st.session_state.big_prizes = [p.strip() for p in big_prizes_str.split(",") if p.strip()]

        st.divider()

        # 新增：重置数据专区
        st.header("🔄 数据与测试重置")
        st.write("如果测试抽奖次数太多了，可以在这里一键清零。")
        if st.button("⚠️ 重置抽奖次数为 0", type="primary"):
            st.session_state.draw_count = 0
            st.success("✅ 抽奖次数已清零！")
            time.sleep(1)
            st.rerun()