import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# Load data function (for illustration purposes, replace this with your actual data loading method)
@st.cache_data
def load_data():
    # Replace with your actual data loading logic
    return pd.read_csv("your_data.csv")

# Load the data
df = load_data()

# Streamlit UI elements for filtering
st.sidebar.header("Filter Options")
system_options = pd.unique(df[['System From', 'System To']].values.ravel())
selected_system_from = st.sidebar.selectbox("Select Source System", system_options)
selected_system_to = st.sidebar.selectbox("Select Target System", system_options)

# Filter data based on user input
valid_flows = df[
    (df['System From'].str.upper() == selected_system_from.upper()) & 
    (df['System To'].str.upper() == selected_system_to.upper())
]

# Create unique nodes and indices
nodes = pd.unique(valid_flows[['System From', 'System To']].values.ravel())
node_indices = {node: i for i, node in enumerate(nodes)}

# Map source and target to indices
valid_flows['source_idx'] = valid_flows['System From'].map(node_indices)
valid_flows['target_idx'] = valid_flows['System To'].map(node_indices)

# Count frequency of each integration line
sankey_links = valid_flows.groupby(['source_idx', 'target_idx']).size().reset_index(name='value')

# Colorize links based on the technology (for example, or any other criteria)
color_map = {
    'Technology1': 'rgba(31, 119, 180, 0.8)', 
    'Technology2': 'rgba(255, 127, 14, 0.8)', 
    'Technology3': 'rgba(44, 160, 44, 0.8)', 
    # Add more colors for each technology
}
valid_flows['link_color'] = valid_flows['Technology'].map(color_map).fillna('rgba(128, 128, 128, 0.8)')

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
        color=valid_flows['link_color'].iloc[:len(sankey_links)]  # Dynamically color links
    )
)])

fig.update_layout(title_text="System Integration Lineage: {} → {}".format(selected_system_from, selected_system_to), font_size=12)

# Display the Sankey diagram
st.plotly_chart(fig)

# Export Sankey diagram to HTML
sankey_html_path = "/mnt/data/system_integration_lineage_sankey.html"
pio.write_html(fig, sankey_html_path)

st.markdown(f"Download the Sankey diagram HTML: [Download here]({sankey_html_path})")

# Filter only BRM as the source system for detailed breakdown
brm_flows = valid_flows[valid_flows['System From'].str.upper() == 'BRM']

# Create unique nodes for BRM-related data
brm_nodes = pd.unique(brm_flows[['System From', 'System To']].values.ravel())
brm_node_indices = {node: i for i, node in enumerate(brm_nodes)}

# Map BRM flows to Sankey format
brm_flows['source_idx'] = brm_flows['System From'].map(brm_node_indices)
brm_flows['target_idx'] = brm_flows['System To'].map(brm_node_indices)

# Aggregate link values for BRM
brm_links = brm_flows.groupby(['source_idx', 'target_idx']).size().reset_index(name='value')

# Generate Sankey diagram for BRM
fig_brm = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=list(brm_node_indices.keys()),
    ),
    link=dict(
        source=brm_links['source_idx'],
        target=brm_links['target_idx'],
        value=brm_links['value'],
    )
)])

fig_brm.update_layout(title_text="BRM System Integration Lineage", font_size=12)

# Display BRM Sankey diagram
st.plotly_chart(fig_brm)

# Export BRM Sankey diagram to HTML
brm_sankey_html_path = "/mnt/data/brm_system_integration_lineage_sankey.html"
pio.write_html(fig_brm, brm_sankey_html_path)

st.markdown(f"Download the BRM Sankey diagram HTML: [Download here]({brm_sankey_html_path})")

# Filter BRM flows with technology and batch job details
brm_detail = df[
    (df['System From'].str.upper() == 'BRM') &
    (df['System To'] != '') &
    (df['Batch Job Name'] != '') &
    (df['Technology'] != '')
][['System From', 'Technology', 'Batch Job Name', 'System To']].copy()

# Create flow: BRM → Technology → Batch Job → System To
records = []
for _, row in brm_detail.iterrows():
    records.append((row['System From'], row['Technology']))
    records.append((row['Technology'], row['Batch Job Name']))
    records.append((row['Batch Job Name'], row['System To']))

brm_lineage_df = pd.DataFrame(records, columns=['source', 'target'])

# Unique nodes and mapping to indices for detailed BRM
brm_nodes_detail = pd.unique(brm_lineage_df[['source', 'target']].values.ravel())
brm_node_idx_detail = {node: i for i, node in enumerate(brm_nodes_detail)}
brm_lineage_df['source_idx'] = brm_lineage_df['source'].map(brm_node_idx_detail)
brm_lineage_df['target_idx'] = brm_lineage_df['target'].map(brm_node_idx_detail)

# Count connections
brm_links_detail = brm_lineage_df.groupby(['source_idx', 'target_idx']).size().reset_index(name='value')

# Generate detailed Sankey diagram with intermediate steps (BRM → Technology → Batch Job → System To)
fig_brm_detail = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=list(brm_node_idx_detail.keys())
    ),
    link=dict(
        source=brm_links_detail['source_idx'],
        target=brm_links_detail['target_idx'],
        value=brm_links_detail['value']
    )
)])

fig_brm_detail.update_layout(title_text="BRM Integration Lineage with Technology & Batch Jobs", font_size=12)

# Display detailed BRM Sankey diagram
st.plotly_chart(fig_brm_detail)

# Export detailed BRM Sankey diagram to HTML
brm_detailed_path = "/mnt/data/brm_detailed_lineage_sankey.html"
pio.write_html(fig_brm_detail, brm_detailed_path)

st.markdown(f"Download the Detailed BRM Sankey diagram HTML: [Download here]({brm_detailed_path})")
