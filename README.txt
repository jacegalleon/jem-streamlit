==================================================
J-Expense Manager – v1.0.0
==================================================

Created by: Jace Galleon

Release: 1.0.0
Date: May 11, 2026

Environment:
- Python 3.14.4
- Streamlit 1.57.0
- Pandas 3.0.2

--------------------------------------------------
DESCRIPTION
--------------------------------------------------

This is a simple expense-sharing web application built using Streamlit.

It allows users to:
- Upload expense data via CSV
- Manually input expense entries
- Validate input data (structure, types, and rules)
- Compute balances for each participant
- Generate settlement transactions
- View per-person breakdowns


--------------------------------------------------
PROJECT STRUCTURE
--------------------------------------------------

jem_v1.0.0/
│
├── ui/
│   └── app.py
│
├── src/
│   └── utils.py
│
├── sample_data/
│   ├── valid_test.csv
│   ├── invalid_test.csv
│   └── template.csv
│
├── requirements.txt
├── jem.bat
└── README.txt


--------------------------------------------------
VERSION DETAILS
--------------------------------------------------

v1.0.0 (Initial Release)

Features included:
- CSV upload with validation
- Manual entry form
- Balance computation
- Settlement generation
- Per-person breakdown view
- Input validation with formatted feedback


--------------------------------------------------
MODULE RESPONSIBILITIES
--------------------------------------------------

app.py
- Handles user interface (Streamlit)
- Manages session state
- Displays tables and computation results

utils.py
- Contains core logic
- Handles validation, computation, and transformations


--------------------------------------------------
HOW TO RUN
--------------------------------------------------

From project root:

    streamlit run ui/app.py


--------------------------------------------------
INPUT REQUIREMENTS (CSV)
--------------------------------------------------

Required columns:
- Contributor
- Item
- Amount
- Payor
- Contribution %

Rules:
- Amount must be numeric and greater than 0
- Contribution % must be in decimal form (0.0 – 1.0)
  Example: 0.25 = 25%
- Total Contribution per (Item + Contributor) must not exceed 1.0
- No empty values in key fields


==============================
SAMPLE DATA
==============================

Located in:
sample_data/

This folder contains example CSV files to help users understand
the expected input format and test the application.

Files included:

- template.csv  
  → Blank template file with required column structure.
  → Use this as a starting point for creating your own data.

- valid_test.csv  
  → Example of correctly formatted data.
  → Can be used to verify that the application works properly.

- invalid_test.csv  
  → Example dataset that violates validation rules.
  → Demonstrates how the application handles errors.

These files are optional and are not required to run the app,
but are highly recommended for testing and onboarding.


==============================
REQUIREMENTS
==============================

Python version:
- Python 3.14.4

Libraries:
- streamlit == 1.57.0
- pandas == 3.0.2

Install dependencies:
pip install -r requirements.txt


--------------------------------------------------
NOTES
--------------------------------------------------

- Validation messages are summarized for readability
- Errors highlight problematic entries clearly
- Application prevents computation unless data is valid


--------------------------------------------------
END OF DOCUMENT
--------------------------------------------------
\ No newline at end of file
---
> ==================================================
> J-Expense Manager – v1.1.0
> ==================================================
> 
> Created by: Jace Galleon
> 
> Release: 1.1.0
> Date: June 15, 2026
> 
> Environment:
> - Python 3.14.4
> - Streamlit 1.57.0
> - Pandas 3.0.2
> 
> --------------------------------------------------
> DESCRIPTION
> --------------------------------------------------
> 
> This is a simple expense-sharing web application built using Streamlit.
> 
> It allows users to:
> - Upload expense data via CSV
> - Manually input expense entries
> - Validate input data (structure, types, and rules)
> - Compute balances for each participant
> - Generate settlement transactions
> - View per-person breakdowns
> - Add new expenses after a settlement has been computed
> - Mark individual expense items as "Settled" to exclude them
>   from balances, settlements, and breakdowns
> 
> 
> --------------------------------------------------
> PROJECT STRUCTURE
> --------------------------------------------------
> 
> jem_v1.1.0/
> │
> ├── ui/
> │   └── app.py
> │
> ├── src/
> │   └── utils.py
> │
> ├── sample_data/
> │   ├── valid_test.csv
> │   ├── invalid_test.csv
> │   └── template.csv
> │
> ├── requirements.txt
> ├── jem.bat
> └── README.txt
> 
> 
> --------------------------------------------------
> VERSION DETAILS
> --------------------------------------------------
> 
> v1.1.0 (Patch)
> 
> New / Changed:
> - Added "Manage Expenses" tab, available after a settlement is computed
> - Users can add new expense entries post-settlement using the same
>   fields as Manual Entry; results recalculate automatically
> - Every expense row now carries a "Settled" flag (defaults to False)
> - Users can mark any expense row as "Settled" via an editable table
> - Settled rows are excluded from Net Balances, Settlements, and
>   Breakdown calculations, but remain visible in the Preview tab
> - Preview tab now displays a Settled status indicator (✅ / —) per row
> - New utility function: get_active_df(df), which filters out rows
>   where Settled is True (safe no-op if the column doesn't exist)
> 
> 
> v1.0.0 (Initial Release)
> 
> Features included:
> - CSV upload with validation
> - Manual entry form
> - Balance computation
> - Settlement generation
> - Per-person breakdown view
> - Input validation with formatted feedback
> 
> 
> --------------------------------------------------
> MODULE RESPONSIBILITIES
> --------------------------------------------------
> 
> app.py
> - Handles user interface (Streamlit)
> - Manages session state
> - Displays tables and computation results
> - Provides post-settlement "Add Expense" and "Mark as Settled" UI
>   (Manage Expenses tab)
> 
> utils.py
> - Contains core logic
> - Handles validation, computation, and transformations
> - get_active_df(df) filters out settled rows before balance,
>   settlement, and breakdown calculations
> 
> 
> --------------------------------------------------
> HOW TO RUN
> --------------------------------------------------
> 
> From project root:
> 
>     streamlit run ui/app.py
> 
> 
> --------------------------------------------------
> INPUT REQUIREMENTS (CSV)
> --------------------------------------------------
> 
> Required columns:
> - Contributor
> - Item
> - Amount
> - Payor
> - Contribution %
> 
> Optional columns:
> - Settled
>   → Boolean-like value (true/false, yes/no, 1/0).
>   → If omitted, all uploaded rows default to unsettled (Settled = False).
>   → Rows marked Settled = True are excluded from balance,
>     settlement, and breakdown calculations.
> 
> Rules:
> - Amount must be numeric and greater than 0
> - Contribution % must be in decimal form (0.0 – 1.0)
>   Example: 0.25 = 25%
> - Total Contribution per (Item + Contributor) must not exceed 1.0
> - No empty values in key fields (Contributor, Item, Payor)
> 
> 
> ==============================
> SAMPLE DATA
> ==============================
> 
> Located in:
> sample_data/
> 
> This folder contains example CSV files to help users understand
> the expected input format and test the application.
> 
> Files included:
> 
> - template.csv  
>   → Blank template file with required column structure.
>   → Use this as a starting point for creating your own data.
> 
> - valid_test.csv  
>   → Example of correctly formatted data.
>   → Can be used to verify that the application works properly.
> 
> - invalid_test.csv  
>   → Example dataset that violates validation rules.
>   → Demonstrates how the application handles errors.
> 
> These files are optional and are not required to run the app,
> but are highly recommended for testing and onboarding.
> 
> 
> ==============================
> REQUIREMENTS
> ==============================
> 
> Python version:
> - Python 3.14.4
> 
> Libraries:
> - streamlit == 1.57.0
> - pandas == 3.0.2
> 
> Install dependencies:
> pip install -r requirements.txt
> 
> 
> --------------------------------------------------
> NOTES
> --------------------------------------------------
> 
> - Validation messages are summarized for readability
> - Errors highlight problematic entries clearly
> - Application prevents computation unless data is valid
> - Once a settlement is computed, expenses can still be added or
>   marked as settled without restarting the workflow
> 
> 
> --------------------------------------------------
> END OF DOCUMENT
> --------------------------------------------------