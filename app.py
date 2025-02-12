import streamlit as st
import Home  
import Complaints
import Billing   
import Other_mails
import Our_Team
from streamlit_carousel import carousel

st.set_page_config(
    page_title="arieoAI",
    page_icon="./static/mail-inbox.jpg"
)

valid_username = "admin"
valid_password = "password123"


query_params = st.query_params
if "logged_in" not in st.session_state:
    st.session_state.logged_in = query_params.get("logged_in", "False") == "True"

if "current_page" not in st.session_state:
    st.session_state.current_page = query_params.get("page", "Home") if st.session_state.logged_in else "Login"

if "show_login" not in st.session_state:
    st.session_state.show_login = False 
if "showLoginButton" not in st.session_state:
    st.session_state.showLoginButton = True  

# Carousel Images
items = [
    {"title": "", "text": "", "img": "./static/Insurance.jpg"},
    {"title": "", "text": "", "img": "./static/Complaints.jpg"},
    {"title": "", "text": "", "img": "./static/support.jpg"},
]

# Step 1: Show Login Form
def show_login_form():
    st.title("arieoAI Insurance")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username == valid_username and password == valid_password:
            st.session_state.logged_in = True
            st.session_state.show_login = False   
            st.session_state.showLoginButton = False  
            st.session_state.current_page = "Home"  
            st.query_params.update({"logged_in": "True", "page": "Home"})   
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")

# Step 2: Sidebar Navigation
def show_sidebar_navigation():
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center;">
                <a href="https://streamlit.io">
                    <img src="./app/static/mail-inbox.jpg" width="100">
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        selection = st.radio("", ["Home", "Complaints", "Billing", "Other mails","Our Team"], 
                             index=["Home", "Complaints", "Billing", "Other mails","Our Team"].index(st.session_state.current_page))
        
        st.query_params["page"] = selection  
        st.session_state.current_page = selection   
        
        st.markdown("---")  # Divider line
        if st.button("Logout", key="sidebar_logout"):
            logout()

    # ✅ Load the selected page
    if selection == "Home":
        Home.app()  
    elif selection == "Complaints":
        Complaints.app()
    elif selection == "Billing":
        Billing.app()
    elif selection == "Other mails":
        Other_mails.app()
    elif selection == "Our Team":
        Our_Team.app()

# Step 3: Logout Function
def logout():
    st.session_state.logged_in = False
    st.session_state.show_login = False   
    st.session_state.showLoginButton = True 
    st.session_state.current_page = "Login" 

    st.query_params.clear()
    st.query_params.update({"logged_in": "False"})

    st.success("You have been logged out.")  
    st.rerun()

# Main Function
def main():
    if not st.session_state.logged_in:
        st.query_params.update({"logged_in": "False"})  
        
        col1, col2 = st.columns([1, 5])  

        if st.session_state.showLoginButton and not st.session_state.show_login:
            with col1:
                if st.button("Login", key="top_left_login"):
                    st.session_state.showLoginButton = False 
                    st.session_state.show_login = True 
                    st.rerun()  

        if not st.session_state.show_login:
            with col2:
                carousel(items)  

        if st.session_state.show_login:
            show_login_form()

        # ✅ Show footer ONLY on login page
        st.markdown(
            """
            <style>
            .footer {
                position: fixed;
                bottom: 0;
                padding: 10px 0;
                text-align: center;
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
            .marquee {
                display: inline-block;
                overflow: hidden;
                animation: marquee 20s linear infinite;
            }
            @keyframes marquee {
                from { transform: translateX(100%); }
                to { transform: translateX(-100%); }
            }
            </style>
            <div class="footer">
                <span class="marquee">
                    📩 Email Insights: 
                    📌 Leads/Prospects |
                    🔧 Support Issues |
                    ⭐ Reviews/Complaints |
                    💰 Billing Activities |
                    🚀 AI Tools → LangChain, LangSmith for Email Automation
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        show_sidebar_navigation()  # No footer when navigating pages

if __name__ == "__main__":
    main()
