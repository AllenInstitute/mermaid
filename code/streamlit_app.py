import streamlit as st
import pandas as pd
from streamlit_mermaid_interactive import mermaid
from typing import Dict

# see: https://pypi.org/project/streamlit-mermaid-interactive/0.1.12/
## 1. DATA AND LOGIC (Your df_to_mermaid equivalent in Python)
# -----------------------------------------------------------

def create_sample_data():
    """Generates a sample DataFrame for the flow."""
    data = {
        'From_ID': ['A', 'A', 'C', 'D'],
        'From_Label': ['Project Start', 'Project Start', 'Analysis', 'Review'],
        'To_ID': ['B', 'C', 'D', 'E'],
        'To_Label': ['Data Collection', 'Analysis', 'Review', 'Final Report'],
        'Connector': ['---', '-- some text -->', '-.->', '<-->'], # see https://mermaid.js.org/syntax/flowchart.html#links-between-nodes
        'Tooltip': ['Kickoff notes', 'Define requirements', 'Check results', 'Final sign-off'],
        'URL': ['#', 'https://example.com/data', 'https://example.com/analysis', 'https://example.com/report'],
        'notes': ['', 'Note B', 'Note C', 'Note D']
    }
    return pd.DataFrame(data)

def df_to_mermaid(df, theme):
    """Converts a Pandas DataFrame into a Mermaid syntax string."""
    
    # 1. Start the configuration and set the theme
    mermaid_code = f"%%{{init: {{'theme': '{theme}'}}}}%%\n"
    mermaid_code += "flowchart TD\n"

    # 2. Build Nodes and Edges
    # not added: node styles
    for index, row in df.iterrows():
        # Sanitize IDs/Labels
        from_id = row['From_ID'].strip()
        to_id = row['To_ID'].strip()
        from_label = row['From_Label'].replace('"', '\\"') # Escape quotes for the label
        to_label = row['To_Label'].replace('"', '\\"')
        
        # Line: A["Start"] --> B["End"]
        # pull connector from DataFrame
        connector = row['Connector'].strip() #if 'Connector' in row and pd.notna(row['Connector']) else '-->'
        print(connector)
        # concatenate using the connector
        mermaid_code += f"    {from_id}[\"{from_label}\"] {connector} {to_id}[\"{to_label}\"]\n"

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
    print(mermaid_code)
    return mermaid_code

def build_url_map(df: pd.DataFrame) -> Dict[str, str]:
    """Build a mapping of node ID -> URL from a DataFrame.

    The DataFrame is expected to contain the columns `From_ID`, `To_ID`,
    and `URL`. The function prefers non-empty URLs and will populate
    entries for both `From_ID` and `To_ID`.

    Returns a dict where keys are IDs (strings) and values are URLs (strings).
    """
    url_map: Dict[str, str] = {}
    for _, r in df.iterrows():
        try:
            fid = str(r.get('From_ID', '')).strip()
        except Exception:
            fid = ''
        try:
            tid = str(r.get('To_ID', '')).strip()
        except Exception:
            tid = ''
        try:
            flabel = str(r.get('From_Label', '')).strip()
        except Exception:
            flabel = ''
        try:
            tlabel = str(r.get('To_Label', '')).strip()
        except Exception:
            tlabel = ''
        url = r.get('URL', '') if pd.notna(r.get('URL', '')) else ''
        if fid:
            if fid not in url_map or (not url_map[fid] and url):
                url_map[fid] = url
        if tid:
            if tid not in url_map or (not url_map[tid] and url):
                url_map[tid] = url
        # Also map human-facing labels to the same URL so click events that
        # return labels (instead of IDs) can be resolved.
        if flabel:
            if flabel not in url_map or (not url_map[flabel] and url):
                url_map[flabel] = url
        if tlabel:
            if tlabel not in url_map or (not url_map[tlabel] and url):
                url_map[tlabel] = url
    return url_map

def build_note_map(df: pd.DataFrame) -> Dict[str, str]:
    """Build a mapping of node ID -> notes from a DataFrame.

    The DataFrame is expected to contain the columns `From_ID`, `To_ID`,
    and `notes`. 

    Returns a dict where keys are IDs (strings) and values are notes (strings).
    """
    note_map: Dict[str, str] = {}
    for _, r in df.iterrows():
        try:
            fid = str(r.get('From_ID', '')).strip()
        except Exception:
            fid = ''
        try:
            tid = str(r.get('To_ID', '')).strip()
        except Exception:
            tid = ''
        try:
            flabel = str(r.get('From_Label', '')).strip()
        except Exception:
            flabel = ''
        try:
            tlabel = str(r.get('To_Label', '')).strip()
        except Exception:
            tlabel = ''
        note = r.get('notes', '') if pd.notna(r.get('notes', '')) else ''
        if fid:
            if fid not in note_map or (not note_map[fid] and note):
                note_map[fid] = note
        if tid:
            if tid not in note_map or (not note_map[tid] and note):
                note_map[tid] = note
        # Also map human-facing labels to the same URL so click events that
        # return labels (instead of IDs) can be resolved.
        if flabel:
            if flabel not in note_map or (not note_map[flabel] and note):
                note_map[flabel] = note
        if tlabel:
            if tlabel not in note_map or (not note_map[tlabel] and note):
                note_map[tlabel] = note
    return note_map

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
    # Orientation selector: change diagram flow direction
    orientation = st.selectbox(
        "Diagram Direction:",
        [
            ('TD', 'Top → Bottom (TD)'),
            ('LR', 'Left → Right (LR)'),
        ],
        index=0,
        format_func=lambda x: x[1],
    )
    # orientation is a tuple (code, label); extract the code
    orientation_code = orientation[0]
    
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

# Apply selected orientation (replace the default header once)
try:
    if orientation_code and isinstance(orientation_code, str):
        mermaid_code_output = mermaid_code_output.replace("flowchart TD\n", f"flowchart {orientation_code}\n", 1)
except NameError:
    # orientation_code not defined (e.g., called from other script) — ignore
    pass

# Build a mapping from node ID -> URL so click handlers can look up links.
url_map = build_url_map(input_df)
note_map = build_note_map(input_df)
# --- Display Mermaid Diagram ---

st.header("Flowchart with Interactive Nodes")

result = mermaid(mermaid_code_output, theme="neutral", key="flowchart")
print(result)

if result.get("entity_clicked"):
    entity = result.get("entity_clicked")
    # try the URL reported by the component first, then fallback to our DataFrame map
#    url = url_map.get(entity, '')
    url = result.get("entity_url") or url_map.get(entity, '')
    note = result.get("note") or note_map.get(entity, '')
    st.info(f"Clicked: {entity}")
    #st.write(f"Clicked: {entity}")
    print("URL:",url)
    print("note:",note)
    if url and url != '#':
        # render a clickable link that opens in a new tab
        st.markdown(
            f'<a href="{url}" target="_blank" rel="noopener noreferrer">Open link</a>',
            unsafe_allow_html=True,
        )
    else:
        st.write("No URL available for this node")
    # dsplay the notes, if available
    if note and note != '#':
        st.markdown(
            f'**Notes:** {note}',
        )
    else:
        st.write("No notes available for this node")
    
    

# 1. Initialize session state if the code hasn't been generated yet
if 'mermaid_editor_code' not in st.session_state:
    st.session_state['mermaid_editor_code'] = mermaid_code_output

# 2. Update the state whenever the DataFrame logic runs (i.e., when inputs change)
# We set a flag to only overwrite the editor if the data changed, 
# not every single time the app reruns.
st.session_state['mermaid_editor_code'] = mermaid_code_output

st.header("Mermaid Code Editor (Edit to fine-tune)")

st.markdown(" \
You can edit the Mermaid code to fine-tune the diagram.  \
See the [Mermaid Flowchart Documentation](https://mermaid.js.org/syntax/flowchart.html) " )

# 3. Use st.text_area for an editable box
edited_code = st.text_area(
    "Edit Code Below", 
    value=st.session_state['mermaid_editor_code'],
    height=300,
    key="mermaid_editor" # Key is important for tracking state
)

# 4. Render the diagram using the content of the editable box
st.header("Generated Flowchart")

result_update = mermaid(edited_code, theme="neutral", key="flowchart_update")

if result_update.get("entity_clicked"):
    entity = result_update.get("entity_clicked")
    url = result_update.get("entity_url") or url_map.get(entity, '')
    st.info(f"Clicked: {entity}")
    if url and url != '#':
        st.markdown(
            f'<a href="{url}" target="_blank" rel="noopener noreferrer">Open link</a>',
            unsafe_allow_html=True,
        )
    else:
        st.write("No URL available for this node")