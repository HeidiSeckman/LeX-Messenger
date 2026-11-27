import html
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="LeX Messenger // LexiTech Studio", layout="wide")

@st.cache_resource
def get_sb():
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    return create_client(url, key) if url and key else None

sb = get_sb()
ST_OPEN = "<" + "style>"
ST_CLOSE = "<" + "/style>"

st.markdown(
    f"{ST_OPEN}"
    + ".stApp { background: #0b0e14; color: #f1f5f9; }"
    + ".stApp { background: #0b0e14; color: #f1f5f9; }"
    + ".block-container { padding-top: 3.2rem !important; }"
    + ".msg-card { background: #121826; border: 1px solid #263042; border-radius: 14px; padding: 14px; }"
    + ".bubble-me { background: #1e293b; border: 1px solid #3b465c; border-radius: 16px 16px 4px 16px; padding: 10px 14px; margin: 6px 0 6px auto; max-width: 72%; }"
    + ".bubble-them { background: #0f172a; border: 1px solid #1e293b; border-radius: 16px 16px 16px 4px; padding: 10px 14px; margin: 6px auto 6px 0; max-width: 72%; }"
    + f"{ST_CLOSE}",
    unsafe_allow_html=True,
)

if "lex_msg_user" not in st.session_state:
    st.session_state.lex_msg_user = None
if "active_chat_handle" not in st.session_state:
    st.session_state.active_chat_handle = None

if not st.session_state.lex_msg_user:
    import base64
    with open("lex-logo.png", "rb") as _lf:
        _logo_b64 = base64.b64encode(_lf.read()).decode()
    _, c_mid, _ = st.columns([1, 1.4, 1])
    with c_mid:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:16px;background:linear-gradient(145deg,#121826 0%,#0b0e14 70%,#07090e 100%);'
            f'border:1px solid #2e3748;border-radius:16px;padding:16px 20px;box-shadow:0 12px 32px rgba(0,0,0,0.8);margin:14px 0 18px 0;">'
            f'<img src="data:image/png;base64,{_logo_b64}" style="width:68px;height:68px;border-radius:14px;object-fit:contain;flex-shrink:0;"/>'
            f'<span style="display:inline-block;font-size:10px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;color:#e2e5ec;'
            f'<div style="font-size:10px;letter-spacing:1.6px;text-transform:uppercase;color:#94a3b8;margin:5px 0 8px 0;">Powered by LeX Social • LexiTech Studio</div>'            f'<div><div style="font-family:Georgia,serif;font-size:28px;font-weight:800;color:#ffffff;line-height:1.1;letter-spacing:0.2px;">LeX Messenger</div>'
            f'border:1px solid #3b465c;background:rgba(226,229,236,0.07);padding:3px 10px;border-radius:999px;">Public Beta // 13+</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        
        with st.form("msg_login_form"):
            em = st.text_input("LeX Social Email")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In to LeX Messenger", use_container_width=True):
                if sb and em.strip() and pw:
                    try:
                        res = sb.auth.sign_in_with_password({"email": em.strip(), "password": pw})
                        uid = res.user.id
                        rows = sb.table("lex_profiles").select("*").eq("user_id", uid).execute().data
                        if rows:
                            st.session_state.lex_msg_user = rows[0]
                            st.rerun()
                        else:
                            st.error("LeX Social profile not found.")
                    except Exception as e:
                        st.error(f"Sign in failed: {e}")
    st.markdown(
        '<div style="position:fixed;bottom:0;left:0;width:100vw;background:#000000;border-top:1px solid #222222;'
        'padding:10px 20px;z-index:999;text-align:center;color:#ffffff;font-size:12px;font-family:monospace;">'
        'LeX Messenger // Engineered by LexiTech Studio • 13+ Community • Support &amp; Safety: <b>support@lexsocial.space</b>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()
me = st.session_state.lex_msg_user
my_handle = str(me.get("handle", "")).lstrip("@")
my_low = my_handle.lower()
th_json = me.get("theme_json") or {}
raw_friends = th_json.get("all_friends") or []
friend_handles = sorted({
    str(f.get("handle") if isinstance(f, dict) else f).lstrip("@").strip()
    for f in raw_friends
    if str(f.get("handle") if isinstance(f, dict) else f).lstrip("@").strip().lower() != my_low
})

import base64
with open("lex-logo.png", "rb") as _lf:
    _logo_b64 = base64.b64encode(_lf.read()).decode()
b_left, b_right = st.columns([0.84, 0.16], vertical_alignment="center")
with b_left:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:14px;background:linear-gradient(145deg,#121826 0%,#0b0e14 70%,#07090e 100%);'
        f'border:1px solid #2e3748;border-radius:14px;padding:10px 18px;box-shadow:0 10px 28px rgba(0,0,0,0.75);margin-bottom:14px;">'
        f'<img src="data:image/png;base64,{_logo_b64}" style="width:46px;height:46px;border-radius:10px;object-fit:contain;"/>'
        f'<div><div style="font-size:20px;font-weight:800;color:#ffffff;line-height:1.1;">LeX Messenger <span style="color:#94a3b8;font-size:13px;font-weight:500;">@{html.escape(my_handle)}</span></div>'
        f'<div style="font-size:10px;letter-spacing:1.6px;text-transform:uppercase;color:#94a3b8;margin-top:2px;">Engineered by LexiTech Studio • Friends-Only Direct Chat</div></div></div>',
        unsafe_allow_html=True,
    )
with b_right:
    if st.button("Sign Out", use_container_width=True):
        st.session_state.lex_msg_user = None
        st.session_state.active_chat_handle = None
        st.rerun()

all_msgs = []
if sb and my_low:
    try:
        all_msgs = sb.table("lex_messages").select("*").order("id", desc=False).limit(600).execute().data or []
    except Exception:
        all_msgs = []

col_friends, col_chat = st.columns([0.32, 0.68], gap="medium")

with col_friends:
    st.markdown("<div class='msg-card'><b>Active Chats</b></div>", unsafe_allow_html=True)
    q_search = st.text_input("Search friends", placeholder="Filter by @handle...", label_visibility="collapsed")
    active_list = []
    other_list = []
    for fh in friend_handles:
        f_low = fh.lower()
        if q_search.strip() and q_search.strip().lstrip("@").lower() not in f_low:
            continue
        cnt = sum(
            1 for m in all_msgs
            if {str(m.get("sender_handle", "")).lstrip("@").lower(), str(m.get("recipient_handle", "")).lstrip("@").lower()} == {my_low, f_low}
            and not str(m.get("body", "")).startswith("[LEX_")
        )
        if cnt > 0:
            active_list.append((fh, cnt))
        else:
            other_list.append(fh)

    if not active_list:
        st.caption("No active chats yet.")
    for idx_f, (fh, cnt) in enumerate(active_list):
        if st.button(f"@{fh} ({cnt})", key=f"chat_sel_{idx_f}_{fh.lower()}", use_container_width=True):
            st.session_state.active_chat_handle = fh
            st.rerun()

    if other_list:
        st.markdown("<div style='margin-top:10px;font-size:12px;color:#94a3b8;font-weight:700;'>Start New Chat</div>", unsafe_allow_html=True)
        pick_new = st.selectbox("Start New Chat", ["Select a friend..."] + [f"@{fh}" for fh in other_list], label_visibility="collapsed", key="new_chat_dd")
        if pick_new != "Select a friend...":
            chosen = pick_new.lstrip("@")
            if st.session_state.active_chat_handle != chosen:
                st.session_state.active_chat_handle = chosen
                st.rerun()

with col_chat:
    default_chat = None   
    target = st.session_state.active_chat_handle or default_chat
    if not target:
        st.markdown("<div class='msg-card' style='text-align:center;padding:40px;'>Select a friend on the left to start messaging.</div>", unsafe_allow_html=True)
    else:
        t_low = target.lower()
        st.markdown(f"<div class='msg-card' style='margin-bottom:10px;'><b>Chatting with @{html.escape(target)}</b></div>", unsafe_allow_html=True)
        thread = [
            m for m in all_msgs
            if {str(m.get("sender_handle", "")).lstrip("@").lower(), str(m.get("recipient_handle", "")).lstrip("@").lower()} == {my_low, t_low}
            and not str(m.get("body", "")).startswith("[LEX_")
        ]
        chat_box = st.container(height=420)
        with chat_box:
            if not thread:
                st.caption("No messages yet. Say hello below!")
            for m in thread:
                s_low = str(m.get("sender_handle", "")).lstrip("@").lower()
                raw_b = str(m.get("body", ""))
                safe_b = html.escape(raw_b)
                if raw_b.startswith(("http://", "https://")) and any(raw_b.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".webp")):
                    inner = f'<img src="{safe_b}" style="max-width:240px;border-radius:10px;display:block;"/>'
                elif raw_b.startswith(("http://", "https://")):
                    inner = f'<a href="{safe_b}" target="_blank" style="color:#93c5fd;">{safe_b}</a>'
                else:
                    inner = safe_b
                if s_low == my_low:
                    st.markdown(f'<div class="bubble-me"><div style="font-size:10px;color:#94a3b8;">You</div><div>{inner}</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="bubble-them"><div style="font-size:10px;color:#94a3b8;">@{html.escape(target)}</div><div>{inner}</div></div>', unsafe_allow_html=True)

        with st.form("send_msg_form", clear_on_submit=True):
            c_in, c_btn = st.columns([0.82, 0.18])
            msg_txt = c_in.text_input("Message", placeholder=f"Message @{target} or paste an image/media URL...", label_visibility="collapsed")
            sent = c_btn.form_submit_button("Send", use_container_width=True)
            if sent and msg_txt.strip() and sb:
                if t_low not in {f.lower() for f in friend_handles}:
                    st.error("Friends-Only Messaging: You can only message approved friends.")
                else:
                    try:
                        sb.table("lex_messages").insert({
                            "sender_handle": my_handle,
                            "recipient_handle": target,
                            "body": msg_txt.strip(),
                        }).execute()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not send message: {e}")

st.markdown('<div style="margin-bottom:54px;"></div>', unsafe_allow_html=True)
st.markdown(
    '<div style="position:fixed;bottom:0;left:0;width:100vw;background:#000000;border-top:1px solid #222222;'
    'padding:10px 20px;z-index:999;text-align:center;color:#ffffff;font-size:12px;font-family:monospace;">'
    'LeX Messenger // Engineered by LexiTech Studio • 13+ Community • Support &amp; Safety: <b>support@lexsocial.space</b>'
    '</div>',
    unsafe_allow_html=True,
)
