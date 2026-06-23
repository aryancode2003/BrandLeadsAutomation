import streamlit as st
import pandas as pd
import io
import os
import time
import json
from datetime import datetime

# ==========================================
# PAGE CONFIGURATION (Must be first)
# ==========================================
st.set_page_config(page_title="Multi-Brand Lead Portal", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# BENTO GRID UI/UX CSS INJECTION 
# ==========================================
st.markdown("""
    <style>
    /* Global Workspace Background */
    .stApp { background-color: #F4F7FE; font-family: 'Inter', sans-serif; color: #0F172A; }
    
    /* Ensure all main area headings are visible and dark */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 { color: #0F172A !important; font-weight: 800; letter-spacing: -0.5px; }
    
    /* Dark Modern Sidebar */
    [data-testid="stSidebar"] { background-color: #111827; }
    [data-testid="stSidebar"] * { color: rgba(255, 255, 255, 0.85) !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
    
    /* Hide Default Headers */
    header {visibility: hidden;} footer {visibility: hidden;}
    
    /* ========================================= */
    /* BENTO CARD DESIGNS                        */
    /* ========================================= */
    
    .bento-card {
        background: #FFFFFF; 
        border-radius: 24px; 
        padding: 2rem; 
        text-align: center;
        box-shadow: 0px 4px 24px rgba(0, 0, 0, 0.04); 
        transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), box-shadow 0.3s ease;
        border: 1px solid #E2E8F0; 
        cursor: pointer; 
        margin-bottom: 1.5rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%;
    }
    .bento-card:hover { 
        transform: translateY(-5px); 
        box-shadow: 0px 15px 35px rgba(54, 153, 255, 0.1); 
        border-color: #3699FF; 
    }
    
    .brand-title { font-size: 1.8rem; font-weight: 800; color: #0F172A !important; margin-bottom: 0.3rem; }
    
    /* Login Container (Bento Style) */
    .login-container { 
        max-width: 420px; 
        margin: 3rem auto; 
        padding: 3rem 2.5rem; 
        background: #FFFFFF; 
        border-radius: 24px; 
        box-shadow: 0px 10px 40px rgba(0, 0, 0, 0.06); 
        border: 1px solid #E2E8F0;
    }
    
    /* Primary Pill Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        color: white !important; 
        border-radius: 50px; /* Pill Shape */
        font-weight: 700; 
        border: none; 
        padding: 0.6rem 2rem;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3); 
        transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4); }
    
    /* Outline Buttons */
    .btn-outline>button { 
        background: transparent !important; 
        color: #0F172A !important; 
        border: 2px solid #E2E8F0 !important; 
        box-shadow: none !important; 
        border-radius: 50px;
    }
    .btn-outline>button:hover { background: #F1F5F9 !important; border-color: #CBD5E1 !important; }
    
    /* Bento Metric Blocks */
    .metric-bento {
        background: #FFFFFF; 
        padding: 1.8rem; 
        border-radius: 24px; 
        box-shadow: 0px 4px 20px rgba(0,0,0,0.03);
        border: 1px solid #E2E8F0; 
        margin-bottom: 1.5rem;
        text-align: left;
    }
    .metric-icon { font-size: 2.2rem; margin-bottom: 12px; }
    .metric-bento h3 { color: #64748B !important; font-size: 0.85rem; margin-bottom: 0.2rem; text-transform: uppercase; font-weight: 700; letter-spacing: 1px;}
    .metric-bento h2 { color: #0F172A !important; font-size: 2.8rem; font-weight: 800; margin: 0; line-height: 1;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. FILE SYSTEM & DATABASE SETUP
# ==========================================
CONFIG_FILE = "brands_config.json"
LOG_FILE = "usage_logs.csv"

# SET YOUR PASSWORDS HERE
USER_DATABASE = {
    "admin@jungleworks.com": {"password": "admin", "role": "superadmin", "brand": "ALL"},
    "aryan.srivastava@jungleworks.com": {"password": "Aryan@123", "role": "user", "brand": "FATAFAT"},
    "anshul.mehra@jungleworks.com": {"password": "Jugnoo123", "role": "user", "brand": "JUGNOO"},
    "riya.arora@jungleworks.com": {"password": "Solobeauty123", "role": "user", "brand": "SOLO BEAUTY"}
}

DEFAULT_BRANDS = {
    "FATAFAT": {
        "name": "FATAFAT", 
        "lost_cities": [
            "Adipur", "Agartala", "Ahmedabad", "Akola", "Aligarh", "Alipurduar", "Alwar", "Ambejogai", 
            "Amravati", "Amritsar", "Asansol", "Ashoka Nagar", "Ashta", "Azamgarh", "Baddi", "Bahraich", 
            "Balasore", "Ballari", "Banka", "Bardhaman", "Baripada", "Basti", "Bazpur", "Beawar", "Betul", 
            "Bhaderwah", "Bhagalpur", "Bhandara", "Bhiwani", "Bilaspur", "Bishanpura", "Brahmapur", "Burhar", 
            "Chamba", "Chanchal", "Chunar", "Coimbatore", "Contai", "Cuttack", "Daltonganj", "Darbhanga", 
            "Dewas", "Dharamshala", "Dharmanagar", "Dimapur", "Dinhata", "Doda", "Dumka", "Durgapur", "Erode", 
            "Faridabad", "Faridkot", "Farrukhabad", "Fatehgarh", "Firozabad", "Ganderbal", "Gandhidham", "Gondia", 
            "Gora Bazar", "Guntur", "Gurugram", "Guruvayur", "Gwalior", "Hailakandi", "Hamirpur", "Haridwar", 
            "Hazaribagh", "Hyderabad", "Imphal", "Islampur", "Jagadhri", "Jaisalmer", "Jalandhar", "Jammu", 
            "Jamshedpur", "Jangipur", "Jhunjhunu", "Jodhpur", "Jorhat", "Kadapa", "Kakinada", "Kalyan", "Kangra", 
            "Karimnagar", "Karnal", "Kathua", "Keonjhar", "KGF", "Khordha", "Kishanganj", "Kishangarh", "Kot Kapura", 
            "Kumarghat", "Kunda", "Kurukshetra", "Lakhimpur Kheri", "Latur", "Ludhiana", "Madurai", "Mahendragarh", 
            "Maheshwarpur", "Mahoba", "Malda", "Manali", "Manawar", "Manipal", "Mau", "Meerut", "Midnapore", 
            "Mohali", "Moradabad", "Motihari", "Nagpur", "Navi Mumbai", "Nimbahera", "Noida", "Nuh", "Orai", 
            "Outer Ahmedabad", "Outer Patna", "Pali", "Panipat", "Paonta Sahib", "Pathankot", "Patna", 
            "Perinthalmanna", "Phalodi", "Port Blair", "Prakasam", "Prayagraj", "Puducherry", "Pune", "Puri", 
            "Rampur", "Rampurhat", "Ranchi", "Rawatbhata", "Reasi", "Robertsganj", "Rohini", "Rohru", "Roorkee", 
            "Sangareddy", "Sangli", "Saraipali", "Sasaram", "Shahdol", "Shahjahanpur", "Shamli", "Shimla", 
            "Shivpuri", "Shujalpur", "Silchar", "Siliguri", "Singhana", "Singur", "Sirohi", "Sirsa", "Solan", 
            "Solapur", "Sonipat District", "Srinagar", "Sundernagar", "Suri", "Tarn Taran", "Tezpur", "Thane", 
            "Tinsukia", "Umarkhed", "Una", "Unnao", "Vadodara", "Waidhan", "Yamunanagar"
        ]
    },
    "JUGNOO": {
        "name": "JUGNOO", 
        "lost_cities": [
            "Vadodara", "Guwahati", "Jaipur", "Srinagar", "Nagercoil", "Bhopal", "Ludhiana", "Faridabad", "Chandigarh", "Mohali", 
            "Sagar", "Rewa", "Dewas", "Kanniyakumari", "Mau", "Raipur", "Daman", "Vapi", "Nagpur", "Rajkot", "Bijnor", "Meerut", 
            "Muzaffarnagar", "Coimbatore", "Deoghar", "Lucknow", "Kanpur", "Pune", "Gorakhpur", "Kalaburagi", "Barabanki", "Ratlam", 
            "Kozhikode", "Betul", "Chhindwara", "Dharmanagar", "Thucklay", "Padmanabhapuram", "Marthandam", "Derabassi", "Durgapur", 
            "Kharar", "Pinjore", "Koraput", "Navi Mumbai", "Kollam", "Sumerpur", "Nagaon", "Balaghat", "Rudrapur", "Una", "Baddi", 
            "Shimla", "Thrissur", "Cooch Bihar", "Imphal", "Dharamshala", "Manali", "Gondia", "Ernakulam", "Kodagu", "Dindigul", 
            "Patiala", "Barwani", "Dhar", "Dhanbad", "Chapra", "Waidan", "Bidar", "Kamareddy", "Nanded", "Pathankot", "Hajipur", 
            "Goalpara", "Balasore", "Puri", "Karimnagar", "Hassan", "Ahmedabad", "Baripada", "Kannur", "Shamli", "Mirzapur", "Jaunpur", 
            "Bhadohi", "Tuticorin", "Ramanathapuram", "Thoubal", "Karimganj", "Doddaballapura", "Nandi Hills", "Godda", "Delhi", 
            "New Delhi", "Gurgaon", "Gurugram", "Noida", "Greater Noida", "Baleswar", "Belgaum", "Calicut", "Midnapore", "Daltonganj", 
            "Barotiwala", "Nalagarh", "Hyderabad", "Bangalore", "Chennai", "Kolkata", "Bengaluru", "Mumbai", "Shahdol", "Kottayam", 
            "Dehri-on-Sone", "Ghaziabad", "Kamrup", "Madanapalle", "Aizawl", "Udaipur", "Narmadapuram", "Bathinda", "Jalgaon", 
            "Waidhan", "Biswanath", "Bandikui", "Ganjam", "Bareilly", "Dhemaji", "Bahraich", "Bhuj", "Gandhidham", "Kutch", "Dhubri", 
            "Kohima", "Nalanda", "Dinhata", "Beawar", "Sitamarhi", "Alipurduar", "Hazaribagh", "Barbil", "Ballia", "Joda", "Bhubaneswar", 
            "Bhadrak", "Palamu", "Mathura", "Vrindavan", "Basti", "Saharsa", "Tarn Taran", "Madurai", "Orai", "Rajouri", "Begusarai", 
            "Kushinagar", "Khatu Shyam", "Dombivli", "Gwalior", "Satara", "Sundar Nagar", "Singrauli", "Surat", "Vikasnagar", "Dimapur", 
            "Rapar", "Katihar", "Vijayapura", "Ajmer", "Gir Somnath", "Moga", "Jharsuguda", "Dwarka", "Madhubani", "Jaisalmer", 
            "Gulbarga", "Huancayo", "Bharuch", "Khanna", "Morbi", "Indore", "Ankleshwar", "Bankura", "Purulia", "Murshidabad", "Haridwar", 
            "Raiganj", "Dalkhola", "Asansol", "Sri Muktsar Sahib", "Bhavnagar", "Malerkotla", "Sangrur", "Barnala", "Raichur", "Palghar", 
            "Vasai", "Dungarpur", "Champawat", "Khatima", "Malviya Nagar", "Arambagh", "Harda", "Gandhinagar", "Hosur", "Naharlagun", 
            "Kishtwar", "Doda", "Ambikapur", "Dar es Salaam", "Ziro", "Malegaon", "Dhule", "Aurangabad", "Bikaner", "Roorkee", 
            "Kharagpur", "Prakasam", "Udgir", "Hojai", "Jalore", "Bhinmal", "Gangapur", "Sonipat", "Addanki", "Saket", "New Town", 
            "Jabalpur", "Kandukur", "Chimakurthi", "Tangutur", "Kothapatnam", "Ahore", "Sayla", "Lanka", "Itanagar", "Kolhapur", 
            "Belagavi", "Jamshedpur", "Dausa", "Karauli", "Rishikesh", "Tirupati", "Secunderabad", "Jaleswar", "Purnia", "Sangli", 
            "Junagadh", "Jhargram", "Godhra", "Bilaspur", "Medchal-Malkajgiri", "Kanyakumari", "Umaria", "Panipat", "Varanasi", 
            "Ayodhya", "Haldia", "Khordha", "Bagodar"
        ]
    },
    "SOLO BEAUTY": {
        "name": "SOLO BEAUTY", 
        "lost_cities": [
            "Hozabad", "Vapi", "Deoria", "Rajkot", "Ajmer", "Udham Singh Nagar", "Rudrapur", "Nagpur", "Bhopal", 
            "Navi Mumbai", "Panipat", "Bhubaneswar", "Gwalior", "Jammu", "Ghaziabad", "Agra", "Jabalpur", "Mathura", 
            "Jalandhar", "Noida", "Secunderabad", "Muzaffarpur", "Asansol", "Silchar", "Mandi", "Ayodhya", "Balasore", 
            "Zirakpur", "Patna", "Etawah", "Kolkata", "South Kolkata", "East Kolkata", "Pune", "Vadodara", "Vijayawada", 
            "Allahabad", "Muzaffarnagar", "Lucknow", "Varanasi", "Jodhpur", "Indore", "Udaipur", "Guntur", "Gorakhpur", 
            "Kashipur", "Gurgaon", "Amritsar", "Hyderabad", "Jaipur", "Kanpur", "Bhagalpur", "Sonipat", "Ahmedabad", 
            "Orai", "Bharatpur", "Firozabad"
        ]
    }
}

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as f: json.dump(DEFAULT_BRANDS, f, indent=4)

if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["Timestamp", "User_Email", "Brand", "Action", "Total_Leads", "File_Name"]).to_csv(LOG_FILE, index=False)

def load_config():
    with open(CONFIG_FILE, "r") as f: return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w") as f: json.dump(data, f, indent=4)

def log_activity(email, brand, action, leads_count, file_name):
    new_log = pd.DataFrame([{
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "User_Email": email, "Brand": brand, "Action": action,
        "Total_Leads": leads_count, "File_Name": file_name
    }])
    new_log.to_csv(LOG_FILE, mode='a', header=False, index=False)

brand_configs = load_config()

# ==========================================
# 2. SESSION STATE
# ==========================================
if 'step' not in st.session_state: st.session_state.step = "brand_selection"
if 'selected_brand' not in st.session_state: st.session_state.selected_brand = ""
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_role = ""

# ==========================================
# STEP 1: BRAND SELECTION SCREEN
# ==========================================
if st.session_state.step == "brand_selection":
    st.markdown("<h1 style='text-align:center; margin-top:4rem; font-size: 3rem;'>⚡ Select Your Workspace</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#64748B; margin-bottom:4rem; font-size: 1.1rem;'>Choose a brand portal to continue</p>", unsafe_allow_html=True)
    
    brands_list = list(brand_configs.keys())
    cols = st.columns(len(brands_list))
    
    for idx, brand in enumerate(brands_list):
        with cols[idx]:
            st.markdown(f"<div class='bento-card'><div class='brand-title'>{brand}</div><span style='color:#64748B; font-weight: 500;'>Lead Engine</span></div>", unsafe_allow_html=True)
            if st.button(f"Enter {brand}", key=f"btn_{brand}", use_container_width=True):
                st.session_state.selected_brand = brand
                st.session_state.step = "login"
                st.rerun()
    st.stop()

# ==========================================
# STEP 2: LOGIN SCREEN
# ==========================================
elif st.session_state.step == "login":
    brand = st.session_state.selected_brand
    st.markdown(f"<h1 style='text-align:center; margin-top:3rem; font-size: 2.5rem;'>{brand} Portal</h1>", unsafe_allow_html=True)
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    with st.form("login_form"):
        st.markdown("<h3 style='margin-bottom: 1.5rem;'>🔐 Secure Login</h3>", unsafe_allow_html=True)
        email_input = st.text_input("Email Address")
        password_input = st.text_input("Password", type="password")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("Authenticate", use_container_width=True):
            if email_input in USER_DATABASE and USER_DATABASE[email_input]["password"] == password_input:
                user_brand = USER_DATABASE[email_input]["brand"]
                if user_brand == brand or user_brand == "ALL":
                    st.session_state.logged_in, st.session_state.user_email, st.session_state.user_role = True, email_input, USER_DATABASE[email_input]["role"]
                    st.session_state.step = "main_portal"
                    log_activity(email_input, brand, "Logged In", 0, "N/A")
                    st.rerun()
                else: st.error(f"Access Denied: Not authorized for {brand}.")
            else: st.error("Invalid credentials.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='btn-outline' style='text-align:center;'>", unsafe_allow_html=True)
    if st.button("← Back to Workspaces"):
        st.session_state.step, st.session_state.selected_brand = "brand_selection", ""
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# STEP 3: MAIN PORTAL & DYNAMIC LOGIC ENGINES
# ==========================================
elif st.session_state.step == "main_portal":
    active_brand = st.session_state.selected_brand
    brand_data = brand_configs.get(active_brand, DEFAULT_BRANDS["FATAFAT"])

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"<h1 style='text-align:center; color:#3B82F6 !important; font-size:2.2rem;'>{active_brand}</h1>", unsafe_allow_html=True)
        if st.session_state.user_role == "superadmin":
            st.divider()
            st.markdown("🛠️ **Super Admin Actions**")
            new_brand = st.selectbox("Quick Switch:", list(brand_configs.keys()), index=list(brand_configs.keys()).index(active_brand))
            if new_brand != active_brand:
                st.session_state.selected_brand = new_brand
                st.rerun()
                
        st.divider()
        st.markdown(f"👤 **{st.session_state.user_email}**\n\n🛡️ **{st.session_state.user_role.upper()}**")
        st.markdown("<div class='btn-outline'>", unsafe_allow_html=True)
        if st.button("🔄 Change Workspace", use_container_width=True):
            st.session_state.step, st.session_state.logged_in = "brand_selection", False
            st.rerun()
        st.markdown("</div><br>", unsafe_allow_html=True)
        if st.button("🚪 Secure Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # --- TABS ---
    st.markdown(f"<h1 style='font-size: 2.5rem; margin-bottom: 1.5rem;'>{active_brand} Operations</h1>", unsafe_allow_html=True)
    if st.session_state.user_role == "superadmin":
        tab_proc, tab_brand_mgr, tab_logs = st.tabs(["📊 Lead Engine", "⚙️ Brand Settings", "📈 Global Logs"])
    else:
        tab_proc, = st.tabs(["📊 Lead Engine"])

    # --- TAB 1: PROCESSOR ---
    with tab_proc:
        
        with st.expander("📝 View / Edit Active Sold-Out Cities for this Upload"):
            joined_cities = ", ".join(brand_data["lost_cities"])
            st.info("💡 You can manually add or remove cities here before uploading your file. It will only apply to this session.")
            live_cities_input = st.text_area("Live Database Grid (Comma Separated):", value=joined_cities, height=150)
            
        active_lost_set = {c.strip().lower() for c in live_cities_input.split(",") if c.strip()}

        uploaded_file = st.file_uploader(f"Upload Raw Leads for {active_brand}", type=["csv", "txt"])

        if uploaded_file is not None:
            try:
                with st.spinner("Executing Brand-Specific Logic..."):
                    try:
                        df = pd.read_csv(uploaded_file, sep='\t', encoding='utf-16')
                    except UnicodeError:
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file, sep='\t', encoding='utf-8')
                    except Exception:
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file)
                    
                    df.columns = df.columns.str.lower().str.strip()

                    df_transformed = pd.DataFrame()
                    df_transformed['City'] = df['city'] if 'city' in df.columns else ""
                    df_transformed['Country'] = 'India'
                    df_transformed['Contact Name'] = df['full_name'] if 'full_name' in df.columns else ""
                    df_transformed['Contact Email'] = df['email'] if 'email' in df.columns else ""
                    
                    if 'phone_number' in df.columns:
                        cleaned_phones = df['phone_number'].astype(str).str.replace(r'\D', '', regex=True)
                        df_transformed['Contact Phone Number'] = cleaned_phones.apply(lambda x: f"{x}" if pd.notnull(x) else "")
                    elif 'phone' in df.columns:
                        cleaned_phones = df['phone'].astype(str).str.replace(r'\D', '', regex=True)
                        df_transformed['Contact Phone Number'] = cleaned_phones.apply(lambda x: f"{x}" if pd.notnull(x) else "")
                    else:
                        df_transformed['Contact Phone Number'] = ""
                    
                    df_transformed['Deal Owner Email ID'] = 'anshul.mehra@jungleworks.com'
                    df_transformed['Pipeline'] = active_brand 
                    df_transformed['Tags'] = 'Brands-Franchise'
                    df_transformed['Deal Status'] = 'Open'

                    # =====================================
                    # DYNAMIC BRAND LOGIC BRANCHING
                    # =====================================
                    if active_brand == "FATAFAT":
                        def determine_utm_fatafat(row):
                            val = str(row.iloc[12]).lower() + " " + str(row.iloc[13]).lower() if len(row) > 13 else ""
                            return 'as_a_delivery_boy' if any(k in val for k in ['driver', 'merchant', 'driving', 'job', 'delivery']) else 'as_a_franchise_owner'
                        df_transformed['Utm Content'] = df.apply(determine_utm_fatafat, axis=1)
                        if 'full_name' in df.columns: df_transformed['Note'] = 'Join ' + df_transformed['Utm Content'] + ' in ' + df['full_name'].astype(str)
                        if 'platform' in df.columns: df_transformed['Source'] = df['platform'].map({'fb': 'Facebook', 'ig': 'Instagram'}).fillna('Other')
                        df_transformed['investment'] = ''

                    elif active_brand == "JUGNOO":
                        def determine_utm_jugnoo(row):
                            val_m = str(row.iloc[12]).lower() if len(row) > 12 else ""
                            val_n = str(row.iloc[13]).lower() if len(row) > 13 else ""
                            combined_vals = val_m + " " + val_n
                            if any(k in combined_vals for k in ['driver', 'merchant', 'driving', 'job', 'delivery']):
                                return 'as_a_delivery_boy'
                            return 'as_a_franchise_owner'
                            
                        df_transformed['Utm Content'] = df.apply(determine_utm_jugnoo, axis=1)
                        if 'full_name' in df.columns: df_transformed['Note'] = 'Want to join ' + df_transformed['Utm Content'] + ' in ' + df['full_name'].astype(str)
                        df_transformed['Source'] = 'Facebook' 
                        df_transformed['investment'] = df.iloc[:, 13].astype(str) if df.shape[1] > 13 else ""

                    elif active_brand == "SOLO BEAUTY":
                        df_transformed['Utm Content'] = 'as_a_franchise_owner_owner'
                        if 'full_name' in df.columns: df_transformed['Note'] = 'Want to join ' + df_transformed['Utm Content'] + ' in ' + df['full_name'].astype(str)
                        df_transformed['Source'] = 'Facebook'
                        df_transformed['investment'] = df.iloc[:, 12].astype(str).str.lower().str.strip() if df.shape[1] > 12 else ""
                    # =====================================

                    # UNIVERSAL STAGE ENGINE
                    def determine_stage(row, lost_set, brand):
                        raw_city = str(row['City']).strip().lower()
                        if brand == "SOLO BEAUTY":
                            if str(row.get('investment', '')).lower() == 'no': return 'Driver/Merchant'
                            if raw_city in lost_set or raw_city.split('(')[0].strip() in lost_set: return 'Lost'
                            return 'Fresh Lead'
                        if row.get('Utm Content') == 'as_a_delivery_boy': return 'Driver/Merchant'
                        if raw_city in lost_set or raw_city.split('(')[0].strip() in lost_set: return 'Lost'
                        return 'Fresh Lead'
                        
                    df_transformed['Stage'] = df_transformed.apply(lambda r: determine_stage(r, active_lost_set, active_brand), axis=1)
                    
                    cols = ['Country', 'City', 'Contact Name', 'Contact Email', 'Contact Phone Number', 
                            'Deal Owner Email ID', 'Pipeline', 'Stage', 'Tags', 'Deal Status', 
                            'Note', 'Source', 'Utm Content', 'investment']
                    df_transformed = df_transformed[cols]
                    
                    if active_brand == "SOLO BEAUTY":
                        df_transformed.rename(columns={'investment': 'Investment'}, inplace=True)

                # DYNAMIC BENTO METRIC RENDERER
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                with m_col1: 
                    st.markdown(f"<div class='metric-bento'><div class='metric-icon'>👥</div><h3>Total Leads</h3><h2>{len(df_transformed)}</h2></div>", unsafe_allow_html=True)
                with m_col2: 
                    st.markdown(f"<div class='metric-bento'><div class='metric-icon'>🏢</div><h3>Fresh Leads</h3><h2>{len(df_transformed[df_transformed['Stage'] == 'Fresh Lead'])}</h2></div>", unsafe_allow_html=True)
                with m_col3: 
                    st.markdown(f"<div class='metric-bento'><div class='metric-icon'>🛑</div><h3>Auto-Lost</h3><h2>{len(df_transformed[df_transformed['Stage'] == 'Lost'])}</h2></div>", unsafe_allow_html=True)
                
                if active_brand == "SOLO BEAUTY":
                    with m_col4: 
                        st.markdown(f"<div class='metric-bento'><div class='metric-icon'>📉</div><h3>No Investment</h3><h2>{len(df_transformed[df_transformed['Stage'] == 'Driver/Merchant'])}</h2></div>", unsafe_allow_html=True)
                else:
                    with m_col4: 
                        st.markdown(f"<div class='metric-bento'><div class='metric-icon'>🛵</div><h3>Delivery</h3><h2>{len(df_transformed[df_transformed['Stage'] == 'Driver/Merchant'])}</h2></div>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df_transformed, use_container_width=True, height=300)
                
                st.download_button(
                    label=f"📥 Download {active_brand} Processed Leads",
                    data=df_transformed.to_csv(index=False, encoding='utf-8'),
                    file_name=f"{active_brand}_Leads_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    on_click=log_activity,
                    args=(st.session_state.user_email, active_brand, "Processed CSV", len(df_transformed), uploaded_file.name)
                )
            except Exception as e:
                st.error(f"Processing Error: Please verify this is a valid {active_brand} raw file. Details: {e}")

    # --- TAB 2: BRAND MANAGER (SUPERADMIN) ---
    if st.session_state.user_role == "superadmin":
        with tab_brand_mgr:
            st.markdown(f"<h3 style='margin-bottom: 1rem;'>Manage Rules for {active_brand}</h3>", unsafe_allow_html=True)
            st.warning("Updates made here will permanently save to the database.")
            current_cities_str = ", ".join(brand_configs[active_brand]["lost_cities"])
            updated_cities = st.text_area("Master Sold-Out Cities Database", value=current_cities_str, height=200)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"💾 Permanently Save {active_brand} Rules"):
                brand_configs[active_brand]["lost_cities"] = [c.strip() for c in updated_cities.split(",") if c.strip()]
                save_config(brand_configs)
                log_activity(st.session_state.user_email, active_brand, "Updated Brand Cities", 0, "N/A")
                st.success(f"{active_brand} successfully updated!")
                st.rerun()

    # --- TAB 3: GLOBAL LOGS (SUPERADMIN) ---
    if st.session_state.user_role == "superadmin":
        with tab_logs:
            st.markdown("<h3 style='margin-bottom: 1rem;'>🌍 Global Audit Master Log</h3>", unsafe_allow_html=True)
            try:
                logs_df = pd.read_csv(LOG_FILE).sort_values(by="Timestamp", ascending=False).reset_index(drop=True)
                st.dataframe(logs_df, use_container_width=True)
            except Exception as e:
                st.error("No logs generated yet.")
