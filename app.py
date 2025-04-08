import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Function to load the data
def load_data(uploaded_file):
    try:
        # Load the Excel file
        df = pd.read_excel(uploaded_file)
        
        # Normalize column names (remove leading/trailing spaces)
        df.columns = df.columns.str.strip()
        
        # Print the actual column names for debugging
        st.write("Actual columns in the uploaded file:", df.columns.tolist())
        
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# Streamlit UI to upload file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

# Ensure file is uploaded
if uploaded_file:
    df = load_data(uploaded_file)
    
    # Check if essential columns are present in the uploaded file
    required_columns = ["System From", "System To", "Batch Job Name", "Technology", "Database/Process From", "Database/Process To"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error("Required columns are missing. Please upload a valid file.")
    else:
        # Dropdown for filtering options
        st.subheader("Select Filters for Data Lineage")
        
        # Generate dropdown options based on the file data
        system_from_options = df["System From"].dropna().unique()
        system_to_options = df["System To"].dropna().unique()
        batch_job_options = df["Batch Job Name"].dropna().unique()
        technology_options = df["Technology"].dropna().unique()
        db_from_options = df["Database/Process From"].dropna().unique()
        db_to_options = df["Database/Process To"].dropna().unique()

        # Two columns for dropdowns layout
        col1, col2 = st.columns(2)
        
        with col1:
            system_from = st.selectbox("System From", system_from_options)
            batch_job_name = st.selectbox("Batch Job Name", batch_job_options)
            technology = st.selectbox("Technology", technology_options)
        
        with col2:
            system_to = st.selectbox("System To", system_to_options)
            db_from = st.selectbox("Database/Process From", db_from_options)
            db_to = st.selectbox("Database/Process To", db_to_options)
        
        # Submit button to generate the Sankey diagram
        if st.button("Submit"):
            # Filter the data based on the selected dropdown values
            filtered_df = df[
                (df["System From"] == system_from) & 
                (df["System To"] == system_to) & 
                (df["Batch Job Name"] == batch_job_name) &
                (df["Technology"] == technology) & 
                (df["Database/Process From"] == db_from) & 
                (df["Database/Process To"] == db_to)
            ]
            
            # Rebuild the edge list for Sankey input: System From → System To
            sankey_df = filtered_df[['System From', 'System To']].copy()
            
            # Build unique list of systems
            nodes = pd.unique(sankey_df[['System From', 'System To']].values.ravel())
            node_indices = {node: i for i, node in enumerate(nodes)}
            
            # Map source and target to indices
            sankey_df['source_idx'] = sankey_df['System From'].map(node_indices)
            sankey_df['target_idx'] = sankey_df['System To'].map(node_indices)
            
            # Count frequency of each integration line
            sankey_links = sankey_df.groupby(['source_idx', 'target_idx']).size().reset_index(name='value')
            
            # Create Sankey diagram
            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=list(nodes),
                ),
                link=dict(
                    source=sankey_links['source_idx'],
                    target=sankey_links['target_idx'],
                    value=sankey_links['value'],
                )
            )])

            fig.update_layout(title_text="System Integration Lineage: System From → System To", font_size=12)

            # Display the Sankey diagram in Streamlit
            st.plotly_chart(fig)
