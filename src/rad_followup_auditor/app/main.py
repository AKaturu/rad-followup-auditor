from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from ..analysis import run_analysis
from ..config import (
    COL_CONFIDENCE,
    COL_HAS_EXPLICIT_RECOMMENDATION,
    COL_URGENCY,
)
from ..data import write_synthetic_csv
from ..report import generate_report

st.set_page_config(
    page_title="rad-followup-auditor",
    page_icon="📋",
    layout="wide",
)

st.title("rad-followup-auditor")
st.markdown(
    "Extract and track incidental finding follow-up recommendations "
    "from radiology reports."
)


def _display_analysis(analysis) -> None:
    stats = analysis.stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Reports", stats["total"])
    col2.metric(
        "With Recommendations",
        stats["with_recommendations"],
        f"{stats['recommendation_rate']}%",
    )
    col3.metric("Negated", stats["negated"], f"{stats['negation_rate']}%")
    col4.metric("Review Required", stats["review_required"])

    df = analysis.extracted
    if df.empty:
        return

    st.subheader("Summary")
    st.dataframe(analysis.summary, hide_index=True, use_container_width=True)

    st.subheader("Confidence Distribution")
    conf_counts = df[COL_CONFIDENCE].value_counts().reindex(
        ["high", "medium", "low"], fill_value=0
    )
    fig_conf = px.bar(
        x=conf_counts.index,
        y=conf_counts.values,
        color=conf_counts.index,
        color_discrete_map={"high": "#28a745", "medium": "#ffc107", "low": "#dc3545"},
        labels={"x": "Confidence", "y": "Count"},
    )
    fig_conf.update_layout(showlegend=False)
    st.plotly_chart(fig_conf, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        urg_counts = df[df[COL_HAS_EXPLICIT_RECOMMENDATION]][COL_URGENCY].value_counts()
        if not urg_counts.empty:
            fig_urg = px.pie(
                values=urg_counts.values,
                names=urg_counts.index,
                title="Urgency Distribution",
            )
            st.plotly_chart(fig_urg, use_container_width=True)

    with col_b:
        if COL_HAS_EXPLICIT_RECOMMENDATION in df.columns:
            has_rec = df[COL_HAS_EXPLICIT_RECOMMENDATION].value_counts()
            fig_rec = px.pie(
                values=has_rec.values,
                names=["No Recommendation", "Has Recommendation"],
                title="Recommendation Status",
                color_discrete_sequence=["#e2e3e5", "#28a745"],
            )
            st.plotly_chart(fig_rec, use_container_width=True)

    st.subheader("Extracted Recommendations")
    display_cols = [
        "report_id",
        "finding",
        "recommended_modality",
        "interval_value",
        "interval_unit",
        "urgency",
        "anatomic_region",
        "confidence",
        "review_required",
    ]
    display_df = df[display_cols].copy()
    display_df["interval_value"] = display_df["interval_value"].apply(
        lambda x: f"{x:.0f}" if pd.notna(x) else ""
    )
    st.dataframe(display_df, hide_index=True, use_container_width=True)

    st.download_button(
        "Download Full Results (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="extracted_results.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download Full Results (JSON)",
        data=df.to_json(orient="records", indent=2).encode("utf-8"),
        file_name="extracted_results.json",
        mime="application/json",
    )


tab_demo, tab_upload, tab_report = st.tabs(
    ["Demo Data", "Upload Reports", "Generate Report"]
)

with tab_demo:
    st.subheader("Synthetic Demo Reports")
    col1, col2, col3 = st.columns(3)
    with col1:
        n_reports = st.number_input("Number of reports", 10, 500, 100, key="demo_n")
    with col2:
        seed = st.number_input("Random seed", 0, 9999, 42, key="demo_seed")
    with col3:
        fup_rate = st.slider(
            "Follow-up rate", 0.0, 1.0, 0.55, key="demo_fup"
        )

    if st.button("Generate and Analyze Demo"):
        with st.spinner("Generating synthetic reports..."):
            csv_path = Path("outputs/demo/demo_reports.csv")
            csv_path.parent.mkdir(parents=True, exist_ok=True)
            write_synthetic_csv(
                csv_path, n=n_reports, seed=seed, followup_rate=fup_rate
            )
            analysis = run_analysis(csv_path)

        st.session_state["analysis"] = analysis
        st.success(f"Generated {n_reports} reports and ran extraction.")
        _display_analysis(analysis)

with tab_upload:
    st.subheader("Upload a CSV of Radiology Reports")
    st.markdown(
        "CSV must have columns: `report_id` (unique ID) and `report_text` "
        "(the radiology report text)."
    )

    uploaded = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded is not None:
        with st.spinner("Extracting follow-up recommendations..."):
            df = pd.read_csv(uploaded)
            if "report_id" not in df.columns:
                df["report_id"] = [f"R-{i+1:04d}" for i in range(len(df))]
            if "report_text" not in df.columns:
                st.error("CSV must contain a `report_text` column.")
                st.stop()
            tmp_csv = Path("outputs/uploaded/input.csv")
            tmp_csv.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(tmp_csv, index=False)
            analysis = run_analysis(tmp_csv)

        st.session_state["analysis"] = analysis
        st.success(f"Processed {len(df)} reports.")
        _display_analysis(analysis)

with tab_report:
    st.subheader("Generate Downloadable Report")
    if "analysis" not in st.session_state:
        st.info("First generate demo data or upload a CSV in the tabs above.")
        st.stop()

    analysis = st.session_state["analysis"]
    include_pdf = st.checkbox("Include PDF export", value=True)

    if st.button("Generate Report"):
        with st.spinner("Generating report..."):
            artifacts = generate_report(
                analysis,
                Path("outputs/report"),
                include_pdf=include_pdf,
            )

        with open(artifacts.html, "rb") as f:
            st.download_button(
                "Download HTML Report",
                data=f,
                file_name="rad_followup_auditor_report.html",
                mime="text/html",
            )

        if artifacts.pdf:
            with open(artifacts.pdf, "rb") as f:
                st.download_button(
                    "Download PDF Report",
                    data=f,
                    file_name="rad_followup_auditor_report.pdf",
                    mime="application/pdf",
                )

        st.success("Report generated successfully!")
