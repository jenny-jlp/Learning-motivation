import streamlit as st
import random
import time

# --- 1. 页面全局配置 ---
st.set_page_config(page_title="专属奖励小助手", page_icon="🎁", layout="centered")


# --- 2. 初始化全局共享数据 (联机核心) ---
@st.cache_resource
def get_global_state():
    return {
        'draw_count': 0,
        'small_prizes': ["无条件上号陪打三局(全听你的) 🛡️", "立刻马上外卖投喂一杯奶茶 🧋", "随机掉落的惊喜外卖盲盒 🍢",
                         "洗头一次", "肩颈按摩一次"],
        'big_prizes': ["周末全套肩颈头部马杀鸡 💆‍♀️", "周末约会行程全包(我做攻略买单) 🗺️", "清空购物车(限额500) 🛒",
                       "报销一件高颜值设计好物 🎁", "周末见面的神秘实体盲盒 💝"],
        'pity_threshold': 15,
        'task_status': "none",
        'current_task': "",
        'task_image': None  # 新增：用于在云端存储她上传的图片数据
    }


db = get_global_state()

# --- 3. 侧边栏：角色切换与密码验证 ---
st.sidebar.title("🔐 身份切换")
role = st.sidebar.radio("请选择你的身份：", ["我是陈雨桐 👑", "我是官瑞安 👨‍💻"])

# 密码验证逻辑
is_admin = False
if role == "我是官瑞安 👨‍💻":
    admin_password = st.sidebar.text_input("请输入专属暗号解锁后台：", type="password")
    if admin_password == "520":
        is_admin = True
        st.sidebar.success("暗号正确，欢迎瑞安！")
    elif admin_password != "":
        st.sidebar.error("暗号不对哦，你是不是想偷看后台！")

# ==========================================
# --- 4. 视图 A：陈雨桐界面 (用户端) ---
# ==========================================
if role == "我是陈雨桐 👑":
    st.title("💖 雨桐的专属奖励系统")

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="累计抽奖次数", value=db['draw_count'])
    with col2:
        draws_to_pity = db['pity_threshold'] - (db['draw_count'] % db['pity_threshold'])
        st.metric(label="距离大奖保底还需", value=f"{draws_to_pity} 次")

    st.divider()

    if st.button("🔄 刷新页面 (看看官瑞安批了没)"):
        st.rerun()

    if db['task_status'] == "none":
        st.subheader("📝 提交今日打卡/进度")
        task_desc = st.text_input("今天干了点啥？(比如：OPPO视觉图排版搞定啦！)")

        # 新增：真正的文件上传组件
        uploaded_file = st.file_uploader("上传打卡照片或截图证明 (选填哦)", type=['png', 'jpg', 'jpeg'])

        if st.button("🚀 提交给官瑞安审核"):
            if task_desc:
                db['current_task'] = task_desc
                # 如果她传了图，就把图片转换成数据存入咱们的全局变量里
                if uploaded_file is not None:
                    db['task_image'] = uploaded_file.getvalue()
                else:
                    db['task_image'] = None

                db['task_status'] = "pending"
                st.success("提交成功！快去微信滴滴他审核吧~")
                time.sleep(1)
                st.rerun()
            else:
                st.warning("提示：随便写点什么才能提交哦！")

    elif db['task_status'] == "pending":
        st.info(f"⏳ 当前进度正在审核中：\n\n**{db['current_task']}**")
        st.write("请耐心等待官瑞安批准...")

    elif db['task_status'] == "approved":
        st.success("🎉 审核通过！你获得了一次抽奖机会！")
        if st.button("🎁 立即开始抽奖！", use_container_width=True):
            with st.spinner("幸运转盘疯狂转动中..."):
                time.sleep(1.5)
                db['draw_count'] += 1
                if db['draw_count'] % db['pity_threshold'] == 0:
                    prize = random.choice(db['big_prizes'])
                    st.balloons()
                    st.error(f"🌟 触发 SSR 保底大奖！恭喜雨桐获得：\n\n### 【{prize}】")
                else:
                    prize = random.choice(db['small_prizes'])
                    st.success(f"✨ 抽奖成功！恭喜雨桐获得：\n\n### 【{prize}】")

                db['task_status'] = "none"
                db['current_task'] = ""
                db['task_image'] = None  # 抽完奖清空图片


# ==========================================
# --- 5. 视图 B：官瑞安界面 (管理端 - 需要密码) ---
# ==========================================
elif role == "我是官瑞安 👨‍💻":
    if not is_admin:
        st.warning("👆 请在左侧输入专属暗号解锁管理后台！")
    else:
        st.title("⚙️ 官瑞安的后台管理")

        if st.button("🔄 刷新页面 (看看雨桐有没有新提交)"):
            st.rerun()

        st.header("📋 审核中心")
        if db['task_status'] == "pending":
            st.warning("⚠️ 收到雨桐新的进度提交！")
            st.write(f"**雨桐提交的描述：** {db['current_task']}")

            # 新增：如果库里有图片数据，就在后台展示出来！
            if db['task_image'] is not None:
                st.image(db['task_image'], caption="附带的打卡凭证 👀", use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ 批准 (发放抽奖资格)", use_container_width=True):
                    db['task_status'] = "approved"
                    st.rerun()
            with col2:
                if st.button("❌ 驳回 (让她重写)", use_container_width=True):
                    db['task_status'] = "none"
                    db['current_task'] = ""
                    db['task_image'] = None  # 驳回也清空图片
                    st.rerun()
        else:
            st.info("目前没有待审核的任务。")

        st.divider()

        st.header("🛠️ 规则与奖池动态设置")
        new_pity = st.number_input("多少次保底必出大奖？", min_value=1, max_value=50, value=db['pity_threshold'])
        db['pity_threshold'] = new_pity

        st.subheader("🎈 小奖池 (日常奖励)")
        small_prizes_str = st.text_area("编辑小奖池 (用英文逗号 , 隔开)", value=",".join(db['small_prizes']))
        db['small_prizes'] = [p.strip() for p in small_prizes_str.split(",") if p.strip()]

        st.subheader("💎 大奖池 (SSR 保底专属)")
        big_prizes_str = st.text_area("编辑大奖池 (用英文逗号 , 隔开)", value=",".join(db['big_prizes']))
        db['big_prizes'] = [p.strip() for p in big_prizes_str.split(",") if p.strip()]

        st.divider()

        st.header("🔄 数据与测试重置")
        st.write("如果测试抽奖次数太多了，可以在这里一键清零。")
        if st.button("⚠️ 重置抽奖次数为 0", type="primary"):
            db['draw_count'] = 0
            st.success("✅ 抽奖次数已清零！")
            time.sleep(1)
            st.rerun()