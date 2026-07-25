from __future__ import annotations

# Sustituye únicamente la función render_stay_filter por esta versión.
# Cambios:
# - Arrival Date y Departure Date alineados con los campos.
# - Sin columna izquierda para las etiquetas.
# - Load Guests centrado respecto a los date pickers.

# Reemplaza las dos filas por:

        st.markdown('<div class="date-group-label">Arrival Date</div>', unsafe_allow_html=True)
        arrival_from_col, arrival_to_col = st.columns([1,1], gap="small")
        with arrival_from_col:
            st.date_input("From", key="filter_arrival_from")
        with arrival_to_col:
            st.date_input("To", key="filter_arrival_to")

        st.markdown('<div class="date-group-label">Departure Date</div>', unsafe_allow_html=True)
        departure_from_col, departure_to_col = st.columns([1,1], gap="small")
        with departure_from_col:
            st.date_input("From", key="filter_departure_from")
        with departure_to_col:
            st.date_input("To", key="filter_departure_to")

        button_left, button_center, button_right = st.columns([1,0.42,1])
        with button_center:
            submitted = st.form_submit_button(
                "Load Guests",
                type="primary",
                use_container_width=True,
            )
