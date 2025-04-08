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
        # Create dropdown options based on uploaded data
        system_from_options = df["System From"].dropna().unique()
        
        # User selects 'System From' first
        system_from = st.selectbox("System From", system_from_options)

        # Filter data based on selected 'System From'
        filtered_df = df[df["System From"] == system_from]

        batch_job_options = filtered_df["Batch Job Name"].dropna().unique()
        technology_options = filtered_df["Technology"].dropna().unique()
        system_to_options = filtered_df["System To"].dropna().unique()
        db_from_options = filtered_df["Database/Process From"].dropna().unique()
        db_to_options = filtered_df["Database/Process To"].dropna().unique()

        # Two-column layout
        col1, col2 = st.columns(2)

        with col1:
            batch_job = st.selectbox("Batch Job Name", batch_job_options)
            db_from = st.selectbox("Database/Process From", db_from_options)

        with col2:
            technology = st.selectbox("Technology", technology_options)
            system_to = st.selectbox("System To", system_to_options)
            db_to = st.selectbox("Database/Process To", db_to_options)

        if st.button("Submit"):
            # Apply filters
            filtered_df = filtered_df[
                (filtered_df["System To"] == system_to) &
                (filtered_df["Batch Job Name"] == batch_job) &
                (filtered_df["Technology"] == technology) &
                (filtered_df["Database/Process From"] == db_from) &
                (filtered_df["Database/Process To"] == db_to)
            ]

            if not filtered_df.empty:
                # Define nodes (System From → Technology → System To)
                unique_nodes = pd.unique(filtered_df[['System From', 'Technology', 'System To']].values.ravel())
                node_indices = {node: i for i, node in enumerate(unique_nodes)}

                # Create Sankey links and colors
                sankey_links = []
                link_colors = []

                # Define a color for each technology to identify each line
                color_map = {tech: f'rgba({i*40 % 255}, {i*80 % 255}, {i*120 % 255}, 0.6)' for i, tech in enumerate(filtered_df["Technology"].unique())}

                for _, row in filtered_df.iterrows():
                    source_idx = node_indices[row["System From"]]
                    tech_idx = node_indices[row["Technology"]]
                    target_idx = node_indices[row["System To"]]

                    # Create links from System From to Technology and from Technology to System To
                    sankey_links.append({"source": source_idx, "target": tech_idx, "value": 5})  # Stronger weight
                    sankey_links.append({"source": tech_idx, "target": target_idx, "value": 5})

                    # Add a direct link from System From to System To (direct connection)
                    sankey_links.append({"source": source_idx, "target": target_idx, "value": 5})  # Direct link

                    # Color the links based on the technology
                    link_colors.extend([color_map[row["Technology"]]] * 3)  # Add color for each link

                # Extract source, target, and value for Plotly
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
