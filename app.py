import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load the Excel file
@st.cache_data
def load_data(file):
    df = pd.read_excel(file, engine="openpyxl")
    df.columns = df.columns.str.replace(r'\s+', ' ', regex=True).str.strip()  # Fix extra spaces
    return df

# Upload file
st.title("System Integration Lineage Visualization")
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)

    # Check if required columns exist
    required_columns = ["System From", "System To", "Batch Job Name", "Technology", "Database/Process From", "Database/Process To"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"Missing columns in uploaded file: {', '.join(missing_columns)}")
    else:
        # Create dropdown options
        system_from_options = df["System From"].dropna().unique()
        system_to_options = df["System To"].dropna().unique()
        batch_job_options = df["Batch Job Name"].dropna().unique()
        technology_options = df["Technology"].dropna().unique()
        db_from_options = df["Database/Process From"].dropna().unique()
        db_to_options = df["Database/Process To"].dropna().unique()

        # Two-column layout
        col1, col2 = st.columns(2)

        with col1:
            system_from = st.selectbox("System From", system_from_options)
            batch_job = st.selectbox("Batch Job Name", batch_job_options)
            db_from = st.selectbox("Database/Process From", db_from_options)

        with col2:
            system_to = st.selectbox("System To", system_to_options)
            technology = st.selectbox("Technology", technology_options)
            db_to = st.selectbox("Database/Process To", db_to_options)

        if st.button("Submit"):
            # Filter data based on selections
            filtered_df = df[
                (df["System From"] == system_from) &
                (df["System To"] == system_to) &
                (df["Batch Job Name"] == batch_job) &
                (df["Technology"] == technology) &
                (df["Database/Process From"] == db_from) &
                (df["Database/Process To"] == db_to)
            ]

            if not filtered_df.empty:
                # Create unique nodes
                nodes = list(pd.unique(filtered_df[['System From', 'Technology', 'System To']].values.ravel()))
                node_indices = {node: i for i, node in enumerate(nodes)}

                # Map source, technology, and target indices
                filtered_df['source_idx'] = filtered_df['System From'].map(node_indices)
                filtered_df['tech_idx'] = filtered_df['Technology'].map(node_indices)
                filtered_df['target_idx'] = filtered_df['System To'].map(node_indices)

                # Sankey links: "System From → Technology" and "Technology → System To"
                sankey_links_1 = filtered_df[['source_idx', 'tech_idx']]
                sankey_links_2 = filtered_df[['tech_idx', 'target_idx']]

                # Concatenate the links
                sankey_links = pd.concat([sankey_links_1, sankey_links_2]).reset_index(drop=True)
                sankey_links['value'] = 1  # Assign a default value for flow

                # Debugging Option: Display Node Mapping
                if st.checkbox("Show Debugging Info"):
                    st.write("Nodes:", nodes)
                    st.write("Node Indices:", node_indices)
                    st.write("Sankey Links:", sankey_links)

                # Create Sankey Diagram
                fig = go.Figure(data=[go.Sankey(
                    node=dict(
                        pad=15, thickness=20, label=nodes, color="blue"
                    ),
                    link=dict(
                        source=sankey_links.iloc[:, 0],  
                        target=sankey_links.iloc[:, 1],  
                        value=sankey_links['value']
                    )
                )])

                fig.update_layout(title_text="System Integration Lineage", font_size=12)
                st.plotly_chart(fig)
            else:
                st.warning("No data found for the selected filters!")
