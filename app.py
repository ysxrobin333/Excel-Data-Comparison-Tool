import streamlit as st
import pandas as pd
import difflib
import io

def parse_paste_data(paste_data, has_header=False):
    """
    Parses pasted text data (Excel format) into a DataFrame.
    Assumes tab-separated values.
    """
    if not paste_data.strip():
        return None
    
    try:
        # Use pandas to read clipboard-like data (tab separated)
        # header=0 if has_header else None means let pandas handle headers or not
        header_arg = 0 if has_header else None
        df = pd.read_csv(io.StringIO(paste_data), sep='\t', header=header_arg, dtype=str)
        
        # If no header, give default column names 0, 1, 2...
        if not has_header:
            df.columns = [f"Col_{i+1}" for i in range(len(df.columns))]
            
        # Fill NaNs with empty strings for consistency
        df = df.fillna("")
        return df
    except Exception as e:
        st.error(f"Error parsing data: {e}")
        return None

def align_dataframes(df_a, df_b):
    """
    Aligns two DataFrames based on exact row matching.
    Preserves order and marks differences.
    """
    # Create comparison keys (join all columns with a separator for robust comparison)
    # We use a unique separator likely not in data, e.g., '|||'
    sep = "|||"
    
    # Helper to stringify row
    def row_to_key(row):
        return sep.join(row.values.astype(str))

    list_a = [row_to_key(row) for _, row in df_a.iterrows()]
    list_b = [row_to_key(row) for _, row in df_b.iterrows()]
    
    # Use SequenceMatcher to find alignment
    matcher = difflib.SequenceMatcher(None, list_a, list_b)
    
    aligned_data = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Rows match
            for k in range(i2 - i1):
                row_a = df_a.iloc[i1 + k].tolist()
                row_b = df_b.iloc[j1 + k].tolist()
                aligned_data.append(row_a + row_b + ["Match"])
                
        elif tag == 'replace':
            # Mismatch block. 
            # We want to show deleted from A and inserted into B as separate lines to be clear,
            # unless we want to map them row-by-row as "Changed".
            # The user asked for "unmatched data in the shorter column as spaces".
            # To preserve strict order and show "Alignment", usually 'replace' means these chunks correspond positionally but diff content.
            # However, simpler for "Diff" tool is to show them as purely separate (A only / B only) or try to line them up?
            # Let's align them line by line for the length of the chunk, masking the rest.
            
            len_a = i2 - i1
            len_b = j2 - j1
            max_len = max(len_a, len_b)
            
            for k in range(max_len):
                row_a = df_a.iloc[i1 + k].tolist() if k < len_a else [""] * len(df_a.columns)
                row_b = df_b.iloc[j1 + k].tolist() if k < len_b else [""] * len(df_b.columns)
                
                diff_type = []
                if k < len_a: diff_type.append("Only in A")
                if k < len_b: diff_type.append("Only in B")
                
                # If both exist, it's a mismatch/replacement
                final_type = "Mismatch" if (k < len_a and k < len_b) else (diff_type[0] if diff_type else "")
                
                aligned_data.append(row_a + row_b + [final_type])
                
        elif tag == 'delete':
            # In A but not in B
            for k in range(i2 - i1):
                row_a = df_a.iloc[i1 + k].tolist()
                row_b = [""] * len(df_b.columns)
                aligned_data.append(row_a + row_b + ["Only in A"])
                
        elif tag == 'insert':
            # In B but not in A
            for k in range(j2 - j1):
                row_a = [""] * len(df_a.columns)
                row_b = df_b.iloc[j1 + k].tolist()
                aligned_data.append(row_a + row_b + ["Only in B"])

    # Construct result columns
    cols_a = [f"A_{c}" for c in df_a.columns]
    cols_b = [f"B_{c}" for c in df_b.columns]
    cols_final = cols_a + cols_b + ["Diff_Type"]
    
    return pd.DataFrame(aligned_data, columns=cols_final)

# --- UI Setup ---
st.set_page_config(page_title="Excel Data Comparison Tool", layout="wide")

st.title("📊 Excel Data Comparison Tool")
st.markdown("""
This tool compares two sets of data (A and B) pasted from Excel.
- It aligns the rows based on **exact matching** of all columns.
- Order is preserved.
- Missing data is shown as empty cells.
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Data Set A")
    paste_a = st.text_area("Paste Excel data for A here:", height=300)

with col2:
    st.subheader("Data Set B")
    paste_b = st.text_area("Paste Excel data for B here:", height=300)

has_header = st.checkbox("My data includes headers", value=False)

if st.button("Compare Data"):
    if not paste_a or not paste_b:
        st.warning("Please paste data into both A and B fields.")
    else:
        df_a = parse_paste_data(paste_a, has_header)
        df_b = parse_paste_data(paste_b, has_header)
        
        if df_a is not None and df_b is not None:
            st.success(f"Loaded Data A: {df_a.shape[0]} rows, {df_a.shape[1]} columns")
            st.success(f"Loaded Data B: {df_b.shape[0]} rows, {df_b.shape[1]} columns")
            
            with st.spinner("Aligning data..."):
                result_df = align_dataframes(df_a, df_b)
            
            st.subheader("Comparison Result")
            st.dataframe(result_df, use_container_width=True)
            
            # Download Logic
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                result_df.to_excel(writer, index=False, sheet_name='Comparison Result')
                
                # Auto-adjust column width (basic heuristic)
                worksheet = writer.sheets['Comparison Result']
                for idx, col in enumerate(result_df):
                    max_len = max(result_df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(idx, idx, max_len)
                    
            output.seek(0)
            
            st.download_button(
                label="📥 Download Result as Excel",
                data=output,
                file_name="comparison_result.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
