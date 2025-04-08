import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load data
@st.cache_data
def load_data(file):
    return pd.read_excel(file)

# UI
st.title("System Integration Lineage Visualization")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
if uploaded_file:
    df = load_data(uploaded_file)
    
    # Dropdowns
    system_from = st.selectbox("Select System From", df['System From'].dropna().unique())
    system_to = st.selectbox("Select System To", df['System To'].dropna().unique())
    batch_job = st.selectbox("Select Batch Job Name", df['Batch Job Name'].dropna().unique())
    technology = st.selectbox("Select Technology", df['Technology'].dropna().unique())
    db_from = st.selectbox("Select Database/Process From", df['Database/Process  From'].dropna().unique())
    db_to = st.selectbox("Select Database/Process To", df['Database/Process To'].dropna().unique())
    
    if st.button("Generate Sankey Diagram"):
        # Filter data based on selections
        filtered_df = df[(df['System From'] == system_from) &
                         (df['System To'] == system_to) &
                         (df['Batch Job Name'] == batch_job) &
                         (df['Technology'] == technology) &
                         (df['Database/Process  From'] == db_from) &
                         (df['Database/Process To'] == db_to)]
        
        if not filtered_df.empty:
            sankey_df = filtered_df[['System From', 'System To']].copy()
            nodes = pd.unique(sankey_df.values.ravel())
            node_indices = {node: i for i, node in enumerate(nodes)}
            sankey_df['source_idx'] = sankey_df['System From'].map(node_indices)
            sankey_df['target_idx'] = sankey_df['System To'].map(node_indices)
            sankey_links = sankey_df.groupby(['source_idx', 'target_idx']).size().reset_index(name='value')
            
            # Sankey Diagram
            fig = go.Figure(data=[go.Sankey(
                node=dict(label=list(nodes), pad=15, thickness=20, line=dict(color="black", width=0.5)),
                link=dict(source=sankey_links['source_idx'], target=sankey_links['target_idx'], value=sankey_links['value'])
            )])
            fig.update_layout(title_text="System Integration Lineage", font_size=12)
            st.plotly_chart(fig)
        else:
            st.warning("No matching data found. Try different selections.")
