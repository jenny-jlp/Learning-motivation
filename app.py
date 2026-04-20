import streamlit as st
import random
import time
import json
import os

# --- 1. 页面及持久化配置 ---
st.set_page_config(page_title="专属奖励系统-持久化版", page_icon="🎁", layout="centered")
DATA_FILE = "data.json"

# 默认初始数据 (已根据你的最新设置更新)
DEFAULT_DATA = {
    'draw_count': 0,
    'small_prizes': ["无条件上号陪打三局(全听你的)", "立刻马上外卖投喂一杯奶茶", "随机掉落的惊喜外卖盲盒", "洗头一次",
                     "肩颈按摩一次", "一本想看的书", "一袋爱吃的零食", "一个小手办"],
    'big_prizes': ["周末全套肩颈头部马杀鸡", "清空购物车(限额500)", "奶茶自由一周", "海鲜自助餐"],
    'pity_threshold': 10,
    'task_status': "none",
    'current_task': "",
    'history': []
}


# --- 2. 持久化核心函数 ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return DEFAULT_DATA.copy()
    return DEFAULT_DATA.copy()


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@st.cache_resource
def get_db():
    return load_data()


db = get_db()

# --- 3. 侧边栏：角色切换 ---
st.sidebar.title("🔐 身份切换")
role = st.sidebar.radio("请选择你的身份：", ["我是陈雨桐 👑", "我是官瑞安 👨‍💻"])

is_admin = False
if role == "我是官瑞安 👨‍💻":
    admin_password = st.sidebar.text_input("请输入专属暗号：", type="password")
    if admin_password == "520":
        is_admin = True
        st.sidebar.success("欢迎回来，瑞安！")

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

    if db['task_status'] == "none":
        st.subheader("📝 提交今日进度")
        task_desc = st.text_input("今天干了点啥？", placeholder="比如：OPPO设计稿初稿完成！")
        if st.button("🚀 提交审核"):
            if task_desc:
                db['current_task'] = task_desc
                db['task_status'] = "pending"
                save_data(db)
                st.success("已提交，等待瑞安审核中...")
                time.sleep(1)
                st.rerun()
            else:
                st.warning("提示：随便写点什么才能提交哦！")

    elif db['task_status'] == "pending":
        st.info(f"⏳ 审核中：{db['current_task']}")
        if st.button("🔄 刷新查看状态"):
            st.rerun()

    elif db['task_status'] == "approved":
        st.success("🎉 审核通过！")
        if st.button("🎁 开始抽奖！", use_container_width=True):
            db['draw_count'] += 1
            is_pity = db['draw_count'] % db['pity_threshold'] == 0
            pool = db['big_prizes'] if is_pity else db['small_prizes']
            prize = random.choice(pool)

            db['history'].append({
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "task": db['current_task'],
                "prize": prize,
                "type": "大奖" if is_pity else "常规"
            })

            st.session_state.last_prize = prize
            db['task_status'] = "none"
            db['current_task'] = ""
            save_data(db)
            st.rerun()

    if 'last_prize' in st.session_state:
        st.balloons()
        st.success(f"恭喜宝宝获得：【{st.session_state.last_prize}】")
        del st.session_state.last_prize

# ==========================================
# --- 5. 视图 B：官瑞安界面 (管理端) ---
# ==========================================
elif role == "我是官瑞安 👨‍💻":
    if not is_admin:
        st.warning("请输入正确暗号解锁后台")
    else:
        st.title("⚙️ 瑞安的管理后台")

        # 审核区
        st.header("📋 待处理审核")
        if db['task_status'] == "pending":
            st.write(f"**雨桐提交：** {db['current_task']}")
            c1, c2 = st.columns(2)
            if c1.button("✅ 批准", use_container_width=True):
                db['task_status'] = "approved"
                save_data(db)
                st.rerun()
            if c2.button("❌ 驳回", use_container_width=True):
                db['task_status'] = "none"
                save_data(db)
                st.rerun()
        else:
            st.info("暂无新任务")

        st.divider()

        # 奖池设置区
        st.header("🛠️ 奖池永久修改")
        st.write("在这里修改后点击“保存设置”，下次打开网页依然有效。")
        db['pity_threshold'] = st.number_input("保底次数", 1, 50, db['pity_threshold'])

        s_prizes = st.text_area("日常奖池(逗号分隔)", ",".join(db['small_prizes']))
        db['small_prizes'] = [x.strip() for x in s_prizes.split(",") if x.strip()]

        b_prizes = st.text_area("大奖池(逗号分隔)", ",".join(db['big_prizes']))
        db['big_prizes'] = [x.strip() for x in b_prizes.split(",") if x.strip()]

        if st.button("💾 保存奖池设置"):
            save_data(db)
            st.success("设置已永久保存！")

        st.divider()

        # 新增：手动修正数据区
        st.header("🎛️ 数据手动修正")
        st.write("如果发现抽奖次数不对，可以在这里手动调整进度。")
        new_draw_count = st.number_input("当前累计抽奖次数", min_value=0, max_value=1000, value=db['draw_count'],
                                         step=1)
        if st.button("💾 更新抽奖次数"):
            db['draw_count'] = new_draw_count
            save_data(db)
            st.success(f"已成功将抽奖次数修改为 {new_draw_count} 次！")
            time.sleep(1)
            st.rerun()

        st.divider()

        # 历史记录区
        st.header("🕒 历史提交记录")
        if db['history']:
            for h in reversed(db['history']):
                st.text(f"[{h['time']}] 任务：{h['task']} -> 抽中：{h['prize']}")
        else:
            st.write("尚无历史记录")

        if st.button("⚠️ 终极重置 (清空所有数据与历史)"):
            save_data(DEFAULT_DATA)
            st.rerun()