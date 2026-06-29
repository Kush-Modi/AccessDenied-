import streamlit as st
import requests
import time

# Page Configuration
st.set_page_config(
    page_title="Intelligent NBA Recruiter Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://127.0.0.1:8000"

st.title("🎯 Intelligent NBA Recruitment Platform")
st.markdown("---")

# Helper to fetch data
def fetch_from_api(endpoint: str):
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error connecting to backend API: {e}")
    return None

# Sidebar - Candidate Selector
st.sidebar.header("👤 Recruiter Workspace")
candidates_data = fetch_from_api("candidates")

if candidates_data:
    candidate_names = [c["name"] for c in candidates_data]
    selected_name = st.sidebar.selectbox("Select Candidate to Analyze", candidate_names)
    selected_candidate = next(c for c in candidates_data if c["name"] == selected_name)
    
    st.sidebar.markdown("### Candidate Details")
    st.sidebar.write(f"**Current Position:** {selected_candidate.get('current_position')}")
    st.sidebar.write(f"**Experience:** {selected_candidate.get('experience_years')} Years")
    st.sidebar.write(f"**Location:** {selected_candidate.get('location')}")
    st.sidebar.write(f"**Skills:** {', '.join(selected_candidate.get('skills', []))}")
    st.sidebar.text_area("Resume Summary", selected_candidate.get("resume_text", ""), height=100, disabled=True)
else:
    st.sidebar.warning("Could not load candidates. Ensure the FastAPI server is running on port 8000.")
    selected_candidate = None

# Main Layout
col_main, col_queue = st.columns([7, 5])

with col_main:
    st.header("🔍 Match Analysis & Human-In-The-Loop Gate")
    
    if selected_candidate:
        st.info(f"Ready to evaluate **{selected_candidate['name']}** against all open roles in Supabase.")
        
        # Analyze Button
        if st.button("🚀 Analyze Fit (Run Agent)", type="primary"):
            with st.spinner("Agent running ReAct loop: fetching profiles & calling semantic tools..."):
                try:
                    res = requests.post(
                        f"{API_BASE_URL}/analyze", 
                        json={"candidate_id": selected_candidate["id"]}
                    )
                    if res.status_code == 200:
                        st.session_state["analysis_res"] = res.json()
                        st.success("Analysis complete! Awaiting approval decision.")
                    else:
                        st.error("Failed to analyze candidate.")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Display Decision Card if analysis exists
        if "analysis_res" in st.session_state:
            data = st.session_state["analysis_res"]
            
            # Display Live Execution Logs
            session_id = data.get("session_id")
            if session_id:
                log_data = fetch_from_api(f"logs/{session_id}")
                if log_data and log_data.get("logs"):
                    st.markdown("### 🖥️ Live Agent Execution Logs")
                    st.code("\n".join(log_data["logs"]), language="bash")
            
            st.markdown("### 📋 Evaluation Decision Card")
            st.json({
                "Status": data.get("status"),
                "Session ID": data.get("session_id"),
                "Match Target Job": data.get("recommendation", {}).get("job_title", "None"),
                "Client Company": data.get("recommendation", {}).get("client_name", "None"),
                "Confidence Score": data.get("confidence", 0.0)
            })
            
            if data.get("status") == "awaiting_approval" or data.get("status") == "already_evaluated":
                st.subheader("💡 Match Reasoning")
                st.text_area("Detailed Evaluation", data.get("reasoning"), height=250, disabled=True)
                
                # Approve & Reject Actions (Only if awaiting approval)
                if data.get("status") == "awaiting_approval":
                    col_app, col_rej = st.columns(2)
                    
                    with col_app:
                        if st.button("✅ Approve Pitch", use_container_width=True, type="primary"):
                            with st.spinner("Logging approved action..."):
                                res = requests.post(
                                    f"{API_BASE_URL}/hitl/respond",
                                    json={"session_id": data["session_id"], "decision": "approved"}
                                )
                                if res.status_code == 200:
                                    st.success("Recommendation approved! Added to Next Best Actions queue.")
                                    del st.session_state["analysis_res"]
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Failed to approve.")
                                    
                    with col_rej:
                        if st.button("❌ Reject Pitch", use_container_width=True):
                            with st.spinner("Logging rejection decision..."):
                                res = requests.post(
                                    f"{API_BASE_URL}/hitl/respond",
                                    json={"session_id": data["session_id"], "decision": "rejected"}
                                )
                                if res.status_code == 200:
                                    st.warning("Recommendation rejected. Logs saved to database.")
                                    del st.session_state["analysis_res"]
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Failed to reject.")
                elif data.get("status") == "already_evaluated":
                    st.success(f"Decision state loaded: Placement suggestion has already been **{data.get('nba_status', '').upper()}**.")
                    if st.button("Clear Results"):
                        del st.session_state["analysis_res"]
                        st.rerun()
            else:
                st.warning("No matching open roles found for this candidate. Approval gate bypassed.")
                if st.button("Clear Results"):
                    del st.session_state["analysis_res"]
                    st.rerun()

with col_queue:
    st.header("📈 Next Best Actions Feed")
    st.markdown("Ranked queue of approved placement recommendations:")
    
    nba_data = fetch_from_api("nba/queue")
    
    if nba_data and nba_data.get("actions"):
        for index, item in enumerate(nba_data["actions"]):
            action = item.get("action", {})
            st.info(
                f"**#{index+1} Pitch Candidate to Client**\n\n"
                f"*   **Candidate:** {item.get('candidate_name', 'N/A')}\n"
                f"*   **Client:** {action.get('client_name')}\n"
                f"*   **Target Job:** {action.get('job_title')}\n"
                f"*   **Confidence Rating:** {item.get('confidence', 0.0):.0%}\n\n"
                f"**Evaluation Reasoning:**\n"
                f"{item.get('reasoning')}"
            )
    else:
        st.write("No approved recommendations in the queue yet. Analyze and approve a match to populate the queue.")
