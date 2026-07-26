GCP Administration Fix v1.8

This version replaces st.markdown(..., unsafe_allow_html=True) with st.html()
for the user detail card. It also builds the HTML without blank lines, which
prevents Streamlit's Markdown parser from displaying nested DIV tags as code.

Replace:
components/administration.py

Then fully stop and restart Streamlit:
Ctrl+C
streamlit run app.py

Requires Streamlit 1.50 or newer.
