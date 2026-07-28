GCP Sidebar Submenu v1.12

Fix:
- Forces Guest Letters to white using both:
  color: #ffffff
  -webkit-text-fill-color: #ffffff
- Adds selectors scoped to Streamlit's sidebar.
- Keeps all module visibility flags.

Replace:
components/sidebar.py
