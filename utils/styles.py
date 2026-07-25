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

        </style>
        """,
        unsafe_allow_html=True,
    )
