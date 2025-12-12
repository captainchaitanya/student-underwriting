import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Navi Student Underwriting", layout="centered")

# --- HEADER ---
st.title("🎓 Future-Potential Underwriting Model")
st.markdown("A **proxy scoring engine** for NTC (New-to-Credit) Students based on employability signals.")
st.markdown("---")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Applicant Profile")

college_tier = st.sidebar.selectbox(
    "College Tier", 
    ["Tier 1 (IIT/NIT/BITS)", "Tier 2 (State Govt/Reputed)", "Tier 3 (Private/Other)"]
)

stream = st.sidebar.selectbox(
    "Stream / Major", 
    ["CS / IT / Circuital", "Core Engineering", "Commerce / Finance", "Arts / Humanities", "Medical"]
)

gpa = st.sidebar.slider("CGPA (Scale of 10)", 5.0, 10.0, 8.5)

internships = st.sidebar.number_input("Past Internships", 0, 5, 1)

backlogs = st.sidebar.radio("Active Backlogs?", ["No", "Yes"])

# --- THE SCORING ALGORITHM ---
def calculate_score(tier, stream, gpa, intern, backlog):
    score = 300 # Base CIBIL-like start
    breakdown = {}

    # 1. Tier Weight (Employability Signal)
    if "Tier 1" in tier: 
        score += 250
        breakdown['College Tier'] = 250
    elif "Tier 2" in tier: 
        score += 150
        breakdown['College Tier'] = 150
    else:
        score += 50
        breakdown['College Tier'] = 50
    
    # 2. Stream Weight (Salary Potential)
    if "CS" in stream or "Medical" in stream: 
        score += 100
        breakdown['Stream'] = 100
    elif "Core" in stream or "Commerce" in stream: 
        score += 70
        breakdown['Stream'] = 70
    else:
        score += 40
        breakdown['Stream'] = 40

    # 3. GPA Weight (Discipline Signal)
    gpa_score = int((gpa - 5) * 30) # Max 150 points
    score += gpa_score
    breakdown['GPA'] = gpa_score

    # 4. Internships (Job Readiness)
    intern_score = intern * 30
    score += intern_score
    breakdown['Experience'] = intern_score

    # 5. Risk Penalty
    if backlog == "Yes":
        score -= 100
        breakdown['Risk Penalty'] = -100
    
    # Cap Score at 900
    return min(score, 900), breakdown

final_score, score_breakdown = calculate_score(college_tier, stream, gpa, internships, backlogs)

# --- DASHBOARD UI ---

# 1. The Big Score Card
col1, col2 = st.columns([1, 2])

with col1:
    st.metric(label="Predicted Credit Score", value=final_score, delta=f"{final_score-300} points added")

with col2:
    if final_score >= 750:
        st.success("✅ **ELITE TIER APPROVED**")
        st.write("Eligible for: **₹45,000 Credit Limit** @ 1.2% Interest")
    elif final_score >= 600:
        st.warning("⚠️ **STANDARD TIER APPROVED**")
        st.write("Eligible for: **₹15,000 Credit Limit** @ 2.5% Interest")
    else:
        st.error("🛑 **REJECTED (High Risk)**")
        st.write("Reason: Project Earning Potential below risk threshold.")

# 2. Visual Breakdown (Plotly)
st.subheader("Why this score?")
st.write("Breakdown of factors contributing to the underwriting decision:")

# Create Waterfall Chart
fig = go.Figure(go.Waterfall(
    orientation = "v",
    measure = ["relative"] * len(score_breakdown),
    x = list(score_breakdown.keys()),
    textposition = "outside",
    text = list(score_breakdown.values()),
    y = list(score_breakdown.values()),
    connector = {"line":{"color":"rgb(63, 63, 63)"}},
))

fig.update_layout(title = "Score Composition", showlegend = False, height=400)
st.plotly_chart(fig, use_container_width=True)

# 3. Product Manager Logic (For the Interview)
with st.expander("ℹ️ View Underwriting Logic (Product Spec)"):
    st.write("""
    **Hypothesis:** Students with higher employability signals (Tier 1 + High GPA) have a 
    90% lower default rate on micro-credit products.
    
    **Weightage Logic:**
    - **College Tier (40%):** Strongest correlation with starting salary.
    - **GPA (20%):** Proxy for conscientiousness and discipline.
    - **Backlogs (-Negative):** High correlation with delayed employment.
    """)