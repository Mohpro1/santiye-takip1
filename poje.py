import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# ==========================================
# 1. PAGE SETUP & CONFIGURATION
# ==========================================
st.set_page_config(page_title="Havence - Site Progress Tracking System", layout="wide", page_icon="🏗️")

# ==========================================
# 2. DATA PERSISTENCE ENGINE (JSON DATABASE)
# ==========================================
DB_FILE = "total_progress_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "saved_state" not in st.session_state:
    st.session_state.saved_state = load_data()

def get_state_val(key, default):
    return st.session_state.saved_state.get(key, default)

def update_state_val(key, val):
    if isinstance(val, (date, datetime)):
        val = val.isoformat()
    st.session_state.saved_state[key] = val
    save_data(st.session_state.saved_state)

def handle_checkbox_change(cb_key, save_key, date_key):
    if cb_key in st.session_state:
        current_val = st.session_state[cb_key]
        update_state_val(save_key, current_val)
        if current_val: 
            if not get_state_val(date_key, None):
                update_state_val(date_key, date.today().strftime("%d.%m.%Y"))
        else: 
            update_state_val(date_key, "")

# ==========================================
# 3. REPORT GENERATION WRAPPER
# ==========================================
def make_report_wrapper(title, content_html):
    today_str = date.today().strftime('%d.%m.%Y')
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #333; margin: 30px; line-height: 1.6; text-align: left; }}
            .no-print {{ text-align: center; margin-bottom: 25px; }}
            .btn {{ background-color: #1E4620; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.15); }}
            .header {{ text-align: center; border-bottom: 3px solid #1E4620; padding-bottom: 15px; margin-bottom: 30px; }}
            .title {{ font-size: 24px; font-weight: bold; color: #1E4620; }}
            .date {{ font-size: 14px; color: #666; margin-top: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; text-align: left; }}
            th, td {{ border: 1px solid #dddddd; padding: 12px; font-size: 14px; }}
            th {{ background-color: #f5f5f5; font-weight: bold; color: #111; }}
            tr:nth-child(even) {{ background-color: #fafafa; }}
            .total {{ font-weight: bold; background-color: #e8f5e9 !important; }}
            @media print {{ .no-print {{ display: none !important; }} body {{ margin: 10px; }} }}
        </style>
    </head>
    <body>
        <div class="no-print">
            <button class="btn" onclick="window.print()">🖨️ Save as PDF / Print Report</button>
        </div>
        <div class="header">
            <div class="title">{title}</div>
            <div class="date">Report Date: {today_str}</div>
        </div>
        {content_html}
    </body>
    </html>
    """

# ==========================================
# 4. SIDEBAR NAVIGATION & MASTER PRICES
# ==========================================
st.sidebar.image("https://img.icons8.com/clouds/100/000000/building.png", width=80)
st.sidebar.title("Havence Management")
st.sidebar.markdown("---")

app_page = st.sidebar.radio(
    "📂 Select Module:",
    [
        "🏁 Project Status & Schedule",
        "💰 Client Progress Payment Report", 
        "👷 Labor Cost & Profits Dashboard",
        "🏠 Interior Works (Plaster & Paint)", 
        "🧱 Exterior Works", 
        "💧 Toilet & Wet Areas (Black Plaster)",
        "⏱️ Daily Site Log & Timeline"
    ]
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Unit Price Settings (₺/m²)")

pm_price_int = st.sidebar.number_input("Client Billing - Interior", value=get_state_val("global_pm_price_int", 450.0), step=10.0)
update_state_val("global_pm_price_int", pm_price_int)
tech_price_int = st.sidebar.number_input("Labor Cost - Interior", value=get_state_val("global_tech_price_int", 300.0), step=10.0)
update_state_val("global_tech_price_int", tech_price_int)

pm_price_ext = st.sidebar.number_input("Client Billing - Exterior", value=get_state_val("global_pm_price_ext", 600.0), step=10.0)
update_state_val("global_pm_price_ext", pm_price_ext)
tech_price_ext = st.sidebar.number_input("Labor Cost - Exterior", value=get_state_val("global_tech_price_ext", 400.0), step=10.0)
update_state_val("global_tech_price_ext", tech_price_ext)

pm_price_toilet = st.sidebar.number_input("Client Billing - Black Plaster", value=get_state_val("global_pm_price_toilet", 750.0), step=10.0)
update_state_val("global_pm_price_toilet", pm_price_toilet)
tech_price_toilet = st.sidebar.number_input("Labor Cost - Black Plaster", value=get_state_val("global_tech_price_toilet", 500.0), step=10.0)
update_state_val("global_tech_price_toilet", tech_price_toilet)

# Custom pricing inputs for the Interior side of the Back Wall
pm_price_wall_int = st.sidebar.number_input("Client Billing - Back Wall (Interior)", value=get_state_val("global_pm_price_wall_int", 500.0), step=10.0)
update_state_val("global_pm_price_wall_int", pm_price_wall_int)
tech_price_wall_int = st.sidebar.number_input("Labor Cost - Back Wall (Interior)", value=get_state_val("global_tech_price_wall_int", 350.0), step=10.0)
update_state_val("global_tech_price_wall_int", tech_price_wall_int)

# Progress Step Weights Mapping
interior_weights = {"int_ano": 0.15, "int_alc": 0.40, "int_sat": 0.25, "int_boy": 0.20}
exterior_weights_insulated = {"ext_siva": 0.30, "ext_mant": 0.40, "ext_ast": 0.10, "ext_boy": 0.20}
exterior_weights_no_insulation = {"ext_siva": 0.45, "ext_ast": 0.15, "ext_boy": 0.40}

# ==========================================
# 5. FIXED DATA STRUCTURE WITH EXTERIOR & TOILET BREAKDOWN
# ==========================================
project_structure = {
    "Floor -1 (Basement Floor)": {
        "Shop -1 (Net Area)": {"area": 66.71, "type": "interior"},
        "Basement Storage Units": {"area": 30.22, "type": "interior"},
        "Basement Shared Corridor": {"area": 50.72, "type": "interior"},
        "Basement Internal Stairs": {"area": 6.96, "type": "interior"},
        "Rear Apartment (Lower Level)": {"area": 187.47, "type": "interior"},
        "Basement Lavatory & WC": {"area": 29.50, "type": "toilet"}
    },
    "Ground Entrance Floor": {
        "Main Entrance & Long Hall": {"area": 24.32, "type": "interior"},
        "Shared Corridor & Ground Lounge": {"area": 50.38, "type": "interior"},
        "Ground Floor Stairs": {"area": 6.96, "type": "interior"},
        "Net Ground Shop": {"area": 24.06, "type": "interior"},
        "Rear Ground Apartment": {"area": 106.56, "type": "interior"},
        "Ground Rear Apartment Toilet": {"area": 20.87, "type": "toilet"},
        "Ground Shop Toilet": {"area": 28.00, "type": "toilet"}
    },
    "Normal Floor 1": {
        "Front Apartment (1)": {"area": 163.17, "type": "interior"},
        "Rear Apartment (1)": {"area": 106.56, "type": "interior"},
        "Shared Stairs & Hall (1)": {"area": 50.76, "type": "interior"},
        "Front Apartment Toilet (1)": {"area": 28.00, "type": "toilet"},
        "Rear Apartment Toilet (1)": {"area": 20.87, "type": "toilet"}
    },
    "Normal Floor 2": {
        "Front Apartment (2)": {"area": 163.17, "type": "interior"},
        "Rear Apartment (2)": {"area": 106.56, "type": "interior"},
        "Shared Stairs & Hall (2)": {"area": 50.76, "type": "interior"},
        "Front Apartment Toilet (2)": {"area": 28.00, "type": "toilet"},
        "Rear Apartment Toilet (2)": {"area": 20.87, "type": "toilet"}
    },
    "Normal Floor 3": {
        "Front Apartment (3)": {"area": 163.17, "type": "interior"},
        "Rear Apartment (3)": {"area": 106.56, "type": "interior"},
        "Shared Stairs & Hall (3)": {"area": 50.76, "type": "interior"},
        "Front Apartment Toilet (3)": {"area": 28.00, "type": "toilet"},
        "Rear Apartment Toilet (3)": {"area": 20.87, "type": "toilet"}
    },
    "Top Floor (Duplex / Penthouse)": {
        "Top Floor Front Apartment": {"area": 163.17, "type": "interior"},
        "Top Floor Rear Apartment": {"area": 106.56, "type": "interior"},
        "Top Floor Stairs & Landings": {"area": 50.76, "type": "interior"},
        "Duplex Front Apartment Toilet": {"area": 28.00, "type": "toilet"},
        "Duplex Rear Apartment Toilet": {"area": 20.87, "type": "toilet"}
    },
    "Building Exteriors": {
        "Rear Exterior Facade - Main Face": {"area": 104.40, "type": "exterior_back"},
        "Rear Exterior Facade - Side 1": {"area": 136.50, "type": "exterior_back"},
        "Rear Exterior Facade - Side 2": {"area": 83.00, "type": "exterior_back"},
        "Rear Exterior Facade - Side 3": {"area": 33.00, "type": "exterior_back"},
        "Front Exterior Facade - Main Face": {"area": 80.00, "type": "exterior_front"},
        "Front Exterior Facade - Side 1 (No Ins)": {"area": 68.25, "type": "exterior_front_no_ins"},
        "Front Exterior Facade - Side 2 (No Ins)": {"area": 41.50, "type": "exterior_front_no_ins"},
        "Back Wall - Exterior Side": {"area": 40.00, "type": "exterior_back"},            # Back Wall Exterior Side
        "Back Wall - Interior Side": {"area": 77.00, "type": "exterior_wall_interior"}    # Back Wall Interior Side
    }
}

# ==========================================
# 6. CALCULATIONS MATRIX
# ==========================================
flat_sections = []
total_project_area = 0
total_completed_equivalent_area = 0
total_billing_owner = 0
total_labor_cost = 0

groups_data = {
    "interior": {"total_area": 0.0, "comp_area": 0.0},
    "exterior_front": {"total_area": 0.0, "comp_area": 0.0},
    "exterior_back": {"total_area": 0.0, "comp_area": 0.0},
    "toilet": {"total_area": 0.0, "comp_area": 0.0}
}

global_idx = 0
for floor_name, sections in project_structure.items():
    for sec_name, info in sections.items():
        area = info["area"]
        sec_type = info["type"]
        
        sec_progress = 0.0
        phases = []
        current_pm = 0.0
        current_tech = 0.0
        
        # Mapping metric groups
        group_key = "interior"
        if "exterior_front" in sec_type:
            group_key = "exterior_front"
        elif "exterior_back" in sec_type or sec_type == "exterior_wall_interior":
            group_key = "exterior_back"
        elif sec_type == "toilet":
            group_key = "toilet"

        if sec_type == "interior":
            current_pm = pm_price_int
            current_tech = tech_price_int
            raw_phases = [("int_ano", "Screed Guide Installation"), ("int_alc", "Gypsum Plaster application"), ("int_sat", "Satin Finish & Sanding"), ("int_boy", "Interior Painting")]
            for code, name in raw_phases:
                is_checked = get_state_val(f"cb_{code}_{global_idx}", False)
                if is_checked:
                    sec_progress += interior_weights[code]
                phases.append((code, name, is_checked))
                
        elif "exterior_front" in sec_type or "exterior_back" in sec_type or sec_type == "exterior_wall_interior":
            # Assign proper customized pricing vectors
            if sec_type == "exterior_wall_interior":
                current_pm = pm_price_wall_int
                current_tech = tech_price_wall_int
            else:
                current_pm = pm_price_ext
                current_tech = tech_price_ext

            if "no_ins" not in sec_type:
                raw_phases = [("ext_siva", "Rough Plastering"), ("ext_mant", "Thermal Insulation (Sheathing)"), ("ext_ast", "Surface Primer & Putty"), ("ext_boy", "Exterior Painting")]
                for code, name in raw_phases:
                    is_checked = get_state_val(f"cb_{code}_{global_idx}", False)
                    if is_checked:
                        sec_progress += exterior_weights_insulated[code]
                    phases.append((code, name, is_checked))
            else:
                raw_phases = [("ext_siva", "Rough Plastering"), ("ext_ast", "Surface Primer & Putty"), ("ext_boy", "Exterior Painting")]
                for code, name in raw_phases:
                    is_checked = get_state_val(f"cb_{code}_{global_idx}", False)
                    if is_checked:
                        sec_progress += exterior_weights_no_insulation[code]
                    phases.append((code, name, is_checked))
                
        else: # toilet
            current_pm = pm_price_toilet
            current_tech = tech_price_toilet
            is_checked = get_state_val(f"cb_toi_ksiva_{global_idx}", False)
            sec_progress = 1.0 if is_checked else 0.0
            phases.append(("toi_ksiva", "Black Plaster Application", is_checked))

        completed_area = area * sec_progress
        total_project_area += area
        total_completed_equivalent_area += completed_area
        
        total_billing_owner += completed_area * current_pm
        total_labor_cost += completed_area * current_tech
        
        groups_data[group_key]["total_area"] += area
        groups_data[group_key]["comp_area"] += completed_area
        
        flat_sections.append({
            "global_idx": global_idx, "floor": floor_name, "section": sec_name, "area": area, "type": sec_type,
            "progress": sec_progress, "comp_area": completed_area, "pm_price": current_pm, "tech_price": current_tech,
            "phases": phases
        })
        global_idx += 1

overall_progress_pct = (total_completed_equivalent_area / total_project_area) if total_project_area > 0 else 0

# ==========================================
# 7. MULTI-PAGE ROUTING LOGIC
# ==========================================

# --- PAGE 1: SCHEDULE TRACKING & INTERACTIVE GAUGES ---
if app_page == "🏁 Project Status & Schedule":
    st.header("🏗️ Havence - Construction Site Progress Tracker")
    
    st.markdown("### 📊 Interactive Progress Gauges per Work Category")
    g_col1, g_col2, g_col3, g_col4 = st.columns(4)
    
    with g_col1:
        int_pct = (groups_data["interior"]["comp_area"] / groups_data["interior"]["total_area"] * 100) if groups_data["interior"]["total_area"] > 0 else 0
        st.metric("🏠 Interior Works", f"{int_pct:.1f} %")
        st.progress(int_pct / 100)
        
    with g_col2:
        front_pct = (groups_data["exterior_front"]["comp_area"] / groups_data["exterior_front"]["total_area"] * 100) if groups_data["exterior_front"]["total_area"] > 0 else 0
        st.metric("🧱 Front Exterior Facade", f"{front_pct:.1f} %")
        st.progress(front_pct / 100)
        
    with g_col3:
        back_pct = (groups_data["exterior_back"]["comp_area"] / groups_data["exterior_back"]["total_area"] * 100) if groups_data["exterior_back"]["total_area"] > 0 else 0
        st.metric("🧱 Rear Facade & Back Wall", f"{back_pct:.1f} %")
        st.progress(back_pct / 100)
        
    with g_col4:
        toi_pct = (groups_data["toilet"]["comp_area"] / groups_data["toilet"]["total_area"] * 100) if groups_data["toilet"]["total_area"] > 0 else 0
        st.metric("💧 Toilets & Wet Areas", f"{toi_pct:.1f} %")
        st.progress(toi_pct / 100)

    st.markdown("---")
    
    st.subheader("🗓️ Operational Timeline Tracking")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        start_date = st.date_input("Project Mobilization Date:", value=datetime.strptime(get_state_val("proj_start_date", "2026-01-01"), "%Y-%m-%d").date())
        update_state_val("proj_start_date", start_date.strftime("%Y-%m-%d"))
    with col_t2:
        end_date = st.date_input("Target Delivery Deadline Date:", value=datetime.strptime(get_state_val("proj_end_date", "2026-08-01"), "%Y-%m-%d").date())
        update_state_val("proj_end_date", end_date.strftime("%Y-%m-%d"))
        
    today_dt = date.today()
    total_days = (end_date - start_date).days
    days_passed = (today_dt - start_date).days
    
    if total_days > 0:
        expected_progress_pct = max(0.0, min(100.0, (days_passed / total_days) * 100))
    else:
        expected_progress_pct = 100.0
        
    actual_progress_pct = overall_progress_pct * 100
    
    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.metric("Overall Cumulative Progress Site-Wide", f"{actual_progress_pct:.2f} %")
    c_m2.metric("Target Linear Calendar Progress", f"{expected_progress_pct:.2f} %")
    
    if actual_progress_pct >= expected_progress_pct:
        c_m3.success("🟢 On Schedule")
    else:
        c_m3.error("🔴 Delayed")

# --- PAGE 2: OWNER BILLING REPORT ---
elif app_page == "💰 Client Progress Payment Report":
    st.header("💰 Progress Statement Report (Client Receivable Ledger)")
    st.metric("Total Client Interim Claim Valuation", f"₺ {total_billing_owner:,.2f}")
    st.markdown("---")
    
    table_rows_html = ""
    report_list = []
    type_map = {
        "interior": "Interior Finishes", 
        "exterior_front": "Front Facade (Insulated)", 
        "exterior_front_no_ins": "Front Facade (Uninsulated)", 
        "exterior_back": "Rear Facade System", 
        "exterior_wall_interior": "Back Wall (Interior Face)", 
        "toilet": "Black Plaster (Toilet)"
    }
    
    for item in flat_sections:
        sec_bill = item["comp_area"] * item["pm_price"]
        
        last_date = "Pending"
        for phase_code, _, _ in item["phases"]:
            d = get_state_val(f"date_{phase_code}_{item['global_idx']}", "")
            if d: last_date = d

        report_list.append({
            "Floor / Group Zone": item["floor"], "Section Zone": item["section"], "Operational Category": type_map.get(item["type"], "Exterior"),
            "Total Metrage": f"{item['area']:.2f} m²", "Completion Rate": f"{item['progress']*100:.0f} %",
            "Contract Unit Rate": f"₺ {item['pm_price']:.2f}", "Certified Valuation Amount": f"₺ {sec_bill:,.2f}",
            "Last Update Date": last_date
        })
        
    st.dataframe(pd.DataFrame(report_list), use_container_width=True)

# --- PAGE 3: LABOR COSTS & PROFITS (Independent Isolated Dashboard) ---
elif app_page == "👷 Labor Cost & Profits Dashboard":
    st.header("👷 Labor Accounts & Havence Net Profitability Analytics")
    
    net_profit = total_billing_owner - total_labor_cost
    
    c_l1, c_l2, c_l3 = st.columns(3)
    c_l1.metric("Total Labor Accounts Liability (Subcontractor)", f"₺ {total_labor_cost:,.2f}")
    c_l2.metric("Havence Absolute Gross Profit Margin", f"₺ {net_profit:,.2f}")
    if total_billing_owner > 0:
        c_l3.metric("Net Margin Performance Percentage", f"{ (net_profit / total_billing_owner)*100:.1f} %")
        
    st.markdown("---")
    st.subheader("📋 Itemized Labor Valuations and Execution Date Log")
    
    labor_report = []
    type_map = {
        "interior": "Interior Finishes", 
        "exterior_front": "Front Facade", 
        "exterior_front_no_ins": "Front Facade (Uninsulated)", 
        "exterior_back": "Rear Facade System", 
        "exterior_wall_interior": "Back Wall (Interior Face)", 
        "toilet": "Wet Area Black Plaster"
    }
    
    for item in flat_sections:
        sec_cost = item["comp_area"] * item["tech_price"]
        sec_bill = item["comp_area"] * item["pm_price"]
        sec_profit = sec_bill - sec_cost
        
        done_dates = []
        for phase_code, phase_name, checked in item["phases"]:
            d = get_state_val(f"date_{phase_code}_{item['global_idx']}", "")
            if d:
                done_dates.append(f"{phase_name}: {d}")
        
        dates_str = " / ".join(done_dates) if done_dates else "No Activity Logs"
        
        labor_report.append({
            "Location Zone": item["floor"],
            "Sub-item Description": item["section"],
            "Task Classification": type_map.get(item["type"], "Exterior"),
            "Finished Equivalent Metrage": f"{item['comp_area']:.2f} m²",
            "Labor Contract Unit Price": f"₺ {item['tech_price']:.2f}",
            "Labor Earned Claim Tutar": f"₺ {sec_cost:,.2f}",
            "Havence Earned Net Spread": f"₺ {sec_profit:,.2f}",
            "Task Execution Timeline History": dates_str
        })
        
    st.dataframe(pd.DataFrame(labor_report), use_container_width=True)

# --- PAGE 4: INTERIOR WORK ---
elif app_page == "🏠 Interior Works (Plaster & Paint)":
    st.header("🏠 Interior Finish-Out Operations Quality Control Panel")
    
    for floor_name in project_structure.keys():
        interior_items = [x for x in flat_sections if x["floor"] == floor_name and x["type"] == "interior"]
        if interior_items:
            with st.expander(f"⬇️ {floor_name} - Internal Tasks Matrix", expanded=True):
                c1, c2 = st.columns(2)
                for i, item in enumerate(interior_items):
                    g_id = item["global_idx"]
                    col = c1 if i % 2 == 0 else c2
                    with col:
                        st.write(f"##### 📍 {item['section']} ({item['area']:.2f} m²)")
                        
                        for code, name, checked in item["phases"]:
                            label_map = {
                                "int_ano": "Screed Guide Installation [15%]",
                                "int_alc": "Machine Gypsum Plastering [40%]",
                                "int_sat": "Satin Plaster Putty Skimming [25%]",
                                "int_boy": "Final Coat Decorative Painting [20%]"
                            }
                            st.checkbox(label_map[code], value=checked, key=f"ui_{code}_{g_id}", 
                                        on_change=handle_checkbox_change, args=(f"ui_{code}_{g_id}", f"cb_{code}_{g_id}", f"date_{code}_{g_id}"))
                        
                        st.write(f"Section Completion Rate: `{item['progress']*100:.0f} %` | Equivalent Metric Area: `{item['comp_area']:.2f} m²`")
                        st.markdown("---")

# --- PAGE 5: EXTERIOR WORK ---
elif app_page == "🧱 Exterior Works":
    st.header("🧱 Building Exterior Insulation, Coating and Facade Works")
    
    exterior_items = [x for x in flat_sections if "exterior" in x["type"]]
    if exterior_items:
        c1, c2 = st.columns(2)
        for i, item in enumerate(exterior_items):
            g_id = item["global_idx"]
            col = c1 if i % 2 == 0 else c2
            with col:
                # Custom label assignments to separate boundaries clearly
                if "front" in item["type"]:
                    prefix_label = "🎯 Front Facade Setup"
                elif "wall_interior" in item["type"]:
                    prefix_label = "📐 Back Wall (Property Line Interior)"
                else:
                    prefix_label = "📐 Rear Facade / Boundary Setup"

                st.write(f"##### {prefix_label} - {item['section']} ({item['area']:.2f} m²)")
                
                label_map = {
                    "ext_siva": "Rough Base Cement Plastering",
                    "ext_mant": "EPS/XPS Thermal Insulation Sheathing [40%]",
                    "ext_ast": "Weather Surface Putty Primer Coating",
                    "ext_boy": "Exterior Acrylic Textured Painting"
                }
                
                for code, name, checked in item["phases"]:
                    suffix = ""
                    if "no_ins" not in item["type"]:
                        pcts = {"ext_siva": " [30%]", "ext_mant": " [40%]", "ext_ast": " [10%]", "ext_boy": " [20%]"}
                        suffix = pcts[code]
                    else:
                        pcts = {"ext_siva": " [45%]", "ext_ast": " [15%]", "ext_boy": " [40%]"}
                        suffix = pcts[code]
                        
                    st.checkbox(label_map[code] + suffix, value=checked, key=f"ui_{code}_{g_id}", 
                                on_change=handle_checkbox_change, args=(f"ui_{code}_{g_id}", f"cb_{code}_{g_id}", f"date_{code}_{g_id}"))
                
                st.write(f"Section Completion Rate: `{item['progress']*100:.0f} %` | Equivalent Metric Area: `{item['comp_area']:.2f} m²`")
                st.markdown("---")

# --- PAGE 6: TOILET WORK ---
elif app_page == "💧 Toilet & Wet Areas (Black Plaster)":
    st.header("💧 Sanitary Layout Concrete Black Plaster Approvals")
    
    for floor_name in project_structure.keys():
        toilet_items = [x for x in flat_sections if x["floor"] == floor_name and x["type"] == "toilet"]
        if toilet_items:
            with st.expander(f"⬇️ {floor_name} - Wet Core Plaster Schedule", expanded=True):
                c1, c2 = st.columns(2)
                for i, item in enumerate(toilet_items):
                    g_id = item["global_idx"]
                    col = c1 if i % 2 == 0 else c2
                    with col:
                        st.write(f"##### 💧 {item['section']} ({item['area']:.2f} m²)")
                        code, name, checked = item["phases"][0]
                        st.checkbox("Waterproof Undercoat Black Plaster Completed [100%]", value=checked, key=f"ui_{code}_{g_id}", 
                                    on_change=handle_checkbox_change, args=(f"ui_{code}_{g_id}", f"cb_{code}_{g_id}", f"date_{code}_{g_id}"))
                        st.write(f"Status Indicator: `{'Completed' if checked else 'Pending Execution'}` | Equivalent Metric Area: `{item['comp_area']:.2f} m²`")
                        st.markdown("---")

# --- PAGE 7: TIMELINE LOG ---
elif app_page == "⏱️ Daily Site Log & Timeline":
    st.header("⏱️ Operational Historic Task Timeline Milestones")
    
    timeline_events = []
    for item in flat_sections:
        g_id = item["global_idx"]
        for phase_code, phase_name, _ in item["phases"]:
            d = get_state_val(f"date_{phase_code}_{g_id}", "")
            if d:
                timeline_events.append({
                    "Completed Date": d, "Location / Level Context": item["floor"], "Itemized Element": item["section"], "Task Step Executed": phase_name
                })
                
    if timeline_events:
        df_time = pd.DataFrame(timeline_events)
        df_time['dt_parse'] = pd.to_datetime(df_time['Completed Date'], format='%d.%m.%Y')
        df_time = df_time.sort_values(by='dt_parse', ascending=False).drop(columns=['dt_parse'])
        
        st.dataframe(df_time, use_container_width=True)
    else:
        st.info("No tasks have been signed off as completed on this engine yet.")
