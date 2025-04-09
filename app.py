# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import hashlib
import random

st.set_page_config(page_title="DEB-DW Data Lineage Viewer", layout="wide")
st.title("System Data Lineage Visualization")

# Upload Excel file
uploaded_file = st.file_uploader("Upload the Excel file", type=["xlsx"])

# Color helper
def string_to_color(s):
    random.seed(int(hashlib.md5(s.encode()).hexdigest(), 16))
    return f"rgba({random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)}, 0.8)"

if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
        df = xls.parse("DEB-DW")
        df.columns = df.columns.str.strip()  # Strip whitespace from column names

        df = df.dropna(subset=["System From", "System To"])

        # Create dropdown options safely
        def get_column_options(col_name):
            if col_name in df.columns:
                return sorted(df[col_name].dropna().unique())
            else:
                st.warning(f"⚠️ Column '{col_name}' is missing in the uploaded file.")
                return []

        system_from_options = get_column_options("System From")
        system_to_options = get_column_options("System To")
        batch_job_options = get_column_options("Batch Job Name")
        tech_options = get_column_options("Technology")
        db_from_options = get_column_options("Database/Process From")
        db_to_options = get_column_options("Database/Process To")

        with st.form("filter_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                # Changed from multiselect to selectbox for System From
                system_from = st.selectbox("System From", system_from_options)
                tech = st.multiselect("Technology", tech_options)
            with col2:
                system_to = st.multiselect("System To", system_to_options)
                db_from = st.multiselect("Database/Process From", db_from_options)
            with col3:
                batch_job = st.multiselect("Batch Job Name", batch_job_options)
                db_to = st.multiselect("Database/Process To", db_to_options)

            submitted = st.form_submit_button("Submit")

        if submitted:
            # Apply filters
            if system_from:
                df = df[df["System From"] == system_from]  # Ensure only one selection is applied
            if system_to:
                df = df[df["System To"].isin(system_to)]
            if tech:
                df = df[df["Technology"].isin(tech)]
            if batch_job:
                df = df[df["Batch Job Name"].isin(batch_job)]
            if db_from:
                df = df[df["Database/Process From"].isin(db_from)]
            if db_to:
                df = df[df["Database/Process To"].isin(db_to)]

            if df.empty:
                st.warning("⚠️ No data matches the selected filters.")
            else:
                edges = list(zip(df["System From"], df["System To"], df["Technology"]))
                nodes = sorted(set(df["System From"]).union(df["System To"]).union(df["Technology"]))
                node_indices = {name: i for i, name in enumerate(nodes)}

                # Prepare sources, targets, and values
                sources = []
                targets = []
                values = []
                colors = []
                
                # Create links for System From -> Technology -> System To
                for _, row in df.iterrows():
                    system_from_idx = node_indices[row["System From"]]
                    technology_idx = node_indices[row["Technology"]]
                    system_to_idx = node_indices[row["System To"]]

                    # Add links: System From -> Technology and Technology -> System To
                    sources.append(system_from_idx)
                    targets.append(technology_idx)
                    values.append(1)  # You can adjust this as needed for weight
                    colors.append(string_to_color(f"{row['System From']}->{row['Technology']}"))

                    sources.append(technology_idx)
                    targets.append(system_to_idx)
                    values.append(1)  # Adjust as needed
                    colors.append(string_to_color(f"{row['Technology']}->{row['System To']}"))

                # Create Sankey diagram
                fig = go.Figure(data=[go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=nodes,
                        color="lightblue"
                    ),
                    link=dict(
                        source=sources,
                        target=targets,
                        value=values,
                        color=colors
                    ))])

                fig.update_layout(title_text="Data Lineage Diagram", font_size=12)
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error reading 'DEB-DW' sheet: {e}")
