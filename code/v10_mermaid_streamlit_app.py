import streamlit as st
import pandas as pd
import streamlit_mermaid
#import streamlit_mermaid_interactive
from streamlit_mermaid import st_mermaid

#from streamlit_mermaid_interactive import st_mermaid

## 1. DATA AND LOGIC (Your df_to_mermaid equivalent in Python)
# -----------------------------------------------------------

def create_sample_data():
    """Generates a sample DataFrame for the flow."""
    data = {
        'From_ID': ['A', 'A', 'C', 'D'],
        'From_Label': ['Project Start', 'Project Start', 'Analysis', 'Review'],
        'To_ID': ['B', 'C', 'D', 'E'],
        'To_Label': ['Data Collection', 'Analysis', 'Review', 'Final Report'],
        'Tooltip': ['Kickoff notes', 'Define requirements', 'Check results', 'Final sign-off'],
        'URL': ['#', 'https://example.com/data', 'https://example.com/analysis', 'https://example.com/report']
    }
    return pd.DataFrame(data)

def df_to_mermaid(df, theme):
    """Converts a Pandas DataFrame into a Mermaid syntax string."""
    
    # 1. Start the configuration and set the theme
    mermaid_code = f"%%{{init: {{'theme': '{theme}'}}}}%%\n"
    mermaid_code += "flowchart TD\n"

    # 2. Build Nodes and Edges
    for index, row in df.iterrows():
        # Sanitize IDs/Labels
        from_id = row['From_ID'].strip()
        to_id = row['To_ID'].strip()
        from_label = row['From_Label'].replace('"', '\\"') # Escape quotes for the label
        to_label = row['To_Label'].replace('"', '\\"')
        
        # Line: A["Start"] --> B["End"]
        mermaid_code += f"    {from_id}[\"{from_label}\"] --> {to_id}[\"{to_label}\"]\n"

    # 3. Add Click Events (Tooltips/Links)
    # Get unique nodes that have metadata
    unique_nodes = df.drop_duplicates(subset=['From_ID'])
    
    mermaid_code += "\n    %% Interactive Elements (Tooltips & Links)\n"

    for index, row in unique_nodes.iterrows():
        id = row['From_ID'].strip()
        url = row['URL'] if pd.notna(row['URL']) else '#'
        tip = row['Tooltip'] if pd.notna(row['Tooltip']) else ''
        
        # Syntax: click ID "URL" "Tooltip"
        if url != '#' or tip != '':
            # Escape quotes for JS string
            tip = tip.replace('"', '\\"') 
            mermaid_code += f"    click {id} \"{url}\" \"{tip}\"\n"

    return mermaid_code


## 2. STREAMLIT APP INTERFACE
# -----------------------------

st.title("Dataframe to Mermaid Flowchart")

# Sidebar for controls
with st.sidebar:
    st.header("Configuration")
    
    # Theme Selector (Styling Improvement)
    theme_option = st.selectbox(
        "Select Mermaid Theme:",
        ['default', 'dark', 'neutral', 'forest'],
        index=0
    )
    
    st.header("Data Input")
    
    # File Uploader
    uploaded_file = st.file_uploader("Upload your Flow CSV", type=['csv'])
    
    # Download Sample Data Button
    sample_df = create_sample_data()
    csv = sample_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Sample CSV Template",
        data=csv,
        file_name='mermaid_flow_template.csv',
        mime='text/csv',
    )


# --- Main App Logic ---

# Determine the DataFrame source
if uploaded_file is not None:
    input_df = pd.read_csv(uploaded_file)
    st.subheader("Uploaded Data Preview")
    st.dataframe(input_df.head())
else:
    input_df = create_sample_data()
    st.subheader("Default Sample Flow")
    st.dataframe(input_df)

# Generate the Mermaid Code from the DataFrame
mermaid_code_output = df_to_mermaid(input_df, theme_option)

# --- Display Mermaid Diagram ---

st.header("Generated Flowchart")

# Render the diagram using the custom Streamlit component
st_mermaid(
    mermaid_code_output,
    key="original_mermaid_chart", # Use a unique key!
    height=800                  # Set a larger height (e.g., 600px)
)

# Display the generated code
#with st.expander("View Generated Mermaid Code"):
#    st.code(mermaid_code_output, language='mermaid')

# 1. Initialize session state if the code hasn't been generated yet
if 'mermaid_editor_code' not in st.session_state:
    st.session_state['mermaid_editor_code'] = mermaid_code_output

# 2. Update the state whenever the DataFrame logic runs (i.e., when inputs change)
# We set a flag to only overwrite the editor if the data changed, 
# not every single time the app reruns.
st.session_state['mermaid_editor_code'] = mermaid_code_output

st.header("Mermaid Code Editor (Edit to fine-tune)")

# 3. Use st.text_area for an editable box
edited_code = st.text_area(
    "Edit Code Below", 
    value=st.session_state['mermaid_editor_code'],
    height=300,
    key="mermaid_editor" # Key is important for tracking state
)

# 4. Render the diagram using the content of the editable box
st.header("Generated Flowchart")

st_mermaid(
    edited_code, # Render the diagram from the *editable* text area
    key="updated_mermaid_chart",
    height=800                  # Set a larger height (e.g., 600px)
)



  