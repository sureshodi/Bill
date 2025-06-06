import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime
import os

# Load products from CSV
@st.cache_data
def load_products():
    df = pd.read_csv("products.csv")
    return df.set_index("product_code").T.to_dict()

product_dict = load_products()

st.title("🎆 Crackers Wholesale Billing App")

# Input table
if "entries" not in st.session_state:
    st.session_state.entries = []

with st.form("add_form"):
    col1, col2 = st.columns(2)
    code = col1.text_input("Enter Product Code").strip().upper()
    qty = col2.number_input("Enter Quantity", min_value=1, step=1)

    submitted = st.form_submit_button("Add Item")
    if submitted:
        if code not in product_dict:
            st.error(f"❌ Product code '{code}' not found.")
        else:
            prod = product_dict[code]
            name = prod['product_name']
            price = prod['price']
            total = price * qty
            st.session_state.entries.append({
                "code": code,
                "name": name,
                "price": price,
                "qty": qty,
                "total": total
            })

# Show bill items
if st.session_state.entries:
    st.subheader("🧾 Bill Items")
    df = pd.DataFrame(st.session_state.entries)
    st.table(df[["code", "name", "price", "qty", "total"]])
    total_amt = df["total"].sum()
    st.markdown(f"### ✅ Total: ₹{total_amt}")

    if st.button("Generate Bill"):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        txt_filename = f"bill_{timestamp}.txt"
        pdf_filename = f"bill_{timestamp}.pdf"

        # Save text bill
        with open(txt_filename, "w") as f:
            f.write("==== Wholesale Crackers Bill ====\n")
            for e in st.session_state.entries:
                f.write(f"{e['code']} - {e['name']} - ₹{e['price']} x {e['qty']} = ₹{e['total']}\n")
            f.write(f"\nTOTAL: ₹{total_amt}\n")

        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Wholesale Crackers Bill", ln=True, align='C')
        for e in st.session_state.entries:
            line = f"{e['code']} - {e['name']} - ₹{e['price']} x {e['qty']} = ₹{e['total']}"
            pdf.cell(200, 10, txt=line, ln=True)
        pdf.cell(200, 10, txt=f"TOTAL: ₹{total_amt}", ln=True)
        pdf.output(pdf_filename)

        with open(txt_filename, "rb") as f:
            st.download_button("⬇️ Download Text Bill", f, txt_filename)

        with open(pdf_filename, "rb") as f:
            st.download_button("⬇️ Download PDF Bill", f, pdf_filename)

        # Optional: clear old entries
        st.session_state.entries = []

else:
    st.info("Add products to begin billing.")
