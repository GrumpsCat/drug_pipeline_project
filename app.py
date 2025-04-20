#!/usr/bin/env python
# coding: utf-8

# In[4]:


import streamlit as st
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import Descriptors, Crippen, Lipinski
from PIL import Image
import numpy as np
from io import BytesIO
import requests

st.sidebar.subheader("🔍 Look up compound by name")
compound_name = st.sidebar.text_input("Enter compound name (e.g., aspirin)")
add_button = st.sidebar.button("Add to Dataset")

if "extra_compounds" not in st.session_state:
    st.session_state.extra_compounds = []

def search_chembl(name):
    url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/search.json?q={name}&limit=1"
    res = requests.get(url)
    if res.status_code == 200:
        results = res.json().get("molecules", [])
        if results:
            smiles = results[0].get("molecule_structures", {}).get("canonical_smiles")
            chembl_id = results[0].get("molecule_chembl_id")
            return smiles, chembl_id
    return None, None
    
def fetch_bioactivity_data(chembl_id):
    url = f"https://www.ebi.ac.uk/chembl/api/data/activity.json?molecule_chembl_id={chembl_id}&limit=1000"
    res = requests.get(url)
    if res.status_code != 200:
        return []

    data = res.json().get("activities", [])
    results = []

    for act in data:
        value = act.get("standard_value")
        units = act.get("standard_units")
        activity_type = act.get("standard_type")
        target = act.get("target_chembl_id")
        target_desc = act.get("target", {}).get("pref_name")

        if value and units and activity_type in ["IC50", "EC50", "Ki"]:
            results.append({
                "Target Name": target_desc or target,
                "Activity Type": activity_type,
                "Value (nM)": f"{value} {units}"
            })

    return results


if compound_name:
    smiles, chembl_id = search_chembl(compound_name)
    if smiles:
        st.sidebar.success(f"Found: {chembl_id}")
        st.sidebar.write(f"**SMILES:** `{smiles}`")
        mol = Chem.MolFromSmiles(smiles)
        st.sidebar.image(Draw.MolToImage(mol, size=(200, 200)))

        # ✅ Bioactivity data goes in main panel, not sidebar
        with st.expander("🧬 Bioactivity Data"):
            activities = fetch_bioactivity_data(chembl_id)
            if activities:
                st.write(pd.DataFrame(activities).head(10))  # show just the first 10
            else:
                st.info("No activity data found.")

        if add_button:
            st.session_state.extra_compounds.append({
                "Name": chembl_id,
                "SMILES": smiles
            })
            st.sidebar.success("✅ Added to dataset!")
    else:
        st.sidebar.warning("No compound found.")



# === File uploader ===
st.title("💊 Drug-Likeness Explorer")
uploaded_file = st.file_uploader("Upload a CSV file with columns 'Name' and 'SMILES'", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    st.info("Using default sample data (Aspirin, Caffeine, Ibuprofen)")
    df = pd.DataFrame([
        {"Name": "Aspirin", "SMILES": "CC(=O)OC1=CC=CC=C1C(=O)O"},
        {"Name": "Caffeine", "SMILES": "Cn1cnc2c1c(=O)n(c(=O)n2C)C"},
        {"Name": "Ibuprofen", "SMILES": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"},
        {"Name": "Palmitic acid", "SMILES": "CCCCCCCCCCCCCCCC(=O)O"}
    ])

# Append any compounds added from ChEMBL
if st.session_state.extra_compounds:
    df = pd.concat([
        df,
        pd.DataFrame(st.session_state.extra_compounds)
    ], ignore_index=True)


# === Compute Lipinski descriptors ===
def compute_descriptors(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None, None
    desc = {
        "Mol": mol,
        "MolWt": Descriptors.MolWt(mol),
        "LogP": Crippen.MolLogP(mol),
        "NumHDonors": Lipinski.NumHDonors(mol),
        "NumHAcceptors": Lipinski.NumHAcceptors(mol),
        "NumRotatableBonds": Lipinski.NumRotatableBonds(mol),
    }
    desc["LipinskiPassed"] = (
        desc["MolWt"] < 500 and desc["LogP"] < 5 and
        desc["NumHDonors"] <= 5 and desc["NumHAcceptors"] <= 10
    )
    return mol, desc

results = []
for _, row in df.iterrows():
    mol, props = compute_descriptors(row["SMILES"])
    if props:
        props["Name"] = row["Name"]
        props["SMILES"] = row["SMILES"]
        results.append(props)

df = pd.DataFrame(results)

# === Sidebar Filter ===
st.sidebar.header("Filter Compounds")
lipinski_filter = st.sidebar.checkbox("Only show Lipinski-passing", value=False)

if lipinski_filter:
    df = df[df["LipinskiPassed"] == True]

# === Title ===
#st.title("💊 Drug-Likeness Explorer")

# === Show Table ===
st.subheader("Compound Table")
st.dataframe(df[["Name", "MolWt", "LogP", "NumHDonors", "NumHAcceptors", "LipinskiPassed"]])

# === Molecule Grid Display ===
st.subheader("Molecular Structures")
n = st.slider("Number of molecules to display", min_value=1, max_value=len(df), value=4)

mols = df["Mol"].head(n).tolist()
legends = df["Name"].head(n).tolist()

# Generate molecule grid image
img_array = Draw.MolsToGridImage(
    mols,
    legends=legends,
    molsPerRow=4,
    subImgSize=(200, 200),
    useSVG=False,
    returnPNG=False
)

# Convert to actual PIL image if necessary
if hasattr(img_array, 'save'):
    img = img_array
else:
    img = Image.fromarray(np.array(img_array))

# Convert to BytesIO buffer
buf = BytesIO()
img.save(buf, format="PNG")
buf.seek(0)

# Display image
st.image(buf)

# === Descriptor Distributions ===
st.subheader("Descriptor Distributions")
st.bar_chart(df[["MolWt", "LogP", "NumHDonors", "NumHAcceptors"]])

import plotly.express as px

st.subheader("📊 Interactive LogP vs Molecular Weight")

fig = px.scatter(
    df,
    x="LogP",
    y="MolWt",
    color="LipinskiPassed",
    size="NumHDonors",
    hover_name="Name",
    labels={
        "LogP": "LogP (lipophilicity)",
        "MolWt": "Molecular Weight (g/mol)",
        "NumHDonors": "# H-Bond Donors",
        "LipinskiPassed": "Lipinski Passed"
    },
    title="Drug-Likeness Properties"
)

st.plotly_chart(fig, use_container_width=True)


# === Download Button ===
st.subheader("📥 Download Results")

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="drug_likeness_results.csv",
    mime="text/csv"
)





