# System-Integration-Lineage-Visualization
### Excel-driven system integration lineage viewer (Streamlit + Plotly Sankey)

<p align="center">
  <img src="https://placehold.co/1200x420?text=System+Integration+Lineage+Visualization" alt="Banner" />
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/Streamlit-App-FF4B4B" alt="Streamlit"/></a>
  <a href="#"><img src="https://img.shields.io/badge/Plotly-Sankey-3F4F75" alt="Plotly"/></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.9%2B-3776AB" alt="Python"/></a>
  <a href="#"><img src="https://img.shields.io/badge/Input-Excel%20(.xlsx)-217346" alt="Excel"/></a>
</p>

---

## What this project is

**System-Integration-Lineage-Visualization** is a lightweight Streamlit app that visualizes **data lineage / integration flow** between systems using a **Sankey diagram**.

You upload an Excel workbook, select filters (system, technology, batch job, source/target processes), and the app renders a lineage view:

**System From → Technology → System To**

This is designed for quick operational visibility of integration pipelines (e.g., DW feeds, ETL, batch transfers) without needing a dedicated lineage platform.

---

## Features

- ✅ Upload an **Excel (.xlsx)** file via Streamlit UI
- ✅ Reads a target sheet: **`DEB-DW`**
- ✅ Filter lineage interactively by:
  - **System From** *(single select)*
  - **System To** *(multi select)*
  - **Technology** *(multi select)*
  - **Batch Job Name** *(multi select)*
  - **Database/Process From** *(multi select)*
  - **Database/Process To** *(multi select)*
- ✅ Renders a **Plotly Sankey diagram**
- ✅ Deterministic link coloring based on content hashing (stable colors across runs)

---

## Quick start (local)

### 1) Create environment + install
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Run the app
```bash
streamlit run app.py
```

---

## Input file requirements

### Required worksheet
Your Excel file **must** contain a worksheet named:

- `DEB-DW`

If that sheet is missing, the app will show:
> ❌ Error reading 'DEB-DW' sheet: ...

### Required columns
The app expects these columns (exact names, case-sensitive after trimming whitespace):

| Column | Required | Used for |
|---|---:|---|
| `System From` | ✅ | Source system node |
| `System To` | ✅ | Target system node |
| `Technology` | ✅ | Technology node (middle layer) |
| `Batch Job Name` | optional | Filter only |
| `Database/Process From` | optional | Filter only |
| `Database/Process To` | optional | Filter only |

Rows with missing `System From` or `System To` are dropped.

> Note: the app strips whitespace from column names (`df.columns = df.columns.str.strip()`), so headers like `" System From "` are safe.

### Minimal example (recommended)
Create an Excel sheet `DEB-DW` with rows like:

| System From | Technology | System To | Batch Job Name | Database/Process From | Database/Process To |
|---|---|---|---|---|---|
| CRM | API | DWH | CRM_to_DWH | CRM.DB | DWH.STAGE |
| ERP | SFTP | DWH | ERP_SFTP_LOAD | ERP.EXPORT | DWH.RAW |
| DWH | ETL | BI | DWH_BI_REFRESH | DWH.MART | BI.DATASET |

---

## How the visualization works

The Sankey diagram is built with two links per row:

1. `System From` → `Technology`
2. `Technology` → `System To`

Every row contributes a weight/value of `1` (can be improved later to represent volume, frequency, or criticality).

Coloring is stable and reproducible:
- the app hashes each link label using MD5 and seeds a RNG to pick a consistent RGBA color.

---

## Screenshots (placeholders)

<p align="center">
  <img src="https://placehold.co/1100x550?text=Upload+%2B+Filters+UI" alt="UI placeholder" />
</p>

<p align="center">
  <img src="https://placehold.co/1100x550?text=Sankey+Lineage+Diagram" alt="Sankey placeholder" />
</p>

---

## Repository structure

```
.
├── app.py               # Streamlit app (Excel upload + filters + Sankey)
├── requirements.txt     # Python deps
└── README.md
```

---

## Troubleshooting

### “Error reading 'DEB-DW' sheet”
- Confirm the Excel sheet is named **exactly** `DEB-DW`
- Confirm required columns exist (`System From`, `System To`, `Technology`)

### “No data matches the selected filters”
- Your selected filter combination yields an empty dataframe
- Start by selecting only **System From**, then add filters gradually

### Plot looks “too dense”
- Use filters to reduce the number of rows
- Consider pre-aggregating your Excel by System/Technology/System To (see Roadmap)

---

## Roadmap / recommended enhancements

If you want this to behave like a lineage product:

- **Aggregation**: group identical paths and sum counts (instead of value=1 per row)
- **3+ hop lineage**: support “System From → Process → Technology → System To”
- **Clickable metadata panel**: show the underlying rows when a link is selected
- **Export**: download filtered data and/or diagram as image
- **Data validation**: explicit schema validation with user-friendly errors
- **Multiple sheets**: select which sheet to visualize

---

## Notes on dependencies

`requirements.txt` currently includes a few Python standard library modules (`hashlib`, `random`) which are not installable via pip. For clean installs, keep only:

- `streamlit`
- `pandas`
- `openpyxl`
- `plotly`

---

## License

Add your license here (MIT / Apache-2.0 / Proprietary).

---

## Maintainer

**Habtamu Wolde**  
Data Systems • Analytics • Automation • Visualization
