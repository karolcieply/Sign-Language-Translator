# components/admin_panel.py
import time

import pandas as pd
import streamlit as st

from frontend.models import UserRequest
from frontend.utils.api_interactions import api_get_users, api_update_user
st.title("Admin Panel")

st.markdown("### Welcome to the Admin Panel!")
st.write("This is the admin panel. Here you can manage users.")
if "users" not in st.session_state:
    st.session_state["users"] = api_get_users()
df = pd.DataFrame(st.session_state["users"])

edited_df = st.data_editor(
    df,
    column_config={"hashed_password": None},
    disabled=["id"],
    use_container_width=True,
    hide_index=True,
)

changes_mask = (edited_df != df).any(axis=1)
updated_df = edited_df.loc[changes_mask].copy()

if st.button("Save user changes", disabled=updated_df.empty):
    if api_update_user([UserRequest(**user) for user in updated_df.to_dict(orient="records")]):
        st.session_state["users"] = edited_df.to_dict(orient="records")
        st.success("Changes saved successfully!")
        time.sleep(2)
        st.rerun()
    else:
        st.error("Failed to save changes.")

