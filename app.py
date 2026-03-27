import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="B2B Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .kpi-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
        border-radius: 12px;
        padding: 20px 24px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        margin-bottom: 10px;
    }
    .kpi-label {
        font-size: 12px;
        font-weight: 500;
        opacity: 0.85;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 30px;
        font-weight: 700;
        line-height: 1;
    }
    .section-header {
        font-size: 17px;
        font-weight: 700;
        color: #1e3a5f;
        border-left: 4px solid #2d6a9f;
        padding-left: 12px;
        margin: 28px 0 14px 0;
    }
    .insight-box {
        background: #f0f6ff;
        border: 1px solid #c3d9f7;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 10px;
        color: #1e3a5f;
        line-height: 1.6;
    }
    .insight-box strong { color: #2d6a9f; }
    .workflow-box {
        background: #f8fffe;
        border: 1px solid #b2dfdb;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 10px;
        color: #1a3c34;
        line-height: 1.65;
    }
    .workflow-box strong { color: #00796b; }
    .stApp { background-color: #f8fafc; }
</style>
""", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("B2B_Leads_Dataset_1000Records.xlsx")
    df["Converted"] = (df["Status"] == "Converted").astype(int)
    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔎 Filters")
    st.markdown("Use these to drill into specific segments.")
    st.markdown("---")

    sel_region = st.multiselect(
        "Region",
        options=sorted(df["Region"].unique()),
        default=sorted(df["Region"].unique()),
    )
    sel_industry = st.multiselect(
        "Industry",
        options=sorted(df["Industry"].unique()),
        default=sorted(df["Industry"].unique()),
    )
    sel_source = st.multiselect(
        "Lead Source",
        options=sorted(df["Lead_Source"].unique()),
        default=sorted(df["Lead_Source"].unique()),
    )

    st.markdown("---")
    st.caption("Applied Programming Tools for B2B Business · End Term Project")

# Apply filters
filtered = df[
    df["Region"].isin(sel_region) &
    df["Industry"].isin(sel_industry) &
    df["Lead_Source"].isin(sel_source)
]

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📊 Analytics Dashboard",
    "⚙️ Make.com Automation (Part B)",
    "💡 Business Insights (Part D)",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ANALYTICS DASHBOARD (Part C)
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("## 📊 B2B Sales Analytics Dashboard")
    st.markdown(
        f"Showing **{len(filtered):,}** of **{len(df):,}** total leads based on current filters."
    )
    st.markdown("---")

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    total     = len(filtered)
    converted = filtered["Converted"].sum()
    conv_rate = (converted / total * 100) if total else 0
    avg_fu    = filtered["Follow_Up_Time"].mean() if total else 0
    total_rev = filtered["Revenue"].sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Total Leads</div>
            <div class="kpi-value">{total:,}</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Converted Leads</div>
            <div class="kpi-value">{converted:,}</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Conversion Rate</div>
            <div class="kpi-value">{conv_rate:.1f}%</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Avg Follow-Up Time</div>
            <div class="kpi-value">{avg_fu:.1f}h</div>
        </div>""", unsafe_allow_html=True)
    with k5:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Total Revenue</div>
            <div class="kpi-value">${total_rev/1e6:.2f}M</div>
        </div>""", unsafe_allow_html=True)

    # ── Row 1: Region & Industry ───────────────────────────────────────────────
    st.markdown('<div class="section-header">📍 Regional & Industry Analysis</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        region_df = (
            filtered.groupby("Region")
            .agg(Total=("Lead_ID", "count"), Converted=("Converted", "sum"))
            .reset_index()
        )
        region_df["Not Converted"] = region_df["Total"] - region_df["Converted"]
        region_df = region_df.sort_values("Total", ascending=False)

        fig1 = px.bar(
            region_df, x="Region", y=["Converted", "Not Converted"],
            title="Leads by Region",
            color_discrete_map={"Converted": "#2d6a9f", "Not Converted": "#b0c4de"},
            barmode="stack", template="plotly_white",
        )
        fig1.update_layout(legend_title="Status", title_font_size=14)
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        ind_df = (
            filtered.groupby("Industry")
            .agg(Total=("Lead_ID", "count"), Converted=("Converted", "sum"))
            .reset_index()
        )
        ind_df["Conversion Rate (%)"] = (
            ind_df["Converted"] / ind_df["Total"] * 100
        ).round(1)
        ind_df = ind_df.sort_values("Conversion Rate (%)", ascending=True)

        fig2 = px.bar(
            ind_df, x="Conversion Rate (%)", y="Industry",
            orientation="h",
            title="Conversion Rate by Industry (%)",
            color="Conversion Rate (%)",
            color_continuous_scale="Blues",
            template="plotly_white",
            text="Conversion Rate (%)",
        )
        fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig2.update_layout(coloraxis_showscale=False, title_font_size=14)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Row 2: Revenue & Lead Source ───────────────────────────────────────────
    st.markdown('<div class="section-header">💰 Revenue & Lead Source Analysis</div>',
                unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        rev_df = (
            filtered.groupby("Industry")["Revenue"]
            .sum().reset_index()
            .sort_values("Revenue", ascending=False)
        )
        rev_df["Revenue ($K)"] = (rev_df["Revenue"] / 1000).round(1)

        fig3 = px.line(
            rev_df, x="Industry", y="Revenue ($K)",
            title="Revenue by Industry ($K)",
            markers=True, template="plotly_white",
            color_discrete_sequence=["#2d6a9f"],
        )
        fig3.update_traces(line_width=3, marker_size=8)
        fig3.update_layout(title_font_size=14)
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        src_df = (
            filtered.groupby("Lead_Source")
            .agg(Total=("Lead_ID", "count"), Converted=("Converted", "sum"))
            .reset_index()
        )
        src_df["Conv Rate (%)"] = (src_df["Converted"] / src_df["Total"] * 100).round(1)

        fig4 = px.scatter(
            src_df, x="Total", y="Conv Rate (%)",
            size="Total", color="Lead_Source",
            title="Lead Source: Volume vs Conversion Rate",
            labels={"Total": "Total Leads", "Conv Rate (%)": "Conversion Rate (%)"},
            template="plotly_white", size_max=50, text="Lead_Source",
        )
        fig4.update_traces(textposition="top center")
        fig4.update_layout(showlegend=False, title_font_size=14)
        st.plotly_chart(fig4, use_container_width=True)

    # ── Row 3: Follow-Up Time ──────────────────────────────────────────────────
    st.markdown('<div class="section-header">⏱️ Follow-Up Time vs Conversion</div>',
                unsafe_allow_html=True)
    c5, c6 = st.columns(2)

    with c5:
        bins   = pd.cut(
            filtered["Follow_Up_Time"],
            bins=[0, 12, 24, 48, 72, 96],
            labels=["0–12h", "12–24h", "24–48h", "48–72h", "72–96h"],
        )
        ft_df = (
            filtered.groupby(bins, observed=True)
            .agg(Total=("Lead_ID", "count"), Converted=("Converted", "sum"))
            .reset_index()
        )
        ft_df.columns = ["Time Bucket", "Total", "Converted"]
        ft_df["Conv Rate (%)"] = (ft_df["Converted"] / ft_df["Total"] * 100).round(1)

        fig5 = px.bar(
            ft_df, x="Time Bucket", y="Conv Rate (%)",
            title="Conversion Rate by Follow-Up Time Window",
            color="Conv Rate (%)", color_continuous_scale="Blues",
            template="plotly_white", text="Conv Rate (%)",
        )
        fig5.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig5.update_layout(coloraxis_showscale=False, title_font_size=14)
        st.plotly_chart(fig5, use_container_width=True)

    with c6:
        fig6 = px.box(
            filtered, x="Status", y="Follow_Up_Time",
            color="Status",
            title="Follow-Up Time Distribution by Status",
            color_discrete_map={
                "Converted": "#2d6a9f",
                "Not Converted": "#b0c4de",
            },
            template="plotly_white",
        )
        fig6.update_layout(showlegend=False, title_font_size=14)
        st.plotly_chart(fig6, use_container_width=True)

    # ── Raw Data ───────────────────────────────────────────────────────────────
    with st.expander("🗂️ View Raw Data (Filtered)"):
        st.dataframe(
            filtered.style.format({
                "Revenue": "${:,.2f}",
                "Follow_Up_Time": "{:.1f}h",
            }),
            use_container_width=True,
            height=300,
        )
        st.download_button(
            "⬇️ Download Filtered Data as CSV",
            data=filtered.to_csv(index=False),
            file_name="filtered_leads.csv",
            mime="text/csv",
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — MAKE.COM AUTOMATION (Part B)
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## ⚙️ Make.com Automation Workflow (Part B)")
    st.markdown(
        "This tab documents the automated lead management workflow built on Make.com."
    )
    st.markdown("---")

    st.markdown('<div class="section-header">🔁 Workflow Overview</div>',
                unsafe_allow_html=True)

    steps = [
        ("🟢 Trigger — Google Form Submission",
         "A prospect fills out the lead capture Google Form. Make.com watches the form "
         "in real time and fires the workflow the moment a new response is submitted. "
         "No manual checking required — it's instant and automatic."),
        ("📋 Action 1 — Store in Google Sheets",
         "The lead's details (name, company, industry, region, contact) are automatically "
         "appended as a new row in the master Google Sheets leads tracker. This replaces "
         "all manual copy-pasting and ensures every lead is instantly logged with a timestamp."),
        ("📧 Action 2 — Confirmation Email to Lead",
         "A personalised Gmail is sent to the lead within seconds of submission. "
         "It acknowledges their enquiry and sets expectations "
         "('We'll reach out within 24 hours'). This builds trust immediately."),
        ("🔔 Action 3 — Alert Sales Team",
         "A second email (or Slack message) is sent to the internal sales team with "
         "the full lead details. The assigned rep is notified immediately so they can "
         "follow up before a competitor does."),
    ]

    for title, description in steps:
        st.markdown(f"""<div class="workflow-box">
            <strong>{title}</strong><br>{description}
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">📐 How to Build This on Make.com</div>',
                unsafe_allow_html=True)

    instructions = [
        "Go to **make.com** → create a free account",
        "Click **'Create a new scenario'**",
        "Add first module → search **Google Forms** → select **'Watch responses'** → connect your Google account and select your lead form",
        "Click **+** → add **Google Sheets** → **'Add a Row'** → map each form field to the correct spreadsheet column",
        "Click **+** → add **Gmail** → **'Send an Email'** → compose your confirmation message to the lead (use the lead's email from the form)",
        "Click **+** → add another **Gmail** (or Slack) → **'Send an Email'** → compose the internal sales team alert with all lead details",
        "Click **'Run once'** to test with a dummy form submission and verify all 3 actions fire correctly",
        "Take screenshots of each module — these are your submission proof",
        "Click the toggle to turn the scenario **ON** for live operation",
    ]

    for i, step in enumerate(instructions, 1):
        st.markdown(f"**Step {i}.** {step}")

    st.markdown('<div class="section-header">✅ Business Benefits</div>',
                unsafe_allow_html=True)

    benefits = [
        ("⚡ Speed",
         "Lead receives a confirmation in seconds, not hours. Research shows leads "
         "contacted within 5 minutes are 9× more likely to convert."),
        ("🔄 Consistency",
         "No leads are ever missed or forgotten. Every single form submission "
         "triggers the same reliable sequence automatically."),
        ("💸 Cost Reduction",
         "Eliminates manual data entry and follow-up coordination — saving "
         "approximately 2–3 hours per day for the sales team."),
        ("📁 Auditability",
         "Every lead is logged in Google Sheets with a timestamp, creating a "
         "complete, searchable record ready for dashboard analysis."),
    ]

    b1, b2 = st.columns(2)
    for i, (title, text) in enumerate(benefits):
        col = b1 if i % 2 == 0 else b2
        with col:
            st.markdown(f"""<div class="insight-box">
                <strong>{title}</strong><br>{text}
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — BUSINESS INSIGHTS (Part D)
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## 💡 Business Insights & Recommendations (Part D)")
    st.markdown(
        "These insights are computed dynamically from your filtered dataset."
    )
    st.markdown("---")

    # Compute answers dynamically
    best_region = (
        filtered.groupby("Region")
        .apply(lambda x: x["Converted"].sum() / len(x) * 100, include_groups=False)
        .idxmax()
    )
    best_region_rate = (
        filtered.groupby("Region")
        .apply(lambda x: x["Converted"].sum() / len(x) * 100, include_groups=False)
        .max()
    )

    src_conv = (
        filtered.groupby("Lead_Source")
        .apply(lambda x: x["Converted"].sum() / len(x) * 100, include_groups=False)
    )
    best_source      = src_conv.idxmax()
    best_source_rate = src_conv.max()
    worst_source     = src_conv.idxmin()

    avg_ft_conv    = filtered[filtered["Status"] == "Converted"]["Follow_Up_Time"].mean()
    avg_ft_notconv = filtered[filtered["Status"] == "Not Converted"]["Follow_Up_Time"].mean()
    ft_diff        = avg_ft_notconv - avg_ft_conv

    st.markdown('<div class="section-header">🔍 Q&A — Data-Driven Answers</div>',
                unsafe_allow_html=True)

    qa = [
        (
            "Q1 — Which region has the highest conversion rate?",
            f"<strong>{best_region}</strong> has the highest conversion rate at "
            f"<strong>{best_region_rate:.1f}%</strong>. Focus sales resources and "
            f"campaign budget here for maximum return on investment.",
        ),
        (
            "Q2 — Which lead source performs best?",
            f"<strong>{best_source}</strong> delivers the highest conversion rate "
            f"at <strong>{best_source_rate:.1f}%</strong>. This channel should receive "
            f"increased budget and attention. In contrast, <strong>{worst_source}</strong> "
            f"has the lowest conversion rate — worth reviewing or deprioritising.",
        ),
        (
            "Q3 — Is follow-up time affecting conversion?",
            f"Yes — strongly. Converted leads are followed up an average of "
            f"<strong>{avg_ft_conv:.1f} hours</strong> after capture, compared to "
            f"<strong>{avg_ft_notconv:.1f} hours</strong> for non-converted leads. "
            f"That is a difference of <strong>{ft_diff:.1f} hours</strong>. "
            f"Speed-to-lead is a key driver of conversion success.",
        ),
    ]

    for question, answer in qa:
        st.markdown(f"""<div class="insight-box">
            <strong>{question}</strong><br>{answer}
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">📌 Q4 — 3 Business Strategies to Improve Conversion</div>',
                unsafe_allow_html=True)

    strategies = [
        (
            "Strategy 1 — Speed-to-Lead Protocol",
            f"Implement a company rule requiring all new leads to receive a first response "
            f"within 12 hours. Use Make.com to send an automated acknowledgement email the "
            f"moment a form is submitted (already built in Part B). This directly addresses "
            f"the {ft_diff:.1f}-hour gap between converted and non-converted leads.",
        ),
        (
            "Strategy 2 — Channel Budget Reallocation",
            f"Shift 30% of the marketing budget away from low-converting sources "
            f"(such as {worst_source}) toward the best-performing channel "
            f"({best_source}, which converts at {best_source_rate:.1f}%). "
            f"Use A/B testing to continuously optimise messaging on the top channel.",
        ),
        (
            "Strategy 3 — Regional Playbook Replication",
            f"The {best_region} region converts at {best_region_rate:.1f}%. Study what "
            f"their sales team does differently — scripts, timing, pricing, follow-up "
            f"cadence — and document it as a structured playbook. Roll this playbook out "
            f"across underperforming regions with targeted training and incentives.",
        ),
    ]

    for title, text in strategies:
        st.markdown(f"""<div class="insight-box">
            <strong>📌 {title}</strong><br>{text}
        </div>""", unsafe_allow_html=True)

    # Summary metrics strip
    st.markdown('<div class="section-header">📊 Quick Summary Metrics</div>',
                unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Best Region",       best_region,       f"{best_region_rate:.1f}% conversion")
    m2.metric("Best Lead Source",  best_source,       f"{best_source_rate:.1f}% conversion")
    m3.metric("Avg Follow-Up (Converted)",    f"{avg_ft_conv:.1f}h")
    m4.metric("Avg Follow-Up (Not Converted)", f"{avg_ft_notconv:.1f}h",
              delta=f"-{ft_diff:.1f}h faster to convert", delta_color="inverse")
