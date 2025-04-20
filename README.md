# 💊 Drug-Likeness Explorer

An interactive cheminformatics web app to explore the drug-likeness of small molecules using **RDKit** and **Streamlit**.

This tool allows users to upload or search for molecular structures, compute molecular descriptors, visualize drug-likeness, and download results — all in a clean web interface.

---

## 🚀 Features

- 🧬 **SMILES Input**: Upload molecules via CSV or search by compound name using ChEMBL.
- 🧠 **Drug-Likeness Filtering**: Apply **Lipinski's Rule of Five** to filter drug-like compounds.
- 🧪 **Descriptor Calculation**:
  - Molecular Weight
  - LogP
  - Hydrogen Bond Donors / Acceptors
  - Rotatable Bonds
- 🖼 **Molecule Visualization**: Display molecule structures in a grid.
- 📊 **Descriptor Distributions**: Bar chart of key descriptors.
- 📥 **Downloadable Results**: Export filtered data as CSV.

---

## 🧰 Tech Stack

| Tool        | Purpose                                  |
|-------------|------------------------------------------|
| `Streamlit` | Web app framework                        |
| `RDKit`     | Cheminformatics toolkit                  |
| `Pandas`    | Data manipulation and table handling     |
| `Plotly`    | Descriptor visualization (optional)      |
| `ChEMBL API`| Molecular search via compound names      |

---

## 📁 File Structure
drug_pipeline_project/ ├── app.py # Main Streamlit app ├── environment.yml # Conda-based environment (used by Streamlit Cloud) ├── .streamlit/ │ └── config.toml # Streamlit Cloud settings
