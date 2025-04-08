import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Upload file
st.title("System Data Lineage Sankey Diagram")
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Dropdown filters
    st.sidebar.header("Filter Options")
    system_from = st.sidebar.multiselect("System From", df["System From"].unique())
    system_to = st.sidebar.multiselect("System To", df["System To"].unique())
    batch_job = st.sidebar.multiselect("Batch Job Name", df["Batch Job Name"].unique())
    tech = st.sidebar.multiselect("Technology", df["Technology"].unique())
    db_from = st.sidebar.multiselect("Database/Process From", df["Database/Process From"].unique())
    db_to = st.sidebar.multiselect("Database/Process To", df["Database/Process To"].unique())

    # Filter logic
    filtered_df = df.copy()
    if system_from:
        filtered_df = filtered_df[filtered_df["System From"].isin(system_from)]
    if system_to:
        filtered_df = filtered_df[filtered_df["System To"].isin(system_to)]
    if batch_job:
        filtered_df = filtered_df[filtered_df["Batch Job Name"].isin(batch_job)]
    if tech:
        filtered_df = filtered_df[filtered_df["Technology"].isin(tech)]
    if db_from:
        filtered_df = filtered_df[filtered_df["Database/Process From"].isin(db_from)]
    if db_to:
        filtered_df = filtered_df[filtered_df["Database/Process To"].isin(db_to)]

    if st.button("Submit"):
        if filtered_df.empty:
            st.warning("No data matches your filter selection.")
        else:
            # Build Sankey nodes and links
            labels = []
            for col in ["System From", "Database/Process From", "Batch Job Name", "Database/Process To", "System To"]:
                labels.extend(filtered_df[col].dropna().unique())
            labels = list(pd.unique(labels))

            def get_index(val):
                return labels.index(val)

            source = []
            target = []
            value = []

            for _, row in filtered_df.iterrows():
                path = [row["System From"], row["Database/Process From"], row["Batch Job Name"],
                        row["Database/Process To"], row["System To"]]
                for i in range(len(path)-1):
                    src = get_index(path[i])
                    tgt = get_index(path[i+1])
                    source.append(src)
                    target.append(tgt)
                    value.append(1)

            # Sankey Diagram
            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=labels
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=value
                ))])

            st.plotly_chart(fig, use_container_width=True)
