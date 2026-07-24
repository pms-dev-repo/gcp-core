import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp{background:#f5f6f8}
        [data-testid="stHeader"]{background:transparent}
        .block-container{max-width:1800px;padding-top:1.1rem;padding-bottom:2rem}
        .top-header{display:flex;justify-content:space-between;align-items:center;background:#fff;border:1px solid #e5e7eb;border-radius:14px;padding:18px 22px;margin-bottom:18px}
        .top-header h1{font-size:22px;margin:0;color:#111827}
        .top-header p{font-size:13px;color:#6b7280;margin:3px 0 0}
        .hotel-name{font-weight:650;color:#111827}
        .panel-title{font-size:17px;font-weight:700;color:#111827;margin-bottom:4px}
        .muted{color:#6b7280;font-size:12px}
        .guest-card{border:1px solid #e5e7eb;border-radius:11px;padding:12px;margin-bottom:8px;background:#fff}
        .guest-card-selected{border-color:#bfdbfe;background:#eff6ff}
        .guest-name{font-weight:700;font-size:14px;color:#111827}
        .guest-meta{color:#6b7280;font-size:12px;margin-top:3px}
        .status-badge{display:inline-block;border-radius:999px;padding:3px 9px;font-size:11px;font-weight:700;margin-top:7px}
        .status-ready,.status-sent{background:#ecfdf5;color:#047857}
        .status-generated{background:#eff6ff;color:#1d4ed8}
        .status-reviewed{background:#fff7ed;color:#c2410c}
        .status-error{background:#fef2f2;color:#b91c1c}
        .summary-card,.document-card{border:1px solid #e5e7eb;border-radius:12px;padding:18px;background:#fff;margin-bottom:14px}
        .summary-title{font-size:18px;font-weight:750;color:#111827;margin-bottom:3px}
        .summary-subtitle{color:#6b7280;font-size:13px;margin-bottom:15px}
        .mini-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
        .mini-card{border:1px solid #e5e7eb;border-radius:10px;padding:13px;background:#fafafa}
        .mini-label{font-size:11px;color:#6b7280;margin-bottom:5px}
        .mini-value{font-size:14px;font-weight:700;color:#111827}
        .document-row{display:grid;grid-template-columns:130px 1fr;gap:12px;margin:7px 0;font-size:13px}
        .document-row span:first-child{color:#6b7280}
        .document-row span:last-child{color:#111827;font-weight:650}
        .preview-box{background:#f9fafb;border:1px dashed #d1d5db;border-radius:12px;padding:18px;min-height:230px;margin-top:14px}
        .paper{background:#fff;border:1px solid #e5e7eb;box-shadow:0 7px 20px rgba(17,24,39,.08);max-width:570px;margin:0 auto;padding:30px 38px;min-height:160px;font-size:13px;line-height:1.55;color:#374151}
        .history-item{border-left:2px solid #dbeafe;padding:0 0 12px 12px;margin-left:4px}
        .history-time{font-size:11px;color:#9ca3af}
        .history-message{font-size:13px;color:#374151}
        div[data-testid="stButton"] button,div[data-testid="stDownloadButton"] button{border-radius:9px;font-weight:650;width:100%}
        </style>
        """,
        unsafe_allow_html=True,
    )
