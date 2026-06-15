import sys
import pandas as pd
import streamlit as st
from pathlib import Path

# -------------------------
# Setup
# -------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / "src"))

from utils import (
    compute_balances,
    balances_to_df,
    settle_debts,
    get_person_breakdown,
    validate_csv,
    get_active_df,
)
APP_NAME = "💸 J.E.M – Jace's Expense Manager"

st.set_page_config(page_title=APP_NAME, layout="wide")
st.title(APP_NAME)

# -------------------------
# ✅ Session State
# -------------------------
if "master_df" not in st.session_state:
    st.session_state.master_df = None

if "computed" not in st.session_state:
    st.session_state.computed = False

if "delete_mode" not in st.session_state:
    st.session_state.delete_mode = False

if "data_df" not in st.session_state:
    st.session_state.data_df = None

if "manual_df" not in st.session_state:
    st.session_state.manual_df = pd.DataFrame(
        columns=["Contributor", "Item", "Amount", "Payor", "Contribution %"]
    )


# ✅ FIX: ALWAYS STORE MODE
if "mode" not in st.session_state:
    st.session_state.mode = "📁 Upload CSV"

# -------------------------
# ✅ TOP SWITCH AREA
# -------------------------
top_col1, top_col2 = st.columns([1, 4])

if st.session_state.computed:
    with top_col1:
        if st.button("🔄 From the start", key="reset_btn"):
            st.session_state.clear()
            st.rerun()

    with top_col2:
        st.success("✅ Results generated")

else:
    with top_col1:
        mode = st.radio(
            "Choose Input Method",
            ["📁 Upload CSV", "✍️ Manual Entry"],
            key="mode",   # ✅ this is the fix
            horizontal=True
        )


# -------------------------
# ✅ INPUT SECTION
# -------------------------
header_col, button_col = st.columns([4, 1])

with button_col:
    compute_clicked = st.button("💰 Compute Settlement", key="compute_btn")
    
    if compute_clicked:
        if st.session_state.data_df is None:
            st.warning("⚠️ Please upload a file or enter data first.")
        else:
            st.session_state.computed = True
            st.rerun()

if not st.session_state.computed:

    # -------------------------
    # Upload
    # -------------------------
    if mode == "📁 Upload CSV":
        with header_col:
            st.subheader("📁 Upload CSV")
    
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
    
            # ✅ RUN VALIDATION
            is_valid, message = validate_csv(df)
    
            if not is_valid:
                st.error(message)
                st.session_state.data_df = None
    
            else:
                st.session_state.master_df = df.copy()

                # ✅ Ensure every row has a "Settled" flag (new items default to unsettled)
                if "Settled" not in st.session_state.master_df.columns:
                    st.session_state.master_df["Settled"] = False
                else:
                    st.session_state.master_df["Settled"] = (
                        st.session_state.master_df["Settled"]
                        .astype(str)
                        .str.strip()
                        .str.lower()
                        .isin(["true", "1", "yes", "y"])
                    )

                st.session_state.data_df = st.session_state.master_df
    
                st.success("✅ File uploaded successfully")
    
                # ✅ Display formatted preview
                display_df = df.copy()
    
                display_df["Amount"] = display_df["Amount"].apply(
                    lambda x: f"{x:,.2f}"
                )
    
                display_df["Contribution %"] = display_df["Contribution %"].apply(
                    lambda x: f"{x:.0%}"
                )
    
                display_df.index += 1
    
                st.dataframe(display_df, use_container_width=True)

    # -------------------------
    # Manual
    # -------------------------
    elif mode == "✍️ Manual Entry":
    
        st.subheader("✍️ Manual Entry")
    
        # ✅ Reset compute mode when editing
        st.session_state.computed = False
    
        # ✅ Input Form
        with st.form("manual_entry_form", clear_on_submit=True):
    
            col1, col2 = st.columns(2)
    
            with col1:
                contributor = st.text_input("Contributor")
                item = st.text_input("Item")
                # ✅ Initialize flags for Amount
                amount_input = st.text_input("Amount")
                
                # ✅ Default value
                amount = 0.0
                amount_valid = True
                amount_error = ""
                
                # ✅ Validation flow
                if amount_input.strip() == "":
                    amount_valid = False
                    amount_error = "⚠️ Amount is required."
                
                else:
                    try:
                        amount = float(amount_input)
                
                        if amount <= 0:
                            amount_valid = False
                            amount_error = "⚠️ Amount must be greater than 0."
                
                    except:
                        amount_valid = False
                        amount_error = "⚠️ Amount should be a valid decimal number."
    
            with col2:
                payor = st.text_input("Payor")
                contribution = st.number_input(
                    "Contribution %",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0
                )
    
            submitted = st.form_submit_button("➕ Add Entry")
    
        # ✅ Add entry with validation
        if submitted:
    
            contributor_clean = contributor.strip()
            item_clean = item.strip()
            payor_clean = payor.strip()
    
            if (
                contributor_clean == "" or
                item_clean == "" or
                payor_clean == ""
            ):
                st.warning("⚠️ Please fill in all text fields.")
            
            elif not amount_valid:
                st.warning(amount_error)

            else:
                new_row = pd.DataFrame([{
                    "Contributor": contributor_clean,
                    "Item": item_clean,
                    "Amount": amount,
                    "Payor": payor_clean,
                    "Contribution %": contribution,
                    "🗑️": False  # ✅ include checkbox column
                }])
    
                st.session_state.manual_df = pd.concat(
                    [st.session_state.manual_df, new_row],
                    ignore_index=True
                )
    
        # ✅ Prepare table (ensure checkbox column exists)
        df = st.session_state.manual_df.copy()
    
        if "🗑️" not in df.columns:
            df["🗑️"] = False
    
        df["🗑️"] = df["🗑️"].fillna(False)
    
        # ✅ Render editable table with checkbox
        if len(df) > 0:
        
            manual_df = st.data_editor(
                df,
                key="manual_editor",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "🗑️": st.column_config.CheckboxColumn(
                        label="🗑️",
                        default=False,
                        help="Select rows to delete"
                    )
                }
            )
            
            # ✅ Always use THIS as source
            current_df = manual_df.copy()
            
            # ✅ ensure column exists (safe guard)
            if "🗑️" not in current_df.columns:
                current_df["🗑️"] = False
            
            current_df["🗑️"] = current_df["🗑️"].fillna(False)
        
            # ✅ Action buttons (fixed layout)
            col1, col2, col3 = st.columns([1, 1, 1.2])
        
            with col1:
                if st.button("🗑️ Remove Last Entry"):
                    st.session_state.manual_df = (
                        current_df.iloc[:-1]
                        .reset_index(drop=True)
                    )
                    st.rerun()
        
            with col2:
                if st.button("🔄 Reset Table"):
                    st.session_state.manual_df = pd.DataFrame(
                        columns=["Contributor", "Item", "Amount", "Payor", "Contribution %", "🗑️"]
                    )
                    st.session_state.data_df = None
                    st.rerun()
        
            with col3:
                # ✅ ALWAYS use latest state
                if current_df["🗑️"].any():
                    if st.button("❌ Delete Selected"):
                        cleaned = current_df[current_df["🗑️"] == False].reset_index(drop=True)
                        cleaned["🗑️"] = False
        
                        st.session_state.manual_df = cleaned
                        st.rerun()
                else:
                    st.empty()
    
        # ✅ Validation for compute
        df = st.session_state.manual_df
    
        if df.empty:
            st.session_state.data_df = None
        else:
            valid_rows = df[
                (df["Contributor"].astype(str).str.strip() != "") &
                (df["Payor"].astype(str).str.strip() != "") &
                (df["Item"].astype(str).str.strip() != "") &
                (pd.to_numeric(df["Amount"], errors="coerce") > 0)
            ]
    
            if not valid_rows.empty:
                master = df.copy()

                # ✅ Drop the manual-entry-only delete checkbox; not part of the dataset
                if "🗑️" in master.columns:
                    master = master.drop(columns=["🗑️"])

                # ✅ New entries start out unsettled
                if "Settled" not in master.columns:
                    master["Settled"] = False

                st.session_state.master_df = master.reset_index(drop=True)
                st.session_state.data_df = st.session_state.master_df

            else:
                st.session_state.data_df = None

# ✅ Compute trigger (FINAL SAFE VERSION ✅)
if compute_clicked:

    df = st.session_state.data_df
    required_cols = ["Contributor", "Payor", "Item", "Amount"]

    # ✅ Handle None or missing columns safely
    if df is None or not all(col in df.columns for col in required_cols):
        valid_rows = pd.DataFrame()

    else:
        df_check = df.copy()

        # ✅ Clean fields
        df_check["Contributor"] = df_check["Contributor"].astype(str).str.strip()
        df_check["Payor"] = df_check["Payor"].astype(str).str.strip()
        df_check["Item"] = df_check["Item"].astype(str).str.strip()
        df_check["Amount"] = pd.to_numeric(df_check["Amount"], errors="coerce")

        # ✅ Valid rows definition
        valid_rows = df_check[
            (df_check["Contributor"] != "") &
            (df_check["Payor"] != "") &
            (df_check["Item"] != "") &
            (df_check["Amount"].notna()) &
            (df_check["Amount"] > 0)
        ]

    # ✅ Unified validation (single message)
    if not valid_rows.empty:
        st.session_state.computed = True
        st.rerun()


# -------------------------
# ✅ RESULTS (TABS)
# -------------------------
if st.session_state.computed and st.session_state.data_df is not None:

    df = st.session_state.data_df

    # ✅ Items marked "Settled" are excluded from balances/settlements/breakdown
    active_df = get_active_df(df)

    tab_results, tab_manage, tab_preview = st.tabs(
        ["📊 Results", "⚙️ Manage Expenses", "📑 Preview"]
    )

    # -------------------------
    # ✅ RESULTS TAB
    # -------------------------
    with tab_results:

        balances = compute_balances(active_df)
        balances_df = balances_to_df(balances)
        settlements_df = settle_debts(balances)

        display_balances = balances_df.copy()
        display_balances["Net Balance"] = display_balances["Net Balance"].apply(
            lambda x: f"{x:,.2f}"
        )
        display_balances.index += 1

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            st.subheader("✅ Net Balances")
            st.dataframe(display_balances, use_container_width=True)

        with col2:
            st.subheader("💸 Settlements")

            if settlements_df is not None and not settlements_df.empty and "Amount" in settlements_df.columns:

                display_settlements = settlements_df.copy()

                display_settlements["Amount"] = display_settlements["Amount"].apply(
                    lambda x: f"{x:,.2f}"
                )

                display_settlements.index += 1

                st.dataframe(display_settlements, use_container_width=True)

            else:
                st.info("No settlements to display.")

        with col3:
            header_col, dropdown_col = st.columns([2, 3])

            with header_col:
                st.subheader("🔎 Breakdown")

            with dropdown_col:
                people = sorted(set(df["Contributor"]).union(set(df["Payor"]))
                )
                options = ["Select Person"] + people

                selected_person = st.selectbox(
                    "",
                    options,
                    key="person_selector"
                )

            if selected_person != "Select Person":
                breakdown_df = get_person_breakdown(active_df, selected_person)

                if breakdown_df.empty:
                    st.info("No unsettled items for this person.")
                else:
                    display_breakdown = breakdown_df.copy()
                    display_breakdown["Amount"] = display_breakdown["Amount"].apply(
                        lambda x: f"{x:,.2f}"
                    )
                    display_breakdown.index += 1

                    st.dataframe(display_breakdown, use_container_width=True)

                    st.write(
                        f"💰 Paid: {breakdown_df[breakdown_df['Type']=='Credit']['Amount'].sum():,.2f}"
                    )
                    st.write(
                        f"💸 Owed: {breakdown_df[breakdown_df['Type']=='Debit']['Amount'].sum():,.2f}"
                    )

            else:
                st.info("Select a person to view breakdown")

    # -------------------------
    # ✅ MANAGE EXPENSES TAB
    # -------------------------
    with tab_manage:

        # -------------------------
        # ➕ Add a new expense (post-settlement)
        # -------------------------
        st.subheader("➕ Add New Expense")
        st.caption(
            "Add an expense the same way as Manual Entry. "
            "It will be included automatically in the results above."
        )

        with st.form("post_settlement_entry_form", clear_on_submit=True):

            ps_col1, ps_col2 = st.columns(2)

            with ps_col1:
                ps_contributor = st.text_input("Contributor", key="ps_contributor")
                ps_item = st.text_input("Item", key="ps_item")
                ps_amount_input = st.text_input("Amount", key="ps_amount")

            with ps_col2:
                ps_payor = st.text_input("Payor", key="ps_payor")
                ps_contribution = st.number_input(
                    "Contribution %",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    key="ps_contribution"
                )

            ps_submitted = st.form_submit_button("➕ Add Expense")

        if ps_submitted:

            ps_contributor_clean = ps_contributor.strip()
            ps_item_clean = ps_item.strip()
            ps_payor_clean = ps_payor.strip()

            # ✅ Same validation flow as Manual Entry
            ps_amount = 0.0
            ps_amount_valid = True
            ps_amount_error = ""

            if ps_amount_input.strip() == "":
                ps_amount_valid = False
                ps_amount_error = "⚠️ Amount is required."
            else:
                try:
                    ps_amount = float(ps_amount_input)

                    if ps_amount <= 0:
                        ps_amount_valid = False
                        ps_amount_error = "⚠️ Amount must be greater than 0."

                except ValueError:
                    ps_amount_valid = False
                    ps_amount_error = "⚠️ Amount should be a valid decimal number."

            if (
                ps_contributor_clean == "" or
                ps_item_clean == "" or
                ps_payor_clean == ""
            ):
                st.warning("⚠️ Please fill in all text fields.")

            elif not ps_amount_valid:
                st.warning(ps_amount_error)

            else:
                new_row = pd.DataFrame([{
                    "Contributor": ps_contributor_clean,
                    "Item": ps_item_clean,
                    "Amount": ps_amount,
                    "Payor": ps_payor_clean,
                    "Contribution %": ps_contribution,
                    "Settled": False,
                }])

                st.session_state.master_df = pd.concat(
                    [st.session_state.master_df, new_row],
                    ignore_index=True
                )
                st.session_state.data_df = st.session_state.master_df

                st.success("✅ Expense added")
                st.rerun()

        st.divider()

        # -------------------------
        # ✅ Mark items as settled
        # -------------------------
        st.subheader("✅ Mark Items as Settled")
        st.caption(
            "Tick 'Settled' for items that have already been paid back. "
            "Settled items are excluded from the Net Balances, Settlements, "
            "and Breakdown shown in the Results tab."
        )

        manage_df = st.session_state.master_df.copy().reset_index(drop=True)

        if "Settled" not in manage_df.columns:
            manage_df["Settled"] = False

        manage_df["Settled"] = manage_df["Settled"].fillna(False).astype(bool)

        display_cols = ["Contributor", "Item", "Amount", "Payor", "Contribution %", "Settled"]
        manage_df = manage_df[[c for c in display_cols if c in manage_df.columns]]

        if manage_df.empty:
            st.info("No expenses to manage yet.")
        else:
            edited_settle_df = st.data_editor(
                manage_df,
                key="settle_editor",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Settled": st.column_config.CheckboxColumn(
                        label="✅ Settled",
                        default=False,
                        help="Check to exclude this item from the balance calculation",
                    ),
                },
                disabled=[c for c in manage_df.columns if c != "Settled"],
            )

            if st.button("🔄 Apply Settled Status", key="apply_settled_btn"):
                st.session_state.master_df = edited_settle_df.copy()
                st.session_state.data_df = st.session_state.master_df
                st.success("✅ Updated — recalculating balances...")
                st.rerun()

    # -------------------------
    # ✅ PREVIEW TAB
    # -------------------------
    with tab_preview:

        preview_df = df.copy()
        preview_df["Amount"] = preview_df["Amount"].apply(
            lambda x: f"{x:,.2f}"
        )
        preview_df["Contribution %"] = preview_df["Contribution %"].apply(
            lambda x: f"{x:.0%}"
        )

        if "Settled" in preview_df.columns:
            preview_df["Settled"] = preview_df["Settled"].apply(
                lambda x: "✅" if bool(x) else "—"
            )

        preview_df.index += 1

        st.dataframe(preview_df, use_container_width=True)