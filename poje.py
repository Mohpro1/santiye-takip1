import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# ==========================================
# 1. PAGE SETUP & CONFIGURATION
# ==========================================
st.set_page_config(page_title="Havence - Multi-Page Dashboard", layout="wide", page_icon="🏗️")

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
    <html dir="rtl">
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #333; margin: 30px; line-height: 1.6; text-align: right; }}
            .no-print {{ text-align: center; margin-bottom: 25px; }}
            .btn {{ background-color: #1E4620; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.15); }}
            .header {{ text-align: center; border-bottom: 3px solid #1E4620; padding-bottom: 15px; margin-bottom: 30px; }}
            .title {{ font-size: 24px; font-weight: bold; color: #1E4620; }}
            .date {{ font-size: 14px; color: #666; margin-top: 5px; }}
            .grid {{ display: flex; gap: 15px; margin-bottom: 25px; flex-direction: row-reverse; }}
            .card {{ flex: 1; background: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; text-align: center; }}
            .card-lbl {{ font-size: 12px; font-weight: bold; color: #777; }}
            .card-val {{ font-size: 22px; font-weight: bold; color: #111; margin-top: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; text-align: right; }}
            th, td {{ border: 1px solid #dddddd; padding: 12px; font-size: 14px; }}
            th {{ background-color: #f5f5f5; font-weight: bold; color: #111; }}
            tr:nth-child(even) {{ background-color: #fafafa; }}
            .total {{ font-weight: bold; background-color: #e8f5e9 !important; }}
            @media print {{ .no-print {{ display: none !important; }} body {{ margin: 10px; }} }}
        </style>
    </head>
    <body>
        <div class="no-print">
            <button class="btn" onclick="window.print()">🖨️ حفظ التقرير كـ PDF / طباعة</button>
        </div>
        <div class="header">
            <div class="title">{title}</div>
            <div class="date">تاريخ استخراج التقرير: {today_str}</div>
        </div>
        {content_html}
    </body>
    </html>
    """

# ==========================================
# 4. SIDEBAR - DYNAMIC NAVIGATION & PRICES
# ==========================================
st.sidebar.image("https://img.icons8.com/clouds/100/000000/building.png", width=80)
st.sidebar.title("Havence Control")
st.sidebar.markdown("---")

# تفعيل التنقل بين الصفحات بشكل منفصل
app_page = st.sidebar.radio(
    "📂 اختر الصفحة المطلوبة:",
    [
        "💰 الميزانية والمستخلصات الشاملة", 
        "🏠 أعمال التشطيبات الداخلية", 
        "🧱 أعمال الواجهات الخارجية", 
        "💧 أعمال الحمامات والمطابخ",
        "⏱️ سجل الموقع الزمني"
    ]
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ إعدادات الأسعار (₺/m²)")

# أسعار الفئات (مربوطة بقاعدة البيانات)
pm_price_int = st.sidebar.number_input("البيع للمالك - داخلي", value=get_state_val("global_pm_price_int", 450.0), step=10.0)
update_state_val("global_pm_price_int", pm_price_int)
tech_price_int = st.sidebar.number_input("تكلفة الفني - داخلي", value=get_state_val("global_tech_price_int", 300.0), step=10.0)
update_state_val("global_tech_price_int", tech_price_int)

pm_price_ext = st.sidebar.number_input("البيع للمالك - خارجي", value=get_state_val("global_pm_price_ext", 600.0), step=10.0)
update_state_val("global_pm_price_ext", pm_price_ext)
tech_price_ext = st.sidebar.number_input("تكلفة الفني - خارجي", value=get_state_val("global_tech_price_ext", 400.0), step=10.0)
update_state_val("global_tech_price_ext", tech_price_ext)

pm_price_toilet = st.sidebar.number_input("البيع للمالك - حمامات", value=get_state_val("global_pm_price_toilet", 750.0), step=10.0)
update_state_val("global_pm_price_toilet", pm_price_toilet)
tech_price_toilet = st.sidebar.number_input("تكلفة الفني - حمامات", value=get_state_val("global_tech_price_toilet", 500.0), step=10.0)
update_state_val("global_tech_price_toilet", tech_price_toilet)

# الأوزان النسبية الهندسية
interior_weights = {"Ano": 0.15, "Alci": 0.40, "Saten": 0.25, "Boya": 0.20}
exterior_weights = {"Siva": 0.30, "Mantolama": 0.40, "Astar": 0.10, "Boya": 0.20}
toilet_weights = {"Tesisat": 0.25, "Izolasyon": 0.20, "Seramik": 0.45, "Montaj": 0.10}

# ==========================================
# 5. FIXED DATA STRUCTURE (SURVEYING)
# ==========================================
project_structure = {
    "الدور -1 (البدروم السكني والخدمي)": {
        "دكان -1 (المساحة الصافية)": {"area": 66.71, "type": "interior"},
        "مخازن البدروم (القطاع الإنشائي)": {"area": 30.22, "type": "interior"},
        "الطرقة العامة للبدروم": {"area": 50.72, "type": "interior"},
        "سلم البدروم الداخلي": {"area": 6.96, "type": "interior"},
        "الشقة الخلفية (الدور السفلي)": {"area": 187.47, "type": "interior"},
        "حمامات البدروم والخدمات": {"area": 15.50, "type": "toilet"}
    },
    "دور المدخل الأرضي": {
        "المدخل الرئيسي والممر الطولي": {"area": 24.32, "type": "interior"},
        "الطرقة العامة والصالة الأرضية": {"area": 50.38, "type": "interior"},
        "سلم الدور الأرضي": {"area": 6.96, "type": "interior"},
        "الدكان الأرضي الصافي": {"area": 24.06, "type": "interior"},
        "الشقة الخلفية الأرضية": {"area": 106.56, "type": "interior"},
        "حمامات الشقة الأرضية والدكان": {"area": 12.20, "type": "toilet"}
    },
    "الدور المتكرر الأول": {
        "الشقة الأمامية (1)": {"area": 163.17, "type": "interior"},
        "الشقة الخلفية (1)": {"area": 106.56, "type": "interior"},
        "السلم العام والطرقة (1)": {"area": 50.76, "type": "interior"},
        "حمامات الشقة الأمامية (1)": {"area": 18.40, "type": "toilet"},
        "حمامات الشقة الخلفية (1)": {"area": 14.20, "type": "toilet"}
    },
    "الدور المتكرر الثاني": {
        "الشقة الأمامية (2)": {"area": 163.17, "type": "interior"},
        "الشقة الخلفية (2)": {"area": 106.56, "type": "interior"},
        "السلم العام والطرقة (2)": {"area": 50.76, "type": "interior"},
        "حمامات الشقة الأمامية (2)": {"area": 18.40, "type": "toilet"},
        "حمامات الشقة الخلفية (2)": {"area": 14.20, "type": "toilet"}
    },
    "الدور المتكرر الثالث": {
        "الشقة الأمامية (3)": {"area": 163.17, "type": "interior"},
        "الشقة الخلفية (3)": {"area": 106.56, "type": "interior"},
        "السلم العام والطرقة (3)": {"area": 50.76, "type": "interior"},
        "حمامات الشقة الأمامية (3)": {"area": 18.40, "type": "toilet"},
        "حمامات الشقة الخلفية (3)": {"area": 14.20, "type": "toilet"}
    },
    "الدور الأخير (الدوبلكس / الملحق)": {
        "الشقة الأمامية الأخير": {"area": 163.17, "type": "interior"},
        "الشقة الخلفية الأخير": {"area": 106.56, "type": "interior"},
        "السلم والمسارات للأخير": {"area": 50.76, "type": "interior"},
        "حمامات الشقة الدوبلكس": {"area": 22.60, "type": "toilet"}
    },
    "الواجهات الخارجية للمبنى": {
        "الواجهة الأمامية الرئيسية": {"area": 280.00, "type": "exterior"},
        "الواجهة الخلفية": {"area": 240.00, "type": "exterior"},
        "الجانب الأيمن (Yan Cephe)": {"area": 20.00 * 10.00, "type": "exterior"}, # الارتفاع المحدث 20 متر
        "الجانب الأيسر": {"area": 200.00, "type": "exterior"}
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

global_idx = 0
for floor_name, sections in project_structure.items():
    for sec_name, info in sections.items():
        area = info["area"]
        sec_type = info["type"]
        
        if sec_type == "interior":
            p1 = get_state_val(f"cb_int_ano_{global_idx}", False)
            p2 = get_state_val(f"cb_int_alc_{global_idx}", False)
            p3 = get_state_val(f"cb_int_sat_{global_idx}", False)
            p4 = get_state_val(f"cb_int_boy_{global_idx}", False)
            sec_progress = ((interior_weights["Ano"] if p1 else 0) + 
                            (interior_weights["Alci"] if p2 else 0) + 
                            (interior_weights["Saten"] if p3 else 0) + 
                            (interior_weights["Boya"] if p4 else 0))
            current_pm = pm_price_int
            current_tech = tech_price_int
            phases = [("int_ano", "البؤج (Ano)"), ("int_alc", "المحارة (Alçı)"), ("int_sat", "المعجون (Saten)"), ("int_boy", "الدهان (Boya)")]
            
        elif sec_type == "exterior":
            p1 = get_state_val(f"cb_ext_siva_{global_idx}", False)
            p2 = get_state_val(f"cb_ext_mant_{global_idx}", False)
            p3 = get_state_val(f"cb_ext_ast_{global_idx}", False)
            p4 = get_state_val(f"cb_ext_boy_{global_idx}", False)
            sec_progress = ((exterior_weights["Siva"] if p1 else 0) + 
                            (exterior_weights["Mantolama"] if p2 else 0) + 
                            (exterior_weights["Astar"] if p3 else 0) + 
                            (exterior_weights["Boya"] if p4 else 0))
            current_pm = pm_price_ext
            current_tech = tech_price_ext
            phases = [("ext_siva", "المحارة الخارجية"), ("ext_mant", "العزل الحراري"), ("ext_ast", "الآستار"), ("ext_boy", "دهان الواجهة")]
            
        else: # toilet
            p1 = get_state_val(f"cb_toi_tes_{global_idx}", False)
            p2 = get_state_val(f"cb_toi_izo_{global_idx}", False)
            p3 = get_state_val(f"cb_toi_ser_{global_idx}", False)
            p4 = get_state_val(f"cb_toi_mon_{global_idx}", False)
            sec_progress = ((toilet_weights["Tesisat"] if p1 else 0) + 
                            (toilet_weights["Izolasyon"] if p2 else 0) + 
                            (toilet_weights["Seramik"] if p3 else 0) + 
                            (toilet_weights["Montaj"] if p4 else 0))
            current_pm = pm_price_toilet
            current_tech = tech_price_toilet
            phases = [("toi_tes", "السباكة والتأسيس"), ("toi_izo", "العزل المائي"), ("toi_ser", "تركيب السيراميك"), ("toi_mon", "القطع الصحية")]

        completed_area = area * sec_progress
        total_project_area += area
        total_completed_equivalent_area += completed_area
        
        total_billing_owner += completed_area * current_pm
        total_labor_cost += completed_area * current_tech
        
        flat_sections.append({
            "global_idx": global_idx, "floor": floor_name, "section": sec_name, "area": area, "type": sec_type,
            "progress": sec_progress, "comp_area": completed_area, "pm_price": current_pm, "tech_price": current_tech,
            "phases": phases, "p1": p1, "p2": p2, "p3": p3, "p4": p4
        })
        global_idx += 1

overall_progress_pct = (total_completed_equivalent_area / total_project_area) if total_project_area > 0 else 0

# ==========================================
# 7. MULTI-PAGE ROUTING LOGIC
# ==========================================

# --- PAGE 1: MONEY & TOTAL DASHBOARD ---
if app_page == "💰 الميزانية والمستخلصات الشاملة":
    st.header("💰 الحسابات المالية الإجمالية للمشروع")
    st.markdown(f"#### 📊 النسبة الكلية المكتملة للموقع: `{overall_progress_pct*100:.2f}%`")
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("مستخلص المالك (المعتمد)", f"₺ {total_billing_owner:,.2f}")
    col_b.metric("أجور ومستحقات الفنيين", f"₺ {total_labor_cost:,.2f}")
    col_c.metric("صافي الأرباح (Havence)", f"₺ {total_billing_owner - total_labor_cost:,.2f}")
    
    st.markdown("---")
    
    table_rows_html = ""
    report_list = []
    type_map = {"interior": "داخلي", "exterior": "خارجي/واجهات", "toilet": "حمامات"}
    
    for item in flat_sections:
        sec_bill = item["comp_area"] * item["pm_price"]
        sec_cost = item["comp_area"] * item["tech_price"]
        
        report_list.append({
            "الموقع/الدور": item["floor"], "البند": item["section"], "الفئة": type_map[item["type"]],
            "المساحة": f"{item['area']:.2f} م²", "الإنجاز": f"{item['progress']*100:.0f}%",
            "حساب المالك": f"₺ {sec_bill:,.2f}", "حساب الفني": f"₺ {sec_cost:,.2f}"
        })
        
        table_rows_html += f"""
        <tr>
            <td>{item['floor']}</td><td>{item['section']}</td><td>{type_map[item['type']]}</td>
            <td>{item['area']:.2f} م²</td><td>{item['progress']*100:.0f}%</td>
            <td>₺ {sec_bill:,.2f}</td><td>₺ {sec_cost:,.2f}</td>
        </tr>
        """
        
    html_content = f"""
    <table>
        <thead>
            <tr><th>الدور</th><th>القطاع</th><th>الفئة</th><th>المساحة</th><th>نسبة الإنجاز</th><th>مستخلص المالك</th><th>أجرة الفني</th></tr>
        </thead>
        <tbody>
            {table_rows_html}
            <tr class="total">
                <td colspan="3">المجموع الإجمالي</td><td>{total_project_area:,.2f} م²</td><td>{overall_progress_pct*100:.2f}%</td>
                <td>₺ {total_billing_owner:,.2f}</td><td>₺ {total_labor_cost:,.2f}</td>
            </tr>
        </tbody>
    </table>
    """
    
    st.download_button("🖨️ تحميل مستخلص المشروع الشامل بصيغة PDF/HTML", 
                       make_report_wrapper("تقرير الحسابات الموحد - Havence", html_content), 
                       file_name="Havence_Financial_Report.html", mime="text/html")
    
    st.dataframe(pd.DataFrame(report_list), use_container_width=True)

# --- PAGE 2: INTERIOR WORK ---
elif app_page == "🏠 أعمال التشطيبات الداخلية":
    st.header("🏠 إدارة ومتابعة التشطيبات الداخلية (İç Mekan)")
    
    for floor_name in project_structure.keys():
        interior_items = [x for x in flat_sections if x["floor"] == floor_name and x["type"] == "interior"]
        if interior_items:
            with st.expander(f"⬇️ {floor_name} - القطاعات الداخلية", expanded=True):
                c1, c2 = st.columns(2)
                for i, item in enumerate(interior_items):
                    g_id = item["global_idx"]
                    col = c1 if i % 2 == 0 else c2
                    with col:
                        st.write(f"##### 📍 {item['section']} ({item['area']:.2f} م²)")
                        st.checkbox("البؤج والأوتار (Ano) [15%]", value=item["p1"], key=f"p_int_ano_{g_id}", 
                                    on_change=handle_checkbox_change, args=(f"p_int_ano_{g_id}", f"cb_int_ano_{g_id}", f"date_int_ano_{g_id}"))
                        st.checkbox("المحارة والجبس (Alçı) [40%]", value=item["p2"], key=f"p_int_alc_{g_id}", 
                                    on_change=handle_checkbox_change, args=(f"p_int_alc_{g_id}", f"cb_int_alc_{g_id}", f"date_int_alc_{g_id}"))
                        st.checkbox("المعجون الناعم (Saten) [25%]", value=item["p3"], key=f"p_int_sat_{g_id}", 
                                    on_change=handle_checkbox_change, args=(f"p_int_sat_{g_id}", f"cb_int_sat_{g_id}", f"date_int_sat_{g_id}"))
                        st.checkbox("الدهان وجه أخير (Boya) [20%]", value=item["p4"], key=f"p_int_boy_{g_id}", 
                                    on_change=handle_checkbox_change, args=(f"p_int_boy_{g_id}", f"cb_int_boy_{g_id}", f"date_int_boy_{g_id}"))
                        st.write(f"نسبة الإنجاز: `{item['progress']*100:.0f}%` | أمتار مكافئة: `{item['comp_area']:.2f} م²`")
                        st.markdown("---")

# --- PAGE 3: EXTERIOR WORK ---
elif app_page == "🧱 أعمال الواجهات الخارجية":
    st.header("🧱 إدارة ومتابعة أعمال الواجهات والـ Dış Cephe")
    
    exterior_items = [x for x in flat_sections if x["type"] == "exterior"]
    if exterior_items:
        c1, c2 = st.columns(2)
        for i, item in enumerate(exterior_items):
            g_id = item["global_idx"]
            col = c1 if i % 2 == 0 else c2
            with col:
                st.write(f"##### 🧱 {item['section']} ({item['area']:.2f} م²)")
                st.checkbox("المحارة الخارجية (Sıva) [30%]", value=item["p1"], key=f"p_ext_siva_{g_id}", 
                            on_change=handle_checkbox_change, args=(f"p_ext_siva_{g_id}", f"cb_ext_siva_{g_id}", f"date_ext_siva_{g_id}"))
                st.checkbox("العزل الحراري (Mantolama) [40%]", value=item["p2"], key=f"p_ext_mant_{g_id}", 
                            on_change=handle_checkbox_change, args=(f"p_ext_mant_{g_id}", f"cb_ext_mant_{g_id}", f"date_ext_mant_{g_id}"))
                st.checkbox("الوجه التحضيري (Astar) [10%]", value=item["p3"], key=f"p_ext_ast_{g_id}", 
                            on_change=handle_checkbox_change, args=(f"p_ext_ast_{g_id}", f"cb_ext_ast_{g_id}", f"date_ext_ast_{g_id}"))
                st.checkbox("الدهان الخارجي (Boya) [20%]", value=item["p4"], key=f"p_ext_boy_{g_id}", 
                            on_change=handle_checkbox_change, args=(f"p_ext_boy_{g_id}", f"cb_ext_boy_{g_id}", f"date_ext_boy_{g_id}"))
                st.write(f"نسبة الإنجاز: `{item['progress']*100:.0f}%` | أمتار مكافئة: `{item['comp_area']:.2f} م²`")
                st.markdown("---")

# --- PAGE 4: TOILET WORK ---
elif app_page == "💧 أعمال الحمامات والمطابخ":
    st.header("💧 إدارة ومتابعة عزل وتأسيس الحمامات والمطابخ")
    
    for floor_name in project_structure.keys():
        toilet_items = [x for x in flat_sections if x["floor"] == floor_name and x["type"] == "toilet"]
        if toilet_items:
            with st.expander(f"⬇️ {floor_name} - شبكة الحمامات والخدمات", expanded=True):
                c1, c2 = st.columns(2)
                for i, item in enumerate(toilet_items):
                    g_id = item["global_idx"]
                    col = c1 if i % 2 == 0 else c2
                    with col:
                        st.write(f"##### 💧 {item['section']} ({item['area']:.2f} م²)")
                        st.checkbox("تأسيس السباكة والتغذية (Tesisat) [25%]", value=item["p1"], key=f"p_toi_tes_{g_id}", 
                                    on_change=handle_checkbox_change, args=(f"p_toi_tes_{g_id}", f"cb_toi_tes_{g_id}", f"date_toi_tes_{g_id}"))
                        st.checkbox("العزل المائي والطبقات (İzolasyon) [20%]", value=item["p2"], key=f"p_toi_izo_{g_id}", 
                                    on_change=handle_checkbox_change, args=(f"p_toi_izo_{g_id}", f"cb_toi_izo_{g_id}", f"date_toi_izo_{g_id}"))
                        st.checkbox("السيراميك والبورسلان (Seramik) [45%]", value=item["p3"], key=f"p_toi_ser_{g_id}", 
                                    on_change=handle_checkbox_change, args=(f"p_toi_ser_{g_id}", f"cb_toi_ser_{g_id}", f"date_toi_ser_{g_id}"))
                        st.checkbox("تركيب الفينش والقطع الصحية (Montaj) [10%]", value=item["p4"], key=f"p_toi_mon_{g_id}", 
                                    on_change=handle_checkbox_change, args=(f"p_toi_mon_{g_id}", f"cb_toi_mon_{g_id}", f"date_toi_mon_{g_id}"))
                        st.write(f"نسبة الإنجاز: `{item['progress']*100:.0f}%` | أمتار مكافئة: `{item['comp_area']:.2f} م²`")
                        st.markdown("---")

# --- PAGE 5: TIMELINE LOG ---
elif app_page == "⏱️ سجل الموقع الزمني":
    st.header("⏱️ الخط الزمني ومواعيد تسليم المراحل الفنية")
    
    timeline_events = []
    for item in flat_sections:
        g_id = item["global_idx"]
        for phase_code, phase_name in item["phases"]:
            d = get_state_val(f"date_{phase_code}_{g_id}", "")
            if d:
                timeline_events.append({
                    "التاريخ": d, "الدور / الموقع": item["floor"], "البند الفني": item["section"], "المرحلة": phase_name
                })
                
    if timeline_events:
        df_time = pd.DataFrame(timeline_events)
        df_time['dt_parse'] = pd.to_datetime(df_time['التاريخ'], format='%d.%m.%Y')
        df_time = df_time.sort_values(by='dt_parse', ascending=False).drop(columns=['dt_parse'])
        
        st.dataframe(df_time, use_container_width=True)
    else:
        st.info("لم يتم إنجاز أو وضع علامة تنفيذ على أي مرحلة في أي صفحة حتى الآن.")
