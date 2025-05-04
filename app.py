import time

import streamlit as st
import pandas as pd
from PIL import Image
import subprocess
import os
import base64
import pickle

# Helper function to add loading spinner and progress bar
def show_progress_bar():
    st.sidebar.markdown("**Processing...**")
    with st.spinner("Please wait while descriptors are being calculated..."):
        for i in range(100):
            st.progress(i + 1)
            time.sleep(0.01)
# Molecular descriptor calculator
def desc_calc():
    # Performs the descriptor calculation
    bashCommand = "java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    os.remove('molecule.smi')

# File download
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
    return href

# Model building
def build_model(input_data):
    # Reads in saved regression model
    load_model = pickle.load(open('acetylcholinesterase_model.pkl', 'rb'))
    # Apply model to make predictions
    prediction = load_model.predict(input_data)
    st.header('**Prediction output**')
    prediction_output = pd.Series(prediction, name='pIC50')
    molecule_name = pd.Series(load_data[1], name='molecule_name')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    st.write(df)
    st.markdown(filedownload(df), unsafe_allow_html=True)

# Logo image
image = Image.open('assets/logo.png')

st.image(image, use_container_width=True)

# Page title
st.markdown("""
<style>
    .stApp {
        background-color: #e6f1eb;
    }
    section[data-testid="stSidebar"] {
        background-color: #e6f1eb;
    }
    header[data-testid="stHeader"] div {
        background-color: #e6f1eb;
    }
     div.stButton > button {
        background-color: #fdf7f1;
        color: black;
        border: 1px solid #ccc;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        transition: all 0.2s ease-in-out;
    }

    div.stButton > button:hover {
        background-color: #f2ede7;
        transform: scale(1.02);
        border-color: #aaa;
    }
    html, body, [class*="css"] {
        color: #2a3c63 !important;
    }

    .stFileUploader label {
        color: #2a3c63 !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #2a3c63 !important;
    }
    </style>
# Bioactivity Prediction App (Acetylcholinesterase)

This app allows you to predict the bioactivity towards inhibting the `Acetylcholinesterase` enzyme. `Acetylcholinesterase` is a drug target for Alzheimer's disease.

**Credits**
- App built in `Python` + `Streamlit` by [Zeineb Eya Rahmani](https://github.com/zeineb-eya/) 
- Descriptor calculated using [PaDEL-Descriptor](http://www.yapcwsoft.com/dd/padeldescriptor/) [[Read the Paper]](https://doi.org/10.1002/jcc.21707).
---
""",unsafe_allow_html=True
)

# Sidebar
with st.sidebar.header('1. Upload your CSV data'):
    uploaded_file = st.sidebar.file_uploader("Upload your input file", type=['txt'])
    st.sidebar.markdown("""
[Example input file](drive.google.com/file/d/1DDTstK4T_vLqfhOIlsa0seWhtIyboGPP/view?usp=drive_open)
""")


if st.sidebar.button('Predict'):
    if uploaded_file is None:
        st.warning('⚠️ Please upload a file before clicking Predict.')
    else:
        try:
            load_data = pd.read_table(uploaded_file, delimiter=' ', header=None)

            # Check if the file is empty after reading
            if load_data.empty:
                st.error('❌ The uploaded file is empty. Please upload a valid file.')
            else:
                # Proceed with further checks and prediction
                if load_data.shape[1] != 2:
                    st.error(
                        '❌ Invalid file format. Each line must contain a SMILES string and a molecule name (e.g., CHEMBL ID), separated by a space.')
                else:
                    load_data.to_csv('molecule.smi', sep='\t', header=False, index=False)
                    st.header('**Original input data**')
                    st.write(load_data)



                    with st.spinner("Calculating descriptors..."):
                        desc_calc()

                    st.header('**Calculated molecular descriptors**')
                    desc = pd.read_csv('data/descriptors_output.csv')
                    st.write(desc)
                    st.write(desc.shape)

                    st.header('**Subset of descriptors from previously built models**')
                    Xlist = list(pd.read_csv('data/descriptor_list.csv').columns)
                    desc_subset = desc[Xlist]
                    st.write(desc_subset)
                    st.write(desc_subset.shape)

                    build_model(desc_subset)
        except Exception as e:
            st.error(f'❌ An error occurred while processing the file: {str(e)}')
else:
    st.info('Upload input data in the sidebar to start!')
# Footer with links and help section
st.markdown("""
---
For more details, check out the [App GitHub](https://github.com/zeineb-eya/bioactivity-predictions-app).

Questions? Reach out to [zeineb.eya.rahmani@outlook.com](mailto:zeineb.eya.rahmani@outlook.com).
""")