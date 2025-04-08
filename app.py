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

                # Create directed links
                links = []
                annotations = []
                x_positions = {}
                y_positions = {}
                spacing = 200  # Adjust spacing for readability

                # Assign positions for nodes
                for i, node in enumerate(unique_nodes):
                    if node in filtered_df["System From"].values:
                        x_positions[node] = 0
                    elif node in filtered_df["Technology"].values:
                        x_positions[node] = spacing
                    elif node in filtered_df["System To"].values:
                        x_positions[node] = spacing * 2
                    y_positions[node] = i * 100

                for _, row in filtered_df.iterrows():
                    source = row["System From"]
                    tech = row["Technology"]
                    target = row["System To"]

                    # Add arrows for flow direction
                    links.append(
                        go.Scatter(
                            x=[x_positions[source], x_positions[tech]],
                            y=[y_positions[source], y_positions[tech]],
                            mode="lines+markers",
                            line=dict(width=2, color="blue"),
                            marker=dict(size=10),
                            name=f"{source} → {tech}",
                        )
                    )

                    links.append(
                        go.Scatter(
                            x=[x_positions[tech], x_positions[target]],
                            y=[y_positions[tech], y_positions[target]],
                            mode="lines+markers",
                            line=dict(width=2, color="green"),
                            marker=dict(size=10),
                            name=f"{tech} → {target}",
                        )
                    )

                    # Add labels
                    annotations.append(
                        dict(
                            x=x_positions[source],
                            y=y_positions[source],
                            xref="x",
                            yref="y",
                            text=source,
                            showarrow=True,
                            arrowhead=2,
                        )
                    )
                    annotations.append(
                        dict(
                            x=x_positions[tech],
                            y=y_positions[tech],
                            xref="x",
                            yref="y",
                            text=tech,
                            showarrow=True,
                            arrowhead=2,
                        )
                    )
                    annotations.append(
                        dict(
                            x=x_positions[target],
                            y=y_positions[target],
                            xref="x",
                            yref="y",
                            text=target,
                            showarrow=True,
                            arrowhead=2,
                        )
                    )

                # Create the flow diagram
                fig = go.Figure(data=links)
                fig.update_layout(
                    title_text="System Integration Flow",
                    font_size=12,
                    annotations=annotations,
                    showlegend=False,
                )

                st.plotly_chart(fig)
            else:
                st.warning("No data found for the selected filters!")
