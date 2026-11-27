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
    _, c_logo, _ = st.columns([1.45, 0.3, 1.45])
    with c_logo:
        st.image("lex-logo.png", width=76)
    st.markdown("<h2 style='text-align:center;margin-top:4px;'>LeX Messenger</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#94a3b8;font-size:12px;letter-spacing:1.5px;'>POWERED BY LEX SOCIAL • LEXITECH STUDIO</p>", unsafe_allow_html=True)
    _, c_mid, _ = st.columns([1, 1.4, 1])
    with c_mid:
        with st.form("msg_login_form"):
            em = st.text_input("LeX Social Email")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In to LeX Messenger", use_container_width=True):
                if sb and em.strip() and pw:
                    try:
                        res = sb.auth.sign_in_with_password({"email": em.strip(), "password": pw})
                        uid = res.user.id
                        rows = sb.table("lex_profiles").select("*").eq("id", uid).execute().data
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

h_left, h_right = st.columns([0.82, 0.18])
with h_left:
    st.markdown(f"<h3 style='margin:0;'>LeX Messenger <span style='color:#94a3b8;font-size:14px;'>@{html.escape(my_handle)}</span></h3>", unsafe_allow_html=True)
with h_right:
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
    st.markdown("<div class='msg-card'><b>Chats &amp; Approved Friends</b></div>", unsafe_allow_html=True)
    q_search = st.text_input("Search friends", placeholder="Filter by @handle...", label_visibility="collapsed")
    shown_friends = [fh for fh in friend_handles if not q_search.strip() or q_search.strip().lstrip("@").lower() in fh.lower()]
    if not shown_friends:
        st.info("No approved friends found yet. Add friends on LeX Social first!")
    for idx_f, fh in enumerate(shown_friends):
        f_low = fh.lower()
        thread_count = sum(
            1 for m in all_msgs
            if {str(m.get("sender_handle", "")).lstrip("@").lower(), str(m.get("recipient_handle", "")).lstrip("@").lower()} == {my_low, f_low}
            and not str(m.get("body", "")).startswith(("[LEX_F]", "[LEX_NOTIF]"))
        )
        lbl = f"@{fh} ({thread_count})" if thread_count else f"@{fh}"
        if st.button(lbl, key=f"chat_sel_{idx_f}_{f_low}", use_container_width=True):
            st.session_state.active_chat_handle = fh
            st.rerun()

with col_chat:
    target = st.session_state.active_chat_handle or (shown_friends[0] if shown_friends else None)
    if not target:
        st.markdown("<div class='msg-card' style='text-align:center;padding:40px;'>Select a friend on the left to start messaging.</div>", unsafe_allow_html=True)
    else:
        t_low = target.lower()
        st.markdown(f"<div class='msg-card' style='margin-bottom:10px;'><b>Chatting with @{html.escape(target)}</b></div>", unsafe_allow_html=True)
        thread = [
            m for m in all_msgs
            if {str(m.get("sender_handle", "")).lstrip("@").lower(), str(m.get("recipient_handle", "")).lstrip("@").lower()} == {my_low, t_low}
            and not str(m.get("body", "")).startswith(("[LEX_F]", "[LEX_NOTIF]"))
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
