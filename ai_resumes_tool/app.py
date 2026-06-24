# 


import streamlit as st
from openai import OpenAI
import os
import html
from dotenv import load_dotenv
from auth import register_user, login_user
from database import save_resume, get_user_resumes
from ats_analyzer import calculate_ats_score, get_ats_improvement_tips
from db_viewer import view_all_users, view_all_resumes, get_database_stats, delete_all_data

# Load environment variables
load_dotenv(override=True, dotenv_path=".env.local")
api_key = os.getenv("OPENAI_API_KEY")

# Page config
st.set_page_config(page_title="AI Resume Optimizer", layout="wide")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.admin = False

# Sidebar for authentication
st.sidebar.title("Authentication")

if not st.session_state.logged_in:
    auth_option = st.sidebar.radio("Choose Action", ["Login", "Sign Up"])
    
    if auth_option == "Login":
        st.sidebar.subheader("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        
        if st.sidebar.button("Login"):
            user_id, message = login_user(username, password)
            if user_id:
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.sidebar.success(message)
                st.rerun()
            else:
                st.sidebar.error(message)
    
    else:  # Sign Up
        st.sidebar.subheader("Sign Up")
        new_username = st.sidebar.text_input("Username", key="signup_username")
        new_email = st.sidebar.text_input("Email", key="signup_email")
        new_password = st.sidebar.text_input("Password", type="password", key="signup_password")
        confirm_password = st.sidebar.text_input("Confirm Password", type="password", key="confirm_password")
        
        if st.sidebar.button("Sign Up"):
            success, message = register_user(new_username, new_email, new_password, confirm_password)
            if success:
                st.sidebar.success(message)
                st.sidebar.info("Please login now")
            else:
                st.sidebar.error(message)
else:
    st.sidebar.write(f"👤 **{st.session_state.username}**")
    
    # Admin access
    if st.sidebar.checkbox("🔐 Admin Panel"):
        admin_password = st.sidebar.text_input("Admin Password", type="password")
        if admin_password == "admin123":  # Change this to your desired admin password
            st.sidebar.success("✅ Admin Access Granted")
            st.session_state.admin = True
        else:
            st.session_state.admin = False
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()

# Main app (only show if logged in)
if st.session_state.logged_in:
    st.title("🚀 AI Resume Optimizer")
    
    # Initialize session state for resume
    if "improved_resume" not in st.session_state:
        st.session_state.improved_resume = ""
    
    # Tabs for different sections
    tab1, tab2 = st.tabs(["📝 Improve Resume", "📚 My History"])
    
    with tab1:
        # Use columns for better layout
        col1, col2 = st.columns(2)
        
        with col1:
            resume = st.text_area("Paste Resume", height=300, key="resume_input")
        
        with col2:
            job_description = st.text_area("Paste Job Description", height=300, key="job_desc_input")
        
        if st.button("Improve Resume", type="primary"):
            if not resume or not job_description:
                st.error("Please fill in both Resume and Job Description fields")
            elif not api_key:
                st.error("API key not found. Check your .env.local file")
            else:
                with st.spinner("Optimizing your resume..."):
                    prompt = f"""You are an expert resume optimizer. Analyze the following resume against the job description and provide an improved version that better matches the job requirements.

RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

Provide an improved resume that:
1. Incorporates keywords from the job description
2. Highlights relevant skills and experience
3. Maintains professional formatting
4. Uses strong action verbs

Return only the improved resume without any extra commentary."""
                    
                    try:
                        client = OpenAI(api_key=api_key)
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are an expert resume optimizer and career coach."},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        st.session_state.improved_resume = response.choices[0].message.content
                        
                        # Save to database
                        save_resume(st.session_state.user_id, resume, st.session_state.improved_resume, job_description)
                        st.success("Resume improved and saved!")
                        
                    except Exception as e:
                        st.error(f"Error calling API: {str(e)}")
        
        if st.session_state.improved_resume:
            st.subheader("✨ Improved Resume:")
            
            # Add CSS styling for better appearance
            resume_html = html.escape(st.session_state.improved_resume).replace('\n', '<br>')
            st.markdown(f"""
            <style>
                .resume-container {{
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 10px;
                    border: 2px solid #2E86AB;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.8;
                    color: #1a1a1a;
                }}
                .resume-container h1, .resume-container h2, .resume-container h3 {{
                    color: #2E86AB;
                    margin-top: 15px;
                    margin-bottom: 10px;
                }}
                .resume-container h1 {{
                    font-size: 28px;
                    font-weight: 700;
                }}
                .resume-container h2 {{
                    font-size: 20px;
                    font-weight: 600;
                    border-bottom: 2px solid #2E86AB;
                    padding-bottom: 8px;
                }}
                .resume-container h3 {{
                    font-size: 16px;
                    font-weight: 600;
                }}
                .resume-container p, .resume-container li {{
                    font-size: 14px;
                    color: #2c2c2c;
                }}
                .resume-container ul {{
                    margin-left: 20px;
                }}
                .resume-container li {{
                    margin-bottom: 8px;
                }}
            </style>
            <div class="resume-container">
                {resume_html}
            </div>
            """, unsafe_allow_html=True)
            
            # Calculate ATS Score
            st.divider()
            st.subheader("🎯 ATS Score Analysis")
            
            ats_result = calculate_ats_score(st.session_state.improved_resume, job_description)
            
            # Display score in a nice format
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Overall Score", f"{ats_result['score']}/100")
            with col2:
                st.metric("Keywords", f"{ats_result['keyword_score']}/35")
            with col3:
                st.metric("Formatting", f"{ats_result['format_score']}/25")
            with col4:
                st.metric("Structure", f"{ats_result['structure_score']}/20")
            
            # Display feedback
            st.write("**Feedback:**")
            for feedback_item in ats_result['feedback']:
                st.write(feedback_item)
            
            # Show missing keywords
            if ats_result['missing_keywords']:
                st.write("**Keywords to Add:**")
                keywords_text = ", ".join(ats_result['missing_keywords'])
                st.info(f"Consider adding these keywords: {keywords_text}")
            
            # Show ATS tips
            with st.expander("💡 ATS Best Practices"):
                for tip in get_ats_improvement_tips():
                    st.write(tip)
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download Improved Resume",
                    data=st.session_state.improved_resume,
                    file_name="improved_resume.txt",
                    mime="text/plain"
                )
    
    with tab2:
        st.subheader("📋 Your Resume History")
        resumes = get_user_resumes(st.session_state.user_id)
        
        if resumes:
            for idx, (res_id, original, improved, job_desc, created_at) in enumerate(resumes, 1):
                # Calculate ATS score for this resume
                ats_result = calculate_ats_score(improved, job_desc)
                ats_score = ats_result['score']
                
                # Color code based on score
                if ats_score >= 75:
                    score_color = "🟢"
                elif ats_score >= 50:
                    score_color = "🟡"
                else:
                    score_color = "🔴"
                
                with st.expander(f"Resume #{idx} - {created_at} {score_color} ATS: {ats_score}/100"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Original Resume:**")
                        st.text(original[:500] + "..." if len(original) > 500 else original)
                    
                    with col2:
                        st.write("**Job Description:**")
                        st.text(job_desc[:500] + "..." if len(job_desc) > 500 else job_desc)
                    
                    st.write("**Improved Resume:**")
                    improved_html = html.escape(improved).replace('\n', '<br>')
                    st.markdown(f"""
                    <div style="background-color: #ffffff; padding: 20px; border-radius: 10px; border: 2px solid #2E86AB; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.8; color: #1a1a1a; font-size: 14px;">
                        {improved_html}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show ATS score details
                    st.write("**ATS Score Breakdown:**")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Overall", f"{ats_score}/100")
                    with col2:
                        st.metric("Keywords", f"{ats_result['keyword_score']}/35")
                    with col3:
                        st.metric("Format", f"{ats_result['format_score']}/25")
                    with col4:
                        st.metric("Structure", f"{ats_result['structure_score']}/20")
                    
                    st.download_button(
                        label=f"Download Resume #{idx}",
                        data=improved,
                        file_name=f"improved_resume_{res_id}.txt",
                        mime="text/plain",
                        key=f"download_{res_id}"
                    )
        else:
            st.info("No resumes yet. Start improving one!")
    
    # Admin Panel
    if "admin" in st.session_state and st.session_state.admin:
        st.divider()
        st.title("🔧 Admin Dashboard")
        
        admin_tabs = st.tabs(["📊 Statistics", "👥 Users", "📋 Resumes", "⚙️ Tools"])
        
        with admin_tabs[0]:
            st.subheader("Database Statistics")
            stats = get_database_stats()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Users", stats['users'])
            with col2:
                st.metric("Total Resumes", stats['resumes'])
            with col3:
                st.metric("Avg Resume Length", f"{stats['avg_length']} chars")
        
        with admin_tabs[1]:
            st.subheader("All Users")
            users = view_all_users()
            if users:
                st.dataframe(users, use_container_width=True, column_config={
                    0: st.column_config.NumberColumn("ID"),
                    1: st.column_config.TextColumn("Username"),
                    2: st.column_config.TextColumn("Email"),
                    3: st.column_config.TextColumn("Created At")
                })
            else:
                st.info("No users yet")
        
        with admin_tabs[2]:
            st.subheader("All Resumes")
            resumes_data = view_all_resumes()
            if resumes_data:
                for idx, (res_id, username, original, improved, job_desc, created_at) in enumerate(resumes_data, 1):
                    with st.expander(f"Resume #{idx} by {username} - {created_at}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Original:**")
                            st.text(original[:300] + "..." if len(original) > 300 else original)
                        
                        with col2:
                            st.write("**Job Description:**")
                            st.text(job_desc[:300] + "..." if len(job_desc) > 300 else job_desc)
                        
                        st.write("**Improved:**")
                        st.text_area(f"Improved #{idx}", value=improved, height=150, disabled=True, key=f"admin_improved_{res_id}")
            else:
                st.info("No resumes yet")
        
        with admin_tabs[3]:
            st.subheader("Database Tools")
            
            st.warning("⚠️ Dangerous operations below!")
            
            if st.button("🗑️ Delete All Data", key="delete_all"):
                if st.checkbox("I understand this will delete all users and resumes", key="confirm_delete"):
                    if delete_all_data():
                        st.success("✅ All data deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Error deleting data")
            
            st.divider()
            st.write("**Database Info:**")
            st.write(f"Database file: `resumes.db`")
            st.write(f"Location: `{os.path.join(os.getcwd(), 'resumes.db')}`")

else:
    st.title("🔐 Please Login to Continue")
    st.info("Sign up or login using the sidebar to access the AI Resume Optimizer")