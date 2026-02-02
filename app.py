import streamlit as st
import utils
import export_utils
import secrets_utils
import profile_utils
import json
import os
import datetime
from io import BytesIO

# --- Page Config ---
st.set_page_config(page_title="AI Cover Letter Generator v1.1", layout="wide", page_icon="📝")

# --- Session State Init ---
DEFAULTS = {
    "api_key": "",
    "provider": "Google Gemini",
    "cover_letter_content": None,
    "docx_data": None,
    "pdf_data": None,
    "latex_data": None,
    "latex_code": None,
    "session_usage": {"tokens": 0, "cost_est": 0.0, "chars": 0},
    "master_password": None,
    "profile_name": "Default",
    "export_formats": ["Word", "PDF", "LaTeX"],
    "gen_metadata": {},
    "last_cv_text": None,
    "last_job_description": None,
    "recorded_video_path": None, # New
    "current_question": None, # New
    "resume_review_result": None, # New
    "questions_queue": [], # Mock Interview
    "current_q_index": 0
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- Helper: Secrets Loading ---
def get_secrets_status():
    """Loads secrets considering lock state."""
    pwd = st.session_state.master_password
    return secrets_utils.load_secrets(pwd)

def update_exports():
    """Regenerates export files when text is edited."""
    if not st.session_state.gen_metadata:
        return
        
    meta = st.session_state.gen_metadata
    full_data = {
        "body": st.session_state.cover_letter_content,
        "user_info": meta.get("user_info", {}),
        "date_str": meta.get("date_str", ""),
        "hr_info": meta.get("hr_info", {})
    }
    
    formats = st.session_state.export_formats
    if "Word" in formats:
        st.session_state.docx_data = export_utils.create_docx(full_data)
    if "PDF" in formats:
        st.session_state.pdf_data = export_utils.create_pdf(full_data)
    if "LaTeX" in formats:
        data, code = export_utils.create_latex(full_data)
        st.session_state.latex_data = data
        st.session_state.latex_code = code

# --- Sidebar ---
with st.sidebar:
    st.title("🧩 Status")
    
    # Profile Selector
    profile_list = profile_utils.list_profiles()
    selected_idx = 0
    if st.session_state.profile_name in profile_list:
        selected_idx = profile_list.index(st.session_state.profile_name)
    
    new_profile_selection = st.selectbox("👤 Active Profile", profile_list, index=selected_idx)
    if new_profile_selection != st.session_state.profile_name:
        st.session_state.profile_name = new_profile_selection
        st.rerun()

    # Secrets Status
    secrets_status = get_secrets_status()
    if secrets_status["requires_unlock"]:
        st.error("🔒 Secrets Locked")
        pwd_input = st.text_input("Unlock Password", type="password", key="sidebar_pwd")
        if st.button("Unlock"):
            st.session_state.master_password = pwd_input
            st.rerun()
    else:
        if st.session_state.api_key:
            st.success("🟢 API Key: Active")
        else:
            st.warning("🔴 API Key: Missing")

    st.divider()
    
    # Usage Stats
    st.subheader("📊 Session Usage")
    u = st.session_state.session_usage
    if u['tokens'] > 0:
        st.write(f"**Tokens**: ~{u['tokens']}")
    if u['chars'] > 0:
        st.write(f"**Chars**: ~{u['chars']}")
        
    st.divider()
    if st.button("🔄 Reset Session"):
        st.session_state.clear()
        st.rerun()

# --- Main Layout ---
import recorder_utils 
from streamlit_webrtc import webrtc_streamer, WebRtcMode

st.title("CareerForge AI: Professional Career Suite")
tab_generator, tab_review, tab_coach, tab_settings = st.tabs(["🚀 Generator", "🧪 Resume Review", "🎥 Interview Coach", "⚙️ Settings"])

# ==========================
# TAB: SETTINGS
# ==========================
with tab_settings:
    st.header("⚙️ Configuration")
    
    col_set_1, col_set_2 = st.columns(2)
    
    # --- Section: API & Keys ---
    with col_set_1:
        st.subheader("1. AI Provider & Keys")
        
        # Provider
        provider = st.radio("Provider", ["Google Gemini", "OpenAI"], 
                          index=0 if st.session_state.provider == "Google Gemini" else 1)
        st.session_state.provider = provider
        
        prov_key = "OpenAI" if provider == "OpenAI" else "Gemini"
        
        # Model (Cosmetic / passed to logic)
        MODEL_OPTIONS = {
            "Google Gemini": {
                "gemini-3-flash-preview": "Gemini 3.0 Flash (New/Fast)",
                "gemini-3-pro-preview": "Gemini 3.0 Pro (New/Smart)",
                "gemini-2.0-flash-exp": "Gemini 2.0 Flash (Experimental)",
                "gemini-1.5-flash": "Gemini 1.5 Flash (Standard)", 
                "gemini-1.5-pro": "Gemini 1.5 Pro (High Reasoning)",
                "gemini-pro": "Gemini 1.0 Pro (Legacy/Stable)"
            },
            "OpenAI": {
                "gpt-5.2": "GPT-5.2 (Best Results)",
                "gpt-5-mini": "GPT-5 Mini (Fast/Efficient)",
                "gpt-4o": "GPT-4o (Legacy/Stable)", 
                "gpt-4o-mini": "GPT-4o Mini (Cheapest)"
            }
        }
        
        model_map = MODEL_OPTIONS[provider]
        selected_display = st.selectbox("Model", list(model_map.values()))
        # Reverse map
        selected_model_name = [k for k, v in model_map.items() if v == selected_display][0]
        
        st.markdown("---")
        
        # Secrets Management
        secrets = get_secrets_status()
        
        if secrets["requires_unlock"]:
            st.info("Unlock vault in Sidebar to manage keys.")
        else:
            # Key Selection
            key_list = secrets.get("openai_keys" if provider == "OpenAI" else "gemini_keys", [])
            
            # Format for dropdown: "Name (Masked)" -> value is actual key
            # We need a map. 
            # key_list is mixed: strings (legacy) or dicts (new)
            
            key_options = {}
            for k_item in key_list:
                if isinstance(k_item, dict):
                    display = f"{k_item.get('name', 'Key')} (...{k_item.get('key', '')[-4:]})"
                    value = k_item.get('key')
                else:
                    display = f"Legacy (...{k_item[-4:] if len(k_item)>4 else ''})"
                    value = k_item
                key_options[display] = value
                
            NEW_OPTION = "➕ Add New Key"
            selection = st.selectbox("Select Key", [NEW_OPTION] + list(key_options.keys()))
            
            if selection == NEW_OPTION:
                new_key_val = st.text_input("Enter API Key", type="password")
                new_key_name = st.text_input("Key Name (e.g. Personal)", value="My Key")
                save_check = st.checkbox("Save to Vault")
                
                current_api_key = new_key_val
                if save_check and new_key_val:
                    if secrets["is_encrypted"]:
                        if st.button("💾 Save Encrypted"):
                            if secrets_utils.save_secret_encrypted(prov_key, new_key_name, new_key_val, st.session_state.master_password):
                                st.success("Saved!")
                                st.rerun()
                            else:
                                st.error("Failed to save.")
                    else:
                        if st.button("💾 Save Plaintext"):
                            secrets_utils.save_secret_plain(prov_key, new_key_val, new_key_name) 
                            st.success("Saved!")
                            st.rerun()
            else:
                current_api_key = key_options[selection]
                st.session_state.api_key = current_api_key
                st.info(f"Using: {selection}")
                
            # Encryption Setup
            if not secrets["is_encrypted"] and not secrets["requires_unlock"]:
                st.markdown("---")
                with st.expander("🔐 Security: Encrypt Vault"):
                    st.warning("Set a master password. All keys will be encrypted.")
                    pass1 = st.text_input("Master Password", type="password")
                    pass2 = st.text_input("Confirm Password", type="password")
                    if st.button("Enable Encryption"):
                        if pass1 and pass1 == pass2:
                            secrets_utils.init_encryption(pass1)
                            st.session_state.master_password = pass1
                            st.success("Vault Encrypted!")
                            st.rerun()
                        else:
                            st.error("Passwords do not match.")

    # --- Section: Profile ---
    with col_set_2:
        st.subheader(f"2. Profile: {st.session_state.profile_name}")
        
        # Load active profile
        profile_data = profile_utils.load_profile(st.session_state.profile_name)
        
        with st.form("profile_form"):
            p_name = st.text_input("Full Name", value=profile_data.get("full_name", ""))
            p_email = st.text_input("Email", value=profile_data.get("email", ""))
            p_phone = st.text_input("Phone", value=profile_data.get("phone", ""))
            p_link = st.text_input("LinkedIn", value=profile_data.get("linkedin", ""))
            p_addr = st.text_input("Address", value=profile_data.get("address", ""))
            
            if st.form_submit_button("💾 Save Profile"):
                new_data = {
                    "full_name": p_name, "email": p_email, "phone": p_phone, 
                    "linkedin": p_link, "address": p_addr
                }
                profile_utils.save_profile(st.session_state.profile_name, new_data)
                st.success("Saved!")
        
        st.markdown("#### Create New Profile")
        new_prof_name = st.text_input("New Profile Name")
        if st.button("Create Profile"):
            if new_prof_name:
                profile_utils.save_profile(new_prof_name, {}) # Create empty
                st.session_state.profile_name = new_prof_name
                st.rerun()

    # --- Section: Exports Preference ---
    st.markdown("---")
    st.subheader("3. Export Formats")
    ex_cols = st.columns(3)
    opts = ["Word", "PDF", "LaTeX"]
    selected_exports = []
    
    # Simple checkbox tracking
    if "export_formats" not in st.session_state: st.session_state.export_formats = opts
    
    for opt in opts:
        is_checked = opt in st.session_state.export_formats
        if st.checkbox(opt, value=is_checked, key=f"check_{opt}"):
            selected_exports.append(opt)
    
    st.session_state.export_formats = selected_exports
    
    # --- Danger Zone (Factory Reset) ---
    st.markdown("---")
    st.subheader("🚫 Danger Zone")
    st.warning("Erase all data? This will delete all Profiles and API Keys permanently (Factory Reset).")
    
    if st.button("🧨 Factory Reset (Clear All Data)", type="primary"):
        # 1. Delete Secrets
        if os.path.exists(secrets_utils.SECRETS_FILE):
             try: os.remove(secrets_utils.SECRETS_FILE)
             except: pass
            
        # 2. Delete Profiles
        import shutil
        if os.path.exists(profile_utils.PROFILES_DIR):
            try: shutil.rmtree(profile_utils.PROFILES_DIR)
            except: pass
            
        # 3. Clear Session
        st.session_state.clear()
        st.rerun()


# ==========================
# TAB: GENERATOR
# ==========================
with tab_generator:
    st.header("🚀 Create Cover Letter")
    
    # Reload profile just in case
    live_profile = profile_utils.load_profile(st.session_state.profile_name)
    user_info = {
        "name": live_profile.get("full_name", ""),
        "email": live_profile.get("email", ""),
        "phone": live_profile.get("phone", ""),
        "linkedin": live_profile.get("linkedin", ""),
        "address": live_profile.get("address", "")
    }

    col_gen_1, col_gen_2 = st.columns([1, 1])
    
    with col_gen_1:
        st.subheader("Input")
        uploaded_file = st.file_uploader("1. Upload Resume (PDF)", type="pdf")
        job_description = st.text_area("2. Paste Job Description", height=300)
        
        today = datetime.date.today()
        letter_date = st.date_input("3. Date", value=today)
        date_str = letter_date.strftime("%B %d, %Y")
        
        generate_btn = st.button("✨ Generate", type="primary", use_container_width=True)

    with col_gen_2:
        st.subheader("Result")
        
        if generate_btn:
            if not st.session_state.api_key:
                st.error("❌ Missing API Key in Settings.")
            elif not uploaded_file or not job_description:
                st.error("❌ Missing Resume or JD.")
            else:
                with st.spinner("Analyzing & Writing..."):
                    # Extract Text
                    cv_text = utils.extract_text_from_pdf(uploaded_file)
                    
                    if cv_text:
                        st.session_state.last_cv_text = cv_text
                        st.session_state.last_job_description = job_description
                        prov_key_norm = "Gemini" if provider == "Google Gemini" else "OpenAI"
                        
                        result = utils.generate_cover_letter(
                            cv_text, job_description, st.session_state.api_key, 
                            prov_key_norm, user_info, selected_model_name, date_str
                        )
                        
                        if result["ok"]:
                            st.success("✅ Generated!")
                            st.session_state.cover_letter_content = result["text"]
                            
                            # Update Usage
                            u_clean = st.session_state.session_usage
                            new_u = result.get("usage", {})
                            u_clean['tokens'] += new_u.get("total_tokens", 0)
                            u_clean['chars'] += new_u.get("input_chars", 0) + new_u.get("output_chars", 0)
                            
                            # Generate Exports
                            full_data = {
                                "body": result["text"],
                                "user_info": live_profile,
                                "date_str": date_str,
                                "hr_info": result.get("hr_info_debug", {})
                            }
                            
                            # Save Metadata for editing
                            st.session_state.gen_metadata = {
                                "user_info": live_profile,
                                "date_str": date_str,
                                "hr_info": result.get("hr_info_debug", {})
                            }
                            
                            # Only generate selected
                            formats = st.session_state.export_formats
                            if "Word" in formats:
                                st.session_state.docx_data = export_utils.create_docx(full_data)
                            if "PDF" in formats:
                                st.session_state.pdf_data = export_utils.create_pdf(full_data)
                            if "LaTeX" in formats:
                                data, code = export_utils.create_latex(full_data)
                                st.session_state.latex_data = data
                                st.session_state.latex_code = code
                            
                            
                        else:
                            st.error(f"Failed: {result['error']}")
                            
                    else:
                        st.error("Failed to read PDF.")

        # Persistent View
        if st.session_state.cover_letter_content:
            # Editable Preview
            st.markdown("### Preview & Edit")
            st.text_area(
                "Edit your cover letter here to update downloads:",
                key="cover_letter_content",
                height=400,
                on_change=update_exports
            )
            
            # Copy Code (Optional)
            with st.expander("📋 View Raw Text (Copy)"):
                st.code(st.session_state.cover_letter_content, language="markdown")
                
            # Downloads
            dl_cols = st.columns(3)
            formats = st.session_state.export_formats
            
            if "Word" in formats and st.session_state.docx_data:
                dl_cols[0].download_button(
                    label="Download .docx",
                    data=st.session_state.docx_data,
                    file_name="cover_letter.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    icon="📄"
                )
            
            if "PDF" in formats and st.session_state.pdf_data:
                dl_cols[1].download_button(
                    label="Download .pdf",
                    data=st.session_state.pdf_data,
                    file_name="cover_letter.pdf",
                    mime="application/pdf",
                    icon="📑"
                )
                
                if "LaTeX" in formats and st.session_state.latex_data:
                    dl_cols[2].download_button(
                        label="Download .tex",
                        data=st.session_state.latex_data,
                        file_name="cover_letter.tex",
                        mime="application/x-tex",
                        icon="📜"
                    )

# ==========================
# TAB: RESUME REVIEW
# ==========================
with tab_review:
    st.header("🧪 Resume Review")

    review_col_1, review_col_2 = st.columns([1, 1])

    with review_col_1:
        st.subheader("Input")
        
        # 1. Resume Handling
        review_file = st.file_uploader("1. Upload Resume (PDF)", type="pdf", key="review_resume")
        
        # Context Aware Logic
        active_cv_text = None
        if review_file:
             active_cv_text = utils.extract_text_from_pdf(review_file)
        elif st.session_state.get("last_cv_text"):
             st.info("✅ Using Resume from Generator tab")
             active_cv_text = st.session_state.last_cv_text
             
        # 2. JD Handling
        # Fix: Streamlit widget state persistence. If widget is empty but global JD exists, sync it.
        if st.session_state.get("last_job_description"):
            if "review_jd" not in st.session_state or not st.session_state.review_jd:
                st.session_state.review_jd = st.session_state.last_job_description
        
        default_jd = st.session_state.get("last_job_description", "")
        review_job_description = st.text_area("2. Job Description", value=default_jd, height=300, key="review_jd")
        
        review_btn = st.button("🔍 Analyze Match", type="primary", use_container_width=True)

    with review_col_2:
        st.subheader("Analysis Result")

        if review_btn:
            if not st.session_state.api_key:
                st.error("❌ Missing API Key in Settings.")
            elif not active_cv_text or not review_job_description:
                st.error("❌ Missing Resume or JD (Upload new or Generate first).")
            else:
                with st.spinner("Reviewing match..."):
                    prov_key_norm = "Gemini" if st.session_state.provider == "Google Gemini" else "OpenAI"
                    result = utils.generate_resume_review(
                        active_cv_text,
                        review_job_description,
                        st.session_state.api_key,
                        prov_key_norm,
                        selected_model_name
                    )

                    if result["ok"]:
                        st.session_state.resume_review_result = result
                        
                        # Update Usage (Once per generation)
                        u_clean = st.session_state.session_usage
                        new_u = result.get("usage", {})
                        u_clean['tokens'] += new_u.get("total_tokens", 0)
                        u_clean['chars'] += new_u.get("input_chars", 0) + new_u.get("output_chars", 0)
                        
                        st.success("✅ Review complete!")
                    else:
                        st.error(f"Failed: {result['error']}")

        # Persistent Review Display
        if st.session_state.resume_review_result:
            result = st.session_state.resume_review_result
            st.metric("Match Score", f"{result['score']}%", result["level"])
            if result.get("summary"):
                st.info(result["summary"])

            if result.get("strengths"):
                with st.expander("✅ Strengths"):
                    for item in result["strengths"]:
                        st.write(f"- {item}")

            if result.get("gaps"):
                with st.expander("⚠️ Gaps"):
                    for item in result["gaps"]:
                        st.write(f"- {item}")

            if result.get("suggestions"):
                with st.expander("🛠️ Suggestions"):
                    for item in result["suggestions"]:
                        st.write(f"- {item}")

            # Update Usage (Already done during generation, just display)

# ==========================
# TAB: INTERVIEW COACH (NEW)
# ==========================
with tab_coach:
    st.header("🎥 AI Interview Coach (Powered by Gemini 3)")
    st.markdown("Upload a practice video. Gemini 3 Pro will analyze your **micro-expressions, eye contact, and answer content** against the JD.")
    
    # Check Provider
    if st.session_state.provider != "Google Gemini":
        st.warning("⚠️ This feature requires **Google Gemini**. Please switch Provider in Settings.")
    else:
        coach_col_1, coach_col_2 = st.columns([1, 1])
        
        with coach_col_1:
            st.subheader("1. Setup")
            # Reuse JD
            jd_context = st.session_state.last_job_description
            if not jd_context:
                jd_context = st.text_area("Paste Job Description (or use Generator tab first)", height=150)
            else:
                st.info("✅ Using Job Description from Generator tab.")
                with st.expander("View JD"):
                    st.write(jd_context)
            
            # --- Mock Interview Logic ---
            st.divider()
            
            # State Check: Are we in an interview?
            queue = st.session_state.get("questions_queue", [])
            idx = st.session_state.get("current_q_index", 0)
            
            # 1. Start Button (If no queue or finished)
            if not queue:
                if st.button("🎲 Start Mock Interview (3 Questions)", type="primary"):
                    if not st.session_state.api_key:
                        st.error("Missing API Key")
                    elif not jd_context:
                        st.error("Missing JD")
                    else:
                        with st.spinner("Designing your interview loop..."):
                            q_list = utils.generate_interview_questions_3_step(jd_context, st.session_state.api_key)
                            st.session_state.questions_queue = q_list
                            st.session_state.current_q_index = 0
                            # Clear previous context
                            st.session_state.current_question = q_list[0]
                            st.session_state.recorded_video_path = None
                            st.rerun()
                            
            # 2. Active Interview Interface
            else:
                # Progress
                progress = (idx + 1) / len(queue)
                st.progress(progress, text=f"Question {idx + 1} of {len(queue)}")
                
                # Navigation (Reset / Next)
                nav_col1, nav_col2 = st.columns([1, 4])
                with nav_col1:
                    if st.button("⏹ Quit", help="Stop Interview"):
                        st.session_state.questions_queue = []
                        st.session_state.current_q_index = 0
                        st.rerun()
                
                # Display Current Question
                current_q = queue[idx]
                st.session_state.current_question = current_q
                
                # --- AI Voice Interviewer ---
                voice_col1, voice_col2 = st.columns([4, 1])
                with voice_col1:
                     st.info(f"**🎤 Please Answer:**\n\n### {current_q}")
                with voice_col2:
                    auto_play = st.checkbox("🔊 Voice", value=True, help="Read question aloud")
                
                if auto_play:
                    # Simple caching: only generate if we haven't already for this specific question
                    # OR just generate (gTTS is reasonably fast for one sentence)
                    # To prevent re-running on every interaction, we could cache, but Streamlit reruns might be okay.
                    # Let's try direct generation first. 
                    audio_data = utils.text_to_speech(current_q)
                    if audio_data:
                        st.audio(audio_data, format="audio/mp3", start_time=0)
                # ----------------------------
                
                st.subheader("2. Upload/Record Answer")
            
            # --- Live Recorder (Shared) ---
            with st.expander("🔴 Live Recording (Advanced)", expanded=True):
                st.write("Real-time Face Mesh Tracking active.")
                ctx = webrtc_streamer(
                    key="interview-recorder",
                    mode=WebRtcMode.SENDRECV,
                    rtc_configuration={
                        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
                    },
                    video_transformer_factory=recorder_utils.FaceMeshProcessor,
                    async_processing=True,
                    video_html_attrs={
                        "style": {"width": "100%"},
                        "muted": True,  # Fix: Mute local playback to prevent echo
                        "autoPlay": True,
                        "playsInline": True
                    }
                )
                
                if ctx.video_transformer:
                    # Recording Controls
                    if not ctx.video_transformer.record:
                        if st.button("Start Recording"):
                            ctx.video_transformer.start_recording()
                            st.experimental_rerun()
                    else:
                        st.error("🔴 Recording in progress...")
                        if st.button("Stop Recording"):
                            saved_path = ctx.video_transformer.stop_recording()
                            st.session_state.recorded_video_path = saved_path
                            st.success(f"Saved to {saved_path}")
                            st.experimental_rerun()
                            
            # --- File Uploader ---
            st.divider()
            uploaded_video = st.file_uploader("Or Upload MP4/MOV", type=["mp4", "mov", "avi"])

            # Determine which video to use
            final_video = None
            if uploaded_video:
                final_video = uploaded_video
            elif st.session_state.get("recorded_video_path") and os.path.exists(st.session_state.recorded_video_path):
                st.info("Using Live Recorded Video.")
                # We need to open it as a file object for the utils function
                # But utils expects a UploadedFile (BytesIO) or we create a wrapper?
                # utils.analyze_interview_video calls upload_video_to_gemini which reads .getbuffer()
                # Local file doesn't have .getbuffer(). We need to adapt utils or read file.
                pass 
                
            analyze_video_btn = st.button("🎬 Analyze Performance", type="primary")

        with coach_col_2:
            st.subheader("3. Analysis Report")
            
            if analyze_video_btn:
                if not st.session_state.api_key:
                    st.error("❌ Missing API Key.")
                elif not jd_context:
                    st.error("❌ Missing Job Description.")
                else:
                    target_video = None
                    # Handle File Source
                    if uploaded_video:
                        target_video = uploaded_video
                    elif st.session_state.get("recorded_video_path"):
                        # Read local file into BytesIO to mimic UploadedFile
                        with open(st.session_state.recorded_video_path, "rb") as f:
                            target_video = BytesIO(f.read())
                    
                    if not target_video:
                        st.error("❌ No Video Source (Upload or Record).")
                    else:
                        with st.spinner("Gemini 3 Pro is watching your video (this make take ~10-20s)..."):
                            # Call Backend
                            res = utils.analyze_interview_video(
                                target_video, 
                                jd_context, 
                                st.session_state.api_key, 
                                selected_model_name,
                                question_context=st.session_state.current_question
                            )
                            
                            if res["ok"]:
                                data = res["data"]
                                
                                # Score
                                st.metric("Interview Score", f"{data.get('score', 0)}/100")
                                st.write(f"**Summary**: {data.get('summary', '')}")
                                
                                st.divider()
                                st.subheader("⏱️ Timeline Analysis")
                                
                                # Timeline
                                timeline = data.get("timeline", [])
                                if not timeline:
                                    st.write("No specific timestamp events detected.")
                                else:
                                    for event in timeline:
                                        t_time = event.get("timestamp", "00:00")
                                        t_type = event.get("type", "General")
                                        t_obs = event.get("observation", "")
                                        
                                        icon = "ℹ️"
                                        if "Visual" in t_type: icon = "👁️"
                                        elif "Audio" in t_type: icon = "🔊"
                                        elif "Content" in t_type: icon = "📝"
                                        
                                        st.markdown(f"**`[{t_time}]` {icon} {t_type}**: {t_obs}")
                                
                                st.divider()
                                with st.expander("💡 Improvement Advice", expanded=True):
                                    for tip in data.get("advice", []):
                                        st.write(f"- {tip}")
                                        
                                    # --- Next Question Logic ---
                                    if st.session_state.get("questions_queue"):
                                        st.divider()
                                        q_idx = st.session_state.current_q_index
                                        q_len = len(st.session_state.questions_queue)
                                        
                                        if q_idx < q_len - 1:
                                            # Next
                                            if st.button("➡️ Next Question", type="primary", key="btn_next_q"):
                                                st.session_state.current_q_index += 1
                                                st.session_state.recorded_video_path = None
                                                st.rerun()
                                        else:
                                            # Finish
                                            if st.button("🎉 Finish Interview", type="primary", key="btn_finish_int"):
                                                st.session_state.questions_queue = []
                                                st.session_state.current_q_index = 0
                                                st.session_state.recorded_video_path = None
                                                st.success("All questions completed!")
                                                st.balloons()
                                                time.sleep(2)
                                                st.rerun()
                                    
                            else:
                                st.error(f"Analysis Failed: {res['error']}")
