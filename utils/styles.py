import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp{
            background:#f5f6f8;

            --gcp-primary:#343A50;
            --gcp-primary-hover:#414862;
            --gcp-primary-active:#2C3145;
            --gcp-accent:rgb(0,104,140);
        }

        [data-testid="stHeader"]{
            background:transparent;
        }

        .block-container{
            max-width:1800px;
            padding-top:1.1rem;
            padding-bottom:2rem;
        }

        /* ===========================
           HEADER
        =========================== */

        .top-header{
            display:flex;
            justify-content:space-between;
            align-items:center;
            background:#fff;
            border:1px solid #e5e7eb;
            border-radius:14px;
            padding:18px 22px;
            margin-bottom:22px;
        }

        .top-header h1{
            font-size:22px;
            margin:0;
            color:#111827;
        }

        .top-header p{
            font-size:13px;
            color:#6b7280;
            margin:3px 0 0;
        }

        .hotel-name{
            font-weight:650;
            color:#111827;
        }

        /* ===========================
           PANELS
        =========================== */

        .summary-card,
        .document-card{
            position:relative;
            background:#fff;
            border:1px solid #d9dde5;
            border-radius:12px;
            padding:30px 20px 22px 20px;
            margin-bottom:26px;
            overflow:hidden;
            box-shadow:0 2px 8px rgba(0,0,0,.04);
        }

        .summary-card::before,
        .document-card::before{
            content:"";
            position:absolute;
            left:0;
            top:0;
            width:100%;
            height:5px;
            background:rgb(22,21,19);
        }

        .panel-title{
            font-size:17px;
            font-weight:700;
            color:#111827;
            margin-bottom:24px;
        }

        .muted{
            color:#6b7280;
            font-size:12px;
        }

        /* ===========================
           GUEST CARDS
        =========================== */

        .guest-card{
            border:1px solid #e5e7eb;
            border-radius:11px;
            padding:12px;
            margin-bottom:8px;
            background:#fff;
        }

        .guest-card-selected{
            border-color:#bfdbfe;
            background:#eff6ff;
        }

        .guest-name{
            font-weight:700;
            font-size:14px;
            color:#111827;
        }

        .guest-meta{
            color:#6b7280;
            font-size:12px;
            margin-top:3px;
        }

        /* ===========================
           STATUS
        =========================== */

        .status-badge{
            display:inline-block;
            border-radius:999px;
            padding:3px 9px;
            font-size:11px;
            font-weight:700;
            margin-top:7px;
        }

        .status-ready,
        .status-sent{
            background:#ecfdf5;
            color:#047857;
        }

        .status-generated{
            background:#eff6ff;
            color:#1d4ed8;
        }

        .status-reviewed{
            background:#fff7ed;
            color:#c2410c;
        }

        .status-error{
            background:#fef2f2;
            color:#b91c1c;
        }

        /* ===========================
           SUMMARY
        =========================== */

        .summary-title{
            font-size:18px;
            font-weight:750;
            color:#111827;
            margin-bottom:4px;
        }

        .summary-subtitle{
            color:#6b7280;
            font-size:13px;
            margin-bottom:18px;
        }

        .mini-grid{
            display:grid;
            grid-template-columns:repeat(4,minmax(0,1fr));
            gap:14px;
        }

        .mini-card{
            border:1px solid #e5e7eb;
            border-radius:10px;
            padding:15px;
            background:#fafafa;
        }

        .mini-label{
            font-size:11px;
            color:#6b7280;
            margin-bottom:6px;
        }

        .mini-value{
            font-size:14px;
            font-weight:700;
            color:#111827;
        }

        /* ===========================
           DOCUMENT
        =========================== */

        .document-row{
            display:grid;
            grid-template-columns:130px 1fr;
            gap:14px;
            margin:10px 0;
            font-size:13px;
        }

        .document-row span:first-child{
            color:#6b7280;
        }

        .document-row span:last-child{
            color:#111827;
            font-weight:650;
        }

        /* ===========================
           PREVIEW
        =========================== */

        .preview-box{
            background:#f9fafb;
            border:1px dashed #d1d5db;
            border-radius:12px;
            padding:20px;
            min-height:230px;
            margin-top:18px;
        }

        .paper{
            background:#fff;
            border:1px solid #e5e7eb;
            box-shadow:0 7px 20px rgba(17,24,39,.08);
            max-width:570px;
            margin:0 auto;
            padding:30px 38px;
            min-height:160px;
            font-size:13px;
            line-height:1.55;
            color:#374151;
        }

        /* ===========================
           HISTORY
        =========================== */

        .history-item{
            border-left:2px solid #dbeafe;
            padding:0 0 12px 12px;
            margin-left:4px;
        }

        .history-time{
            font-size:11px;
            color:#9ca3af;
        }

        .history-message{
            font-size:13px;
            color:#374151;
        }

        /* ===========================
   ALL BUTTONS
=========================== */

div[data-testid="stButton"] button,
div[data-testid="stDownloadButton"] button{

    width:100%;
    min-height:42px;

    border:none !important;
    border-radius:10px;

    background:var(--gcp-primary) !important;
    color:#ffffff !important;

    font-weight:650;

    box-shadow:0 3px 10px rgba(52,58,80,.22);

    transition:all .20s ease;
}

/* Hover */

div[data-testid="stButton"] button:hover,
div[data-testid="stDownloadButton"] button:hover{

    background:var(--gcp-primary-hover) !important;
    color:#ffffff !important;

    transform:translateY(-1px);

    box-shadow:0 6px 18px rgba(52,58,80,.30);
}

/* Click */

div[data-testid="stButton"] button:active,
div[data-testid="stDownloadButton"] button:active{

    background:var(--gcp-primary-active) !important;
}

/* Focus */

div[data-testid="stButton"] button:focus,
div[data-testid="stDownloadButton"] button:focus{

    box-shadow:
        0 0 0 3px rgba(52,58,80,.25),
        0 6px 18px rgba(52,58,80,.20);
}
/* ==========================================================
   OPERA CLOUD SEARCH BAR
========================================================== */

div[data-testid="stForm"]{
    border:none !important;
    padding:0 !important;
    margin:0 0 18px 0 !important;
    background:transparent !important;
}

/* INPUT */

div[data-testid="stTextInput"]{
    width:100%;
    margin-bottom:0 !important;
}

div[data-testid="stTextInput"] input{

    height:38px;
    width:100%;
    border:1px solid #aeb4bc !important;
    border-radius:2px !important;

    background:white !important;

    font-size:13px;

    padding-left:36px !important;
    padding-right:14px !important;

    box-shadow:none !important;

}

/* Placeholder */

div[data-testid="stTextInput"] input::placeholder{

    color:#808692;
    opacity:1;

}

/* Focus */

div[data-testid="stTextInput"] input:focus{

    border-color:#3b82f6 !important;

    box-shadow:0 0 0 1px #3b82f6 !important;

}

/* Lupa */

div[data-testid="stTextInput"] > div{

    position:relative;

}

div[data-testid="stTextInput"] > div::before{

    content:"⌕";

    position:absolute;

    left:11px;

    top:50%;

    transform:translateY(-52%);

    font-size:18px;
    font-weight:600;
    line-height:1;

    color:#7b8190;

    z-index:10;

    pointer-events:none;

}

/* SEARCH BUTTON */

div[data-testid="stFormSubmitButton"] button{

    width:82px !important;
    min-width:82px !important;

    height:38px !important;
    min-height:38px !important;

    padding:0 16px !important;

    background:var(--gcp-primary) !important;
    color:#ffffff !important;

    border:1px solid var(--gcp-primary) !important;
    border-radius:2px !important;

    font-size:12px;
    font-weight:700;

    white-space:nowrap !important;

    box-shadow:none !important;
    transform:none !important;
}

div[data-testid="stFormSubmitButton"] button:hover{

    background:var(--gcp-primary-hover) !important;
    border-color:var(--gcp-primary-hover) !important;
    color:#ffffff !important;

    transform:none !important;
    box-shadow:none !important;
}


/* ==========================================================
   TABS - ACTIVE COLOR
========================================================== */

/* Override Streamlit theme color inside the application */
.stApp{
    --primary-color:rgb(0,104,140);
}

/* Normal tab */
[data-testid="stTabs"] button[role="tab"]{
    height:42px !important;
    padding:0 18px 0 0 !important;
    color:#6b7280 !important;
    font-size:13px !important;
    font-weight:600 !important;
    transition:color .20s ease !important;
}

/* Normal tab text */
[data-testid="stTabs"] button[role="tab"] p,
[data-testid="stTabs"] button[role="tab"] span,
[data-testid="stTabs"] button[role="tab"] div{
    color:inherit !important;
}

/* Hover */
[data-testid="stTabs"] button[role="tab"]:hover,
[data-testid="stTabs"] button[role="tab"]:hover *{
    color:rgb(0,104,140) !important;
}

/* Selected tab and all text inside it */
[data-testid="stTabs"] button[role="tab"][aria-selected="true"],
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] *{
    color:rgb(0,104,140) !important;
    font-weight:700 !important;
}

/* Streamlit/BaseWeb active underline */
[data-testid="stTabs"] div[data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{
    background-color:rgb(0,104,140) !important;
    background:rgb(0,104,140) !important;
    height:3px !important;
    border-radius:2px !important;
}

/* Fallback for Streamlit versions that draw the underline
   through a pseudo-element on the selected tab */
[data-testid="stTabs"] button[role="tab"][aria-selected="true"]::after{
    background:rgb(0,104,140) !important;
    border-color:rgb(0,104,140) !important;
}


/* ==========================================================
   MICROSOFT 365 WORD LAUNCHER
========================================================== */

.m365-launcher{
    max-width:620px;
    margin:18px auto;
    padding:26px 28px;
    background:#ffffff;
    border:1px solid #d8dde6;
    border-radius:12px;
    box-shadow:0 12px 34px rgba(31,41,55,.14);
    animation:m365FadeIn .25s ease-out;
}

.m365-brand-row{
    display:flex;
    align-items:center;
    gap:13px;
    padding-bottom:20px;
    border-bottom:1px solid #eceff3;
    margin-bottom:22px;
}

.m365-word-icon{
    width:42px;
    height:42px;
    border-radius:6px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#185abd;
    color:#ffffff;
    font-size:22px;
    font-weight:700;
    box-shadow:0 4px 12px rgba(24,90,189,.25);
}

.m365-brand{
    color:#242424;
    font-size:15px;
    font-weight:700;
}

.m365-product{
    color:#616161;
    font-size:12px;
    margin-top:2px;
}

.m365-launch-title{
    color:#242424;
    font-size:20px;
    font-weight:700;
    text-align:center;
    margin-top:8px;
}

.m365-launch-message{
    color:#616161;
    font-size:13px;
    text-align:center;
    margin:7px 0 22px;
}

.m365-progress-track{
    width:100%;
    height:6px;
    overflow:hidden;
    background:#e8e8e8;
    border-radius:999px;
}

.m365-progress-fill{
    height:100%;
    background:#185abd;
    border-radius:999px;
    transition:width .35s ease;
    position:relative;
}

.m365-progress-fill::after{
    content:"";
    position:absolute;
    inset:0;
    background:linear-gradient(
        90deg,
        transparent,
        rgba(255,255,255,.55),
        transparent
    );
    animation:m365Shimmer 1.1s infinite;
}

.m365-progress-value{
    color:#616161;
    font-size:11px;
    text-align:right;
    margin-top:6px;
}

.m365-step{
    font-size:12px;
    margin-top:8px;
}

.m365-step-complete{
    color:#107c10;
}

.m365-check{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    width:17px;
    height:17px;
    margin-right:7px;
    border-radius:50%;
    background:#107c10;
    color:#ffffff;
    font-size:11px;
    font-weight:800;
}

.m365-launch-detail{
    display:flex;
    align-items:center;
    justify-content:center;
    gap:9px;
    min-height:24px;
    color:#4f4f4f;
    font-size:12px;
    margin-top:18px;
}

.m365-spinner{
    width:16px;
    height:16px;
    border:2px solid #d6e4f7;
    border-top-color:#185abd;
    border-radius:50%;
    animation:m365Spin .8s linear infinite;
}

.m365-launcher-success{
    text-align:center;
}

.m365-success-icon{
    width:48px;
    height:48px;
    margin:2px auto 15px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:50%;
    background:#e8f5e9;
    color:#107c10;
    font-size:25px;
    font-weight:800;
}

.m365-document-name{
    display:inline-block;
    margin-top:5px;
    padding:8px 12px;
    border-radius:6px;
    background:#f3f6fa;
    color:#3b3b3b;
    font-size:12px;
    font-weight:650;
}

.word-opened-meta{
    margin:-4px 0 14px;
    color:#6b7280;
    font-size:11px;
}

.word-opened-meta span{
    color:#107c10;
    font-weight:800;
    margin-right:4px;
}

@keyframes m365Spin{
    to{transform:rotate(360deg);}
}

@keyframes m365FadeIn{
    from{
        opacity:0;
        transform:translateY(5px);
    }
    to{
        opacity:1;
        transform:translateY(0);
    }
}

@keyframes m365Shimmer{
    from{transform:translateX(-100%);}
    to{transform:translateX(100%);}
}



/* ==========================================================
   STAY DATE FILTER
========================================================== */

.stay-filter-heading{
    display:flex;
    justify-content:space-between;
    align-items:center;
    background:#ffffff;
    border:1px solid #d9dde5;
    border-bottom:none;
    border-radius:12px 12px 0 0;
    padding:18px 20px 10px;
    margin-top:2px;
}

.stay-filter-title{
    color:#111827;
    font-size:16px;
    font-weight:750;
}

.stay-filter-subtitle{
    color:#6b7280;
    font-size:12px;
    margin-top:3px;
}

.filter-active-label{
    min-height:42px;
    display:flex;
    align-items:center;
    justify-content:flex-end;
    color:#6b7280;
    font-size:12px;
    font-weight:650;
}

.date-group-label{
    min-height:70px;
    display:flex;
    align-items:center;
    color:#111827;
    font-size:13px;
    font-weight:700;
    padding-top:17px;
}

/* The Streamlit form directly below the filter heading. */
.stay-filter-heading + div [data-testid="stForm"]{
    background:#ffffff !important;
    border:1px solid #d9dde5 !important;
    border-top:none !important;
    border-radius:0 0 12px 12px !important;
    padding:4px 20px 18px !important;
    margin:0 0 22px !important;
}

/* Date controls */
div[data-testid="stDateInput"] label{
    color:#6b7280 !important;
    font-size:12px !important;
    font-weight:600 !important;
}

div[data-testid="stDateInput"] input{
    background:#ffffff !important;
    border-color:#aeb4bc !important;
    border-radius:3px !important;
    color:#111827 !important;
}

@media (max-width:900px){
    .filter-active-label{
        justify-content:flex-start;
    }

    .date-group-label{
        min-height:auto;
        padding-top:8px;
    }
}

        /* ===========================
           EMPTY WORKSPACE
        =========================== */

        .empty-workspace-card{
            background:#ffffff;
            border:1px solid #d9dde5;
            border-radius:12px;
            padding:52px 28px;
            margin-bottom:26px;
            text-align:center;
            box-shadow:0 2px 8px rgba(0,0,0,.04);
        }

        .empty-workspace-secondary{
            padding:30px 28px;
        }

        .empty-workspace-icon{
            width:54px;
            height:54px;
            margin:0 auto 16px;
            display:flex;
            align-items:center;
            justify-content:center;
            border-radius:50%;
            background:rgba(0,104,140,.10);
            color:rgb(0,104,140);
            font-size:25px;
            font-weight:700;
        }

        .empty-workspace-title{
            color:#111827;
            font-size:20px;
            font-weight:750;
            margin-bottom:8px;
        }

        .empty-workspace-text,
        .empty-workspace-placeholder{
            max-width:590px;
            margin:0 auto;
            color:#6b7280;
            font-size:13px;
            line-height:1.6;
        }

        .empty-workspace-section-title{
            color:#111827;
            font-size:16px;
            font-weight:700;
            margin-bottom:10px;
        }

        

/* ==========================================================
   FINAL BUTTON ALIGNMENT AND CONSISTENT RADIUS
========================================================== */

/* Bring date labels closer to their date controls. */
.date-group-label{
    min-height:44px !important;
    padding-top:9px !important;
    justify-content:flex-start !important;
}

/* Compact spacing in the Stay Date Filter rows. */
.stay-filter-heading + div [data-testid="stForm"] [data-testid="stHorizontalBlock"]{
    gap:0.70rem !important;
}

.stay-filter-heading + div [data-testid="stForm"]{
    padding:2px 18px 14px !important;
}

/* Search and Load Guests use the same corner radius. */
div[data-testid="stFormSubmitButton"] button{
    border-radius:6px !important;
}

/* Keep the Guest Search button compact. */
div[data-testid="stForm"]:not(:has(div[data-testid="stDateInput"]))
div[data-testid="stFormSubmitButton"] button{
    width:96px !important;
    min-width:96px !important;
    max-width:96px !important;
    padding:0 14px !important;
    border-radius:6px !important;
}

/* Give Load Guests its own width and prevent clipping. */
div[data-testid="stForm"]:has(div[data-testid="stDateInput"])
div[data-testid="stFormSubmitButton"]{
    width:100% !important;
    display:flex !important;
    justify-content:center !important;
}

div[data-testid="stForm"]:has(div[data-testid="stDateInput"])
div[data-testid="stFormSubmitButton"] button{
    width:100% !important;
    min-width:145px !important;
    max-width:none !important;
    height:38px !important;
    min-height:38px !important;
    padding:0 18px !important;
    white-space:nowrap !important;
    overflow:visible !important;
    border-radius:6px !important;
}

/* All primary action buttons share the same radius. */
div[data-testid="stButton"] button,
div[data-testid="stDownloadButton"] button{
    border-radius:6px !important;
}

        

/* ==========================================================
   GCP GUIDED WORKFLOW
========================================================== */

div[data-testid="stVerticalBlockBorderWrapper"]:has(.workflow-card-marker){
    position:relative;
    background:#ffffff !important;
    border:1px solid #d9dde5 !important;
    border-radius:12px !important;
    padding:28px 20px 22px !important;
    margin-bottom:26px !important;
    overflow:hidden !important;
    box-shadow:0 2px 8px rgba(0,0,0,.04) !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.workflow-card-marker)::before{
    content:"";
    position:absolute;
    top:0;
    left:0;
    right:0;
    height:5px;
    background:rgb(22,21,19);
}

.workflow-card-marker,
.word-action-marker{
    display:none;
}

.workflow-title{
    margin-bottom:18px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.workflow-card-marker)
div[data-testid="stButton"],
div[data-testid="stVerticalBlockBorderWrapper"]:has(.workflow-card-marker)
div[data-testid="stDownloadButton"]{
    margin-bottom:10px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.workflow-card-marker)
div[data-testid="stButton"] button,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.workflow-card-marker)
div[data-testid="stDownloadButton"] button{
    width:100% !important;
    min-height:42px !important;
    border-radius:6px !important;
    justify-content:center !important;
    white-space:nowrap !important;
}

/* Custom Microsoft Word icon for the Word action. */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.word-action-marker)
button::before{
    content:"W";
    display:inline-flex;
    align-items:center;
    justify-content:center;
    width:22px;
    height:22px;
    margin-right:8px;
    border-radius:4px;
    background:#185abd;
    color:#ffffff;
    font-size:13px;
    font-weight:800;
    box-shadow:inset -5px 0 0 rgba(255,255,255,.10);
}

.m365-word-logo{
    width:42px;
    height:42px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:6px;
    background:#185abd;
    color:#ffffff;
    font-size:22px;
    font-weight:800;
    box-shadow:inset -8px 0 0 rgba(255,255,255,.10),
               0 4px 12px rgba(24,90,189,.25);
}

.workflow-status-title{
    color:#111827;
    font-size:14px;
    font-weight:700;
    margin-bottom:10px;
}

@media (max-width:900px){
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.workflow-card-marker){
        padding:24px 14px 18px !important;
    }
}

        

/* ==========================================================
   OPERA CLOUD INSPIRED HEADER + SIDEBAR - FIXED
========================================================== */

[data-testid="stHeader"]{
    display:none !important;
}

[data-testid="stMainBlockContainer"]{
    padding-top:0 !important;
}

.block-container{
    max-width:100% !important;
    padding:8px 16px 2rem !important;
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"]{
    background:#ffffff !important;
}

/* One continuous header bar */
.gcp-header{
    position:relative;
    width:100%;
    height:44px;
    box-sizing:border-box;
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:0 16px 0 66px;
    margin:0 0 14px;
    background:#30364c;
    color:#ffffff;
    overflow:hidden;
}

.gcp-header-left,
.gcp-header-right,
.gcp-user{
    display:flex;
    align-items:center;
}

.gcp-header-left{gap:8px; min-width:0;}
.gcp-header-right{gap:17px; margin-left:auto;}
.gcp-user{gap:12px;}

.gcp-brand{
    color:#ffffff;
    font-size:28px;
    font-weight:700;
    line-height:1;
    letter-spacing:.7px;
    white-space:nowrap;
}

.gcp-divider{
    width:1px;
    height:20px;
    background:rgba(255,255,255,.35);
}

.gcp-product-name{
    color:#ffffff;
    font-size:16px;
    white-space:nowrap;
}

.gcp-date-time{text-align:right; line-height:1.15; white-space:nowrap;}
.gcp-date{color:#ffffff; font-size:12px; font-weight:600;}
.gcp-time{color:#d9dce6; font-size:12px; margin-top:2px;}

.gcp-avatar{
    width:28px;
    height:28px;
    border-radius:6px;
    background:#69728f;
    color:#ffffff;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:12px;
    font-weight:600;
}

.gcp-user-info{line-height:1.12; white-space:nowrap;}
.gcp-hotel,.gcp-username{color:#ffffff; font-size:12px; font-weight:600;}

/* Burger floats over the continuous header */
div[data-testid="stButton"] button[title="Show or hide navigation"],
div[data-testid="stButton"] button[aria-label="Show or hide navigation"]{
    position:absolute !important;
    top:8px !important;
    left:16px !important;
    z-index:1002 !important;
    width:50px !important;
    min-width:50px !important;
    height:44px !important;
    min-height:44px !important;
    padding:0 !important;
    border:0 !important;
    border-radius:0 !important;
    background:#3c425a !important;
    color:#ffffff !important;
    box-shadow:none !important;
    font-size:22px !important;
}

div[data-testid="stButton"] button[title="Show or hide navigation"]:hover,
div[data-testid="stButton"] button[aria-label="Show or hide navigation"]:hover{
    background:#4a516b !important;
    transform:none !important;
}

.gcp-sidebar-open,.gcp-sidebar-closed{display:none;}

/* Native Streamlit sidebar restyled as OPERA navigation */
[data-testid="stSidebar"]{
    width:250px !important;
    min-width:250px !important;
    background:#3c425a !important;
    border-right:1px solid rgba(0,0,0,.22) !important;
    transition:width .22s ease, min-width .22s ease, transform .22s ease !important;
    overflow:hidden !important;
}

[data-testid="stSidebar"] > div:first-child{
    width:250px !important;
    background:#3c425a !important;
    padding-top:12px !important;
}

[data-testid="stSidebarContent"]{
    background:#3c425a !important;
    padding:10px 0 24px !important;
}

[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"]{
    display:none !important;
}

/* Our burger controls this state. */
body:has(.gcp-sidebar-closed) [data-testid="stSidebar"]{
    width:0 !important;
    min-width:0 !important;
    transform:translateX(-250px) !important;
    border-right:0 !important;
}

body:has(.gcp-sidebar-closed) [data-testid="stSidebar"] > div:first-child{
    width:250px !important;
}

.gcp-sidebar-root{display:none;}

.gcp-sidebar-brand{
    display:flex;
    align-items:center;
    gap:10px;
    padding:4px 14px 14px;
    color:#ffffff;
}

.gcp-sidebar-brand-icon{
    width:34px;
    height:34px;
    border-radius:7px;
    background:#ffffff;
    color:#3c425a;
    display:flex;
    align-items:center;
    justify-content:center;
    font-weight:800;
}

.gcp-sidebar-brand-title{font-size:14px; font-weight:700;}
.gcp-sidebar-brand-subtitle{color:#cfd3df; font-size:10px; margin-top:2px;}

.gcp-sidebar-search{
    height:34px;
    margin:0 12px 14px;
    padding:0 10px;
    display:flex;
    align-items:center;
    gap:8px;
    background:#ffffff;
    color:#7b8190;
    border-radius:3px;
    font-size:12px;
}

.gcp-sidebar-section-label{
    color:#f2cf62;
    font-size:10px;
    font-weight:700;
    padding:7px 14px 5px;
    letter-spacing:.4px;
}

.gcp-sidebar-section-spaced{margin-top:10px;}
.gcp-sidebar-divider{height:1px; background:rgba(255,255,255,.12); margin:14px 0 10px;}

[data-testid="stSidebar"] div[data-testid="stButton"]{margin:0 !important;}
[data-testid="stSidebar"] div[data-testid="stButton"] button{
    min-height:42px !important;
    width:100% !important;
    border-radius:0 !important;
    justify-content:flex-start !important;
    padding:0 14px !important;
    background:#3c425a !important;
    color:#e5e7ef !important;
    box-shadow:none !important;
    border-top:1px solid rgba(255,255,255,.04) !important;
    border-bottom:1px solid rgba(0,0,0,.10) !important;
    font-size:12px !important;
    font-weight:600 !important;
}

[data-testid="stSidebar"] div[data-testid="stButton"] button:hover{
    background:#4a516b !important;
    color:#ffffff !important;
    transform:none !important;
}

[data-testid="stSidebar"] div[data-testid="stElementContainer"]:has(.sidebar-nav-marker.active)
+ div[data-testid="stElementContainer"] button{
    background:#515973 !important;
    color:#ffffff !important;
    box-shadow:inset 4px 0 0 #f2cf62 !important;
}
.sidebar-nav-marker{display:none;}

/* Restore clear borders on all date picker controls. */
div[data-testid="stDateInput"] [data-baseweb="input"],
div[data-testid="stDateInput"] > div > div{
    background:#ffffff !important;
    border:1px solid #aeb4bc !important;
    border-radius:4px !important;
    box-shadow:none !important;
}

div[data-testid="stDateInput"] [data-baseweb="input"]:focus-within,
div[data-testid="stDateInput"] > div > div:focus-within{
    border-color:#3b82f6 !important;
    box-shadow:0 0 0 1px #3b82f6 !important;
}

div[data-testid="stDateInput"] input{
    border:0 !important;
    background:transparent !important;
    color:#111827 !important;
}

@media (max-width:900px){
    .gcp-product-name,.gcp-hotel,.gcp-time{display:none;}
    .gcp-header{padding-left:62px; padding-right:10px;}
    [data-testid="stSidebar"]{
        position:fixed !important;
        z-index:1001 !important;
        height:100vh !important;
    }
}


/* ==========================================================
   GCP UI POLISH v2.0
   Compact top alignment for header, sidebar and workspace.
========================================================== */

/* Remove Streamlit's residual top spacing from the main canvas. */
[data-testid="stMainBlockContainer"],
.block-container{
    padding-top:0 !important;
    margin-top:0 !important;
}

.block-container{
    padding-left:16px !important;
    padding-right:16px !important;
    padding-bottom:1.5rem !important;
}

/* The toggle button is absolutely positioned, but its Streamlit wrapper
   otherwise remains in document flow and creates the large blank band. */
div[data-testid="stElementContainer"]:has(
    button[title="Show or hide navigation"]
),
div[data-testid="stElementContainer"]:has(
    button[aria-label="Show or hide navigation"]
){
    position:absolute !important;
    inset:0 auto auto 0 !important;
    width:0 !important;
    height:0 !important;
    min-height:0 !important;
    margin:0 !important;
    padding:0 !important;
    overflow:visible !important;
    z-index:1003 !important;
}

/* Align the toggle exactly with the header bar. */
div[data-testid="stButton"] button[title="Show or hide navigation"],
div[data-testid="stButton"] button[aria-label="Show or hide navigation"]{
    top:0 !important;
    left:16px !important;
    width:50px !important;
    min-width:50px !important;
    height:46px !important;
    min-height:46px !important;
}

/* Compact enterprise header. */
.gcp-header{
    height:46px !important;
    min-height:46px !important;
    margin:0 0 10px !important;
    padding-left:66px !important;
    border-radius:0 !important;
}

.gcp-brand{
    font-size:27px !important;
}

/* Start native sidebar content at the same top edge as the header. */
[data-testid="stSidebar"] > div:first-child{
    padding-top:0 !important;
}

[data-testid="stSidebarContent"]{
    padding-top:0 !important;
}

/* Remove the small synthetic spacer used when branding/search are hidden. */
[data-testid="stSidebar"] .gcp-sidebar-root + div:has(> div[style*="height:10px"]),
[data-testid="stSidebar"] div[style*="height:10px"]{
    height:0 !important;
    min-height:0 !important;
    margin:0 !important;
    padding:0 !important;
}

/* Keep the first section visually aligned and compact. */
.gcp-sidebar-section-label{
    padding-top:8px !important;
}

/* Reduce unnecessary vertical gaps immediately below the header. */
.gcp-header + div,
.gcp-header + [data-testid="stElementContainer"]{
    margin-top:0 !important;
}

.stay-filter-heading{
    margin-top:0 !important;
}

@media (max-width:900px){
    .block-container{
        padding-left:10px !important;
        padding-right:10px !important;
    }

    div[data-testid="stButton"] button[title="Show or hide navigation"],
    div[data-testid="stButton"] button[aria-label="Show or hide navigation"]{
        left:10px !important;
    }

    .gcp-header{
        padding-left:62px !important;
        margin-bottom:8px !important;
    }
}


        </style>
        """,
        unsafe_allow_html=True,
    )
