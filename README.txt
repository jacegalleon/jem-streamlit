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