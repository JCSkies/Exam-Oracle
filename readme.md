# AI CS Exam Oracle (Hackathon)

A Streamlit app that analyzes CS course materials (notes/slides/text), surfaces high-yield topics, and generates likely exam questions.

## Architecture (Grounded Hybrid)
- **Deterministic core (always works):** chunking + topic ranking + templated question generation
- **Optional LLM enhancement (when API key present):** refine question wording + produce grounded answer outlines using retrieved evidence

This keeps results stable and reproducible while still enabling a “wow” layer for demos.

---

## Project Structure

---

## Setup (Windows + VS Code)

## In case of issues
**Check if you are in the right folder (should show as (venv) PS C:\Users\<your-name>\exam-oracle)**
```powershell
pwd
dir

```
### 0) Prereqs

- Python installed (use python.org installer)
- VS Code + Python extension

### 1) Clone the repo and open it
```powershell
git clone <REPO_URL>
cd exam-oracle
code .

```
### 2) Create the virtual environment (project-local)
py -3 -m venv venv

### 3) Activate the venv
.\venv\Scripts\Activate.ps1

### In case PowerShell blocks activation
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

### Use the same activation script once again

### 4) Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

### 5) Run the app
python -m streamlit run src/app.py

**Open the URL shown in the terminal (it may auto-open, usually it appears as http://localhost:8501)**