import streamlit as st

# Simple Admin Panel with password access
def admin_login():
    """Admin login form with password protection."""
    st.subheader("🔒 Admin Login")

    password = st.text_input("Enter password:", type="password")
    if password == "mzadmin2025":
        st.session_state["admin_logged_in"] = True
        st.success("Access granted. Welcome, ing. Moca Zizic!")
    elif password:
        st.error("Incorrect password. Try again.")

def admin_panel():
    """Main admin dashboard content."""
    st.title("Admin Panel — MZ WALL DESIGNER PRO v2.0")
    st.caption("Created and designed by ing. Moca Zizic — 'always be ahead' (Modular thinking — smart construction)")

    st.markdown("### ⚙️ Options")
    st.write("1. View documentation")
    st.write("2. Manage saved projects")
    st.write("3. System information")
    st.write("4. (Reserved for future updates)")

    st.markdown("---")
    st.markdown("**© 2025 ing. Moca Zizic**")

def show_admin():
    """Wrapper to display admin access."""
    if "admin_logged_in" not in st.session_state or not st.session_state["admin_logged_in"]:
        admin_login()
    else:
        admin_panel()
