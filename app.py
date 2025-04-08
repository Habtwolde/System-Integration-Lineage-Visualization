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
    
    # Check if columns exist
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
            st.markdown("**System From**")  # Add label
            system_from = st.selectbox("Select System From", system_from_options)
            st.markdown("**Batch Job Name**")  # Add label
            batch_job = st.selectbox("Select Batch Job Name", batch_job_options)
            st.markdown("**Database/Process From**")  # Add label
            db_from = st.selectbox("Select Database/Process From", db_from_options)

        with col2:
            st.markdown("**System To**")  # Add label
            system_to = st.selectbox("Select System To", system_to_options)
            st.markdown("**Technology**")  # Add label
            technology = st.selectbox("Select Technology", technology_options)
            st.markdown("**Database/Process To**")  # Add label
            db_to = st.selectbox("Select Database/Process To", db_to_options)

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
                # Define nodes: Add Technology as a middle node
                unique_nodes = pd.unique(filtered_df[['System From', 'Technology', 'System To']].values.ravel())
                node_indices = {node: i for i, node in enumerate(unique_nodes)}

                # Add source and target indices based on the node mapping
                filtered_df['source_idx'] = filtered_df['System From'].map(node_indices)
                filtered_df['technology_idx'] = filtered_df['Technology'].map(node_indices)
                filtered_df['target_idx'] = filtered_df['System To'].map(node_indices)

                # Create Sankey links: Including links from System From -> Technology -> System To
                sankey_links = []
                for _, row in filtered_df.iterrows():
                    # Link from System From to Technology
                    sankey_links.append({"source": row['source_idx'], "target": row['technology_idx'], "value": 5})
                    # Link from Technology to System To
                    sankey_links.append({"source": row['technology_idx'], "target": row['target_idx'], "value": 5})

                # Define a color for each technology
                color_map = {tech: f'rgba({i*40 % 255}, {i*80 % 255}, {i*120 % 255}, 0.6)' for i, tech in enumerate(filtered_df["Technology"].unique())}

                # Assign colors to links based on the technology
                link_colors = [color_map[row["Technology"]] for _, row in filtered_df.iterrows() for _ in range(2)]

                # Extract source, target, value for Plotly
                sources = [link["source"] for link in sankey_links]
                targets = [link["target"] for link in sankey_links]
                values = [link["value"] for link in sankey_links]

                # Create the Sankey diagram
                fig = go.Figure(data=[go.Sankey(
                    node=dict(pad=15, thickness=20, label=list(unique_nodes)),
                    link=dict(source=sources, target=targets, value=values, color=link_colors)  # Add color to links
                )])

                fig.update_layout(title_text="System Integration Lineage", font_size=12)
                st.plotly_chart(fig)
            else:
                st.warning("No data found for the selected filters!")
