import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# ==========================================
# 1. PAGE SETUP & CONFIGURATION
# ==========================================
st.set_page_config(page_title="Havence - Şantiye Takip Sistemi", layout="wide", page_icon="🏗️")

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
    <html lang="tr">
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
            <button class="btn" onclick="window.print()">🖨️ Raporu PDF Olarak Kaydet / Yazdır</button>
        </div>
        <div class="header">
            <div class="title">{title}</div>
            <div class="date">Rapor Tarihi: {today_str}</div>
        </div>
        {content_html}
    </body>
    </html>
    """

# ==========================================
# 4. SIDEBAR NAVIGATION & MASTER PRICES
# ==========================================
st.sidebar.image("https://img.icons8.com/clouds/100/000000/building.png", width=80)
st.sidebar.title("Havence Yönetim")
st.sidebar.markdown("---")

app_page = st.sidebar.radio(
    "📂 Sayfa Seçimi Yapın:",
    [
        "🏁 Proje Durumu & İş Programı",
        "💰 İşveren Hakediş Raporu", 
        "👷 hesaplar ve kar (العمال والأرباح)",
        "🏠 İç Mekan İşleri (Alçı & Sıva)", 
        "🧱 Dış Cephe İşleri", 
        "💧 Tuvalet & Islak Hacim (Kara Sıva)",
        "⏱️ Şantiye Günlüğü & Zaman Çizelgesi"
    ]
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Birim Fiyat Ayarları (₺/m²)")

pm_price_int = st.sidebar.number_input("İşveren Satış - İç Mekan", value=get_state_val("global_pm_price_int", 450.0), step=10.0)
update_state_val("global_pm_price_int", pm_price_int)
tech_price_int = st.sidebar.number_input("Usta Maliyeti - İç Mekan", value=get_state_val("global_tech_price_int", 300.0), step=10.0)
update_state_val("global_tech_price_int", tech_price_int)

pm_price_ext = st.sidebar.number_input("İşveren Satış - Dış Cephe", value=get_state_val("global_pm_price_ext", 600.0), step=10.0)
update_state_val("global_pm_price_ext", pm_price_ext)
tech_price_ext = st.sidebar.number_input("Usta Maliyeti - Dış Cephe", value=get_state_val("global_tech_price_ext", 400.0), step=10.0)
update_state_val("global_tech_price_ext", tech_price_ext)

pm_price_toilet = st.sidebar.number_input("İşveren Satış - Kara Sıva", value=get_state_val("global_pm_price_toilet", 750.0), step=10.0)
update_state_val("global_pm_price_toilet", pm_price_toilet)
tech_price_toilet = st.sidebar.number_input("Usta Maliyeti - Kara Sıva", value=get_state_val("global_tech_price_toilet", 500.0), step=10.0)
update_state_val("global_tech_price_toilet", tech_price_toilet)

# Ağırlık Katsayıları Tanımlamaları
interior_weights = {"int_ano": 0.15, "int_alc": 0.40, "int_sat": 0.25, "int_boy": 0.20}
exterior_weights_insulated = {"ext_siva": 0.30, "ext_mant": 0.40, "ext_ast": 0.10, "ext_boy": 0.20}
exterior_weights_no_insulation = {"ext_siva": 0.45, "ext_ast": 0.15, "ext_boy": 0.40}

# ==========================================
# 5. FIXED DATA STRUCTURE WITH EXTERIOR & TOILET BREAKDOWN
# ==========================================
project_structure = {
    "Kat -1 (Bodrum Katı)": {
        "Dükkan -1 (Net Alan)": {"area": 66.71, "type": "interior"},
        "Bodrum Depoları": {"area": 30.22, "type": "interior"},
        "Bodrum Ortak Koridor": {"area": 50.72, "type": "interior"},
        "Bodrum İç Merdiven": {"area": 6.96, "type": "interior"},
        "Arka Daire (Alt Kat)": {"area": 187.47, "type": "interior"},
        "Bodrum Lavabo & WC": {"area": 29.50, "type": "toilet"}
    },
    "Zemin Giriş Katı": {
        "Ana Giriş & Uzun Hol": {"area": 24.32, "type": "interior"},
        "Ortak Koridor & Zemin Salon": {"area": 50.38, "type": "interior"},
        "Zemin Kat Merdiveni": {"area": 6.96, "type": "interior"},
        "Net Zemin Dükkan": {"area": 24.06, "type": "interior"},
        "Arka Zemin Daire": {"area": 106.56, "type": "interior"},
        "Zemin Arka Daire Tuvaleti": {"area": 20.87, "type": "toilet"},
        "Zemin Dükkan Tuvaleti": {"area": 28.00, "type": "toilet"}
    },
    "Normal Kat 1": {
        "Ön Daire (1)": {"area": 163.17, "type": "interior"},
        "Arka Daire (1)": {"area": 106.56, "type": "interior"},
        "Ortak Merdiven & Hol (1)": {"area": 50.76, "type": "interior"},
        "Ön Daire Tuvaleti (1)": {"area": 28.00, "type": "toilet"},
        "Arka Daire Tuvaleti (1)": {"area": 20.87, "type": "toilet"}
    },
    "Normal Kat 2": {
        "Ön Daire (2)": {"area": 163.17, "type": "interior"},
        "Arka Daire (2)": {"area": 106.56, "type": "interior"},
        "Ortak Merdiven & Hol (2)": {"area": 50.76, "type": "interior"},
        "Ön Daire Tuvaleti (2)": {"area": 28.00, "type": "toilet"},
        "Arka Daire Tuvaleti (2)": {"area": 20.87, "type": "toilet"}
    },
    "Normal Kat 3": {
        "Ön Daire (3)": {"area": 163.17, "type": "interior"},
        "Arka Daire (3)": {"area": 106.56, "type": "interior"},
        "Ortak Merdiven & Hol (3)": {"area": 50.76, "type": "interior"},
        "Ön Daire Tuvaleti (3)": {"area": 28.00, "type": "toilet"},
        "Arka Daire Tuvaleti (3)": {"area": 20.87, "type": "toilet"}
    },
    "Son Kat (Dublex / Çatı Katı)": {
        "Son Kat Ön Daire": {"area": 163.17, "type": "interior"},
        "Son Kat Arka Daire": {"area": 106.56, "type": "interior"},
        "Son Kat Merdiven & Geçişler": {"area": 50.76, "type": "interior"},
        "Dublex Ön Daire Tuvaleti": {"area": 28.00, "type": "toilet"},
        "Dublex Arka Daire Tuvaleti": {"area": 20.87, "type": "toilet"}
    },
    "Binanın Dış Cepheleri": {
        "Arka Dış Cephe - Ana Yüzey": {"area": 104.40, "type": "exterior_back"},
        "Arka Dış Cephe - 1. Yan": {"area": 136.50, "type": "exterior_back"},
        "Arka Dış Cephe - 2. Yan": {"area": 83.00, "type": "exterior_back"},
        "Arka Dış Cephe - 3. Yan": {"area": 33.00, "type": "exterior_back"},
        "Ön Dış Cephe - Ana Yüzey": {"area": 80.00, "type": "exterior_front"},
        "Ön Dış Cephe - 1. Yan (Yalıtımsız)": {"area": 68.25, "type": "exterior_front_no_ins"},
        "Ön Dış Cephe - 2. Yan (Yalıtımsız)": {"area": 41.50, "type": "exterior_front_no_ins"}
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

# مجموعات حساب النسب التفاعلية للواجهات والداخلي والحمامات
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
        
        # ربط الجروبات بالمؤشرات الرئيسية المطلوبة
        group_key = "interior"
        if "exterior_front" in sec_type:
            group_key = "exterior_front"
        elif "exterior_back" in sec_type:
            group_key = "exterior_back"
        elif sec_type == "toilet":
            group_key = "toilet"

        if sec_type == "interior":
            current_pm = pm_price_int
            current_tech = tech_price_int
            raw_phases = [("int_ano", "Ano Çıtası"), ("int_alc", "Alçı Sıva"), ("int_sat", "Saten Alçı"), ("int_boy", "İç Cephe Boya")]
            for code, name in raw_phases:
                is_checked = get_state_val(f"cb_{code}_{global_idx}", False)
                if is_checked:
                    sec_progress += interior_weights[code]
                phases.append((code, name, is_checked))
                
        elif "exterior_front" in sec_type or "exterior_back" in sec_type:
            current_pm = pm_price_ext
            current_tech = tech_price_ext
            if "no_ins" not in sec_type:
                raw_phases = [("ext_siva", "Kaba Sıva"), ("ext_mant", "Mantolama"), ("ext_ast", "Dış Cephe Astar"), ("ext_boy", "Dış Cephe Boya")]
                for code, name in raw_phases:
                    is_checked = get_state_val(f"cb_{code}_{global_idx}", False)
                    if is_checked:
                        sec_progress += exterior_weights_insulated[code]
                    phases.append((code, name, is_checked))
            else:
                raw_phases = [("ext_siva", "Kaba Sıva"), ("ext_ast", "Dış Cephe Astar"), ("ext_boy", "Dış Cephe Boya")]
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
            phases.append(("toi_ksiva", "Kara Sıva Uygulaması", is_checked))

        completed_area = area * sec_progress
        total_project_area += area
        total_completed_equivalent_area += completed_area
        
        total_billing_owner += completed_area * current_pm
        total_labor_cost += completed_area * current_tech
        
        # تحديث بيانات المجموعات التفاعلية
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
if app_page == "🏁 Proje Durumu & İş Programı":
    st.header("🏗️ Havence - Şantiye İlerleme ve İş Durumu")
    
    # قسم المؤشرات التفاعلية الجديد للبند الأساسية
    st.markdown("### 📊 Ana İmalat Kalemleri İlerleme Göstergeleri (مؤشرات تقدم البنود التفاعلية)")
    
    g_col1, g_col2, g_col3, g_col4 = st.columns(4)
    
    with g_col1:
        int_pct = (groups_data["interior"]["comp_area"] / groups_data["interior"]["total_area"] * 100) if groups_data["interior"]["total_area"] > 0 else 0
        st.metric("🏠 İç Mekan İşleri (الداخلي)", f"% {int_pct:.1f}")
        st.progress(int_pct / 100)
        
    with g_col2:
        front_pct = (groups_data["exterior_front"]["comp_area"] / groups_data["exterior_front"]["total_area"] * 100) if groups_data["exterior_front"]["total_area"] > 0 else 0
        st.metric("🧱 Ön Dış Cephe (الواجهة الأمامية)", f"% {front_pct:.1f}")
        st.progress(front_pct / 100)
        
    with g_col3:
        back_pct = (groups_data["exterior_back"]["comp_area"] / groups_data["exterior_back"]["total_area"] * 100) if groups_data["exterior_back"]["total_area"] > 0 else 0
        st.metric("🧱 Arka Dış Cephe (الواجهة الخلفية)", f"% {back_pct:.1f}")
        st.progress(back_pct / 100)
        
    with g_col4:
        toi_pct = (groups_data["toilet"]["comp_area"] / groups_data["toilet"]["total_area"] * 100) if groups_data["toilet"]["total_area"] > 0 else 0
        st.metric("💧 Tuvaletler (الحمامات)", f"% {toi_pct:.1f}")
        st.progress(toi_pct / 100)

    st.markdown("---")
    
    st.subheader("🗓️ Genel Proje Zaman Çizelgesi Takibi")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        start_date = st.date_input("🗓️ Proje Fiili Başlangıç Tarihi:", value=datetime.strptime(get_state_val("proj_start_date", "2026-01-01"), "%Y-%m-%d").date())
        update_state_val("proj_start_date", start_date.strftime("%Y-%m-%d"))
    with col_t2:
        end_date = st.date_input("🗓️ Hedeflenen Proje Bitiş Tarihi:", value=datetime.strptime(get_state_val("proj_end_date", "2026-08-01"), "%Y-%m-%d").date())
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
    c_m1.metric("Şantiyedeki Genel İlerleme (إجمالي الإنجاز)", f"% {actual_progress_pct:.2f}")
    c_m2.metric("Zamana Göre Olması Gereken", f"% {expected_progress_pct:.2f}")
    
    if actual_progress_pct >= expected_progress_pct:
        c_m3.success("🟢 On Schedule (Zamanlamaya Uygun)")
    else:
        c_m3.error("🔴 Delayed (Gecikme Var)")

# --- PAGE 2: OWNER BILLING REPORT ---
elif app_page == "💰 İşveren Hakediş Raporu":
    st.header("💰 İşveren Hakediş Raporu (جدول حائضي المستحقات من مالك المشروع)")
    st.metric("İşverenden Alınacak Toplam Hakediş", f"₺ {total_billing_owner:,.2f}")
    st.markdown("---")
    
    table_rows_html = ""
    report_list = []
    type_map = {"interior": "İç Mekan", "exterior_front": "Ön Cephe (Yalıtımlı)", "exterior_front_no_ins": "Ön Cephe (Yalıtımsız)", "exterior_back": "Arka Cephe", "toilet": "Kara Sıva (Tuvalet)"}
    
    for item in flat_sections:
        sec_bill = item["comp_area"] * item["pm_price"]
        
        # جلب تاريخ الإنجاز إن وجد
        last_date = "Bekliyor"
        for phase_code, _, _ in item["phases"]:
            d = get_state_val(f"date_{phase_code}_{item['global_idx']}", "")
            if d: last_date = d

        report_list.append({
            "Kat / Bölge": item["floor"], "Bölüm": item["section"], "Kategori": type_map.get(item["type"], "Dış Cephe"),
            "Alan": f"{item['area']:.2f} m²", "İlerleme": f"%{item['progress']*100:.0f}",
            "İşveren Birim Fiyat": f"₺ {item['pm_price']:.2f}", "Hakediş Tutarı": f"₺ {sec_bill:,.2f}",
            "Son İşlem Tarihi": last_date
        })
        
    st.dataframe(pd.DataFrame(report_list), use_container_width=True)

# --- PAGE 3: SEPARATE LABOR COSTS & PROFITS (الصفحة المنفصلة الجديدة) ---
elif app_page == "👷 hesaplar ve kar (العمال والأرباح)":
    st.header("👷 Usta Hesapları ve Havence Net Kârlılık Analizi")
    
    net_profit = total_billing_owner - total_labor_cost
    
    c_l1, c_l2, c_l3 = st.columns(3)
    c_l1.metric("Ustalara Ödenecek Toplam Hakediş", f"₺ {total_labor_cost:,.2f}")
    c_l2.metric("Havence Brüt Kâr", f"₺ {net_profit:,.2f}")
    if total_billing_owner > 0:
        c_l3.metric("Kâr Marjı Oranı", f"% {(net_profit / total_billing_owner)*100:.1f}")
        
    st.markdown("---")
    st.subheader("📋 Detaylı Usta Maliyet ve Tarih Tablosu")
    
    labor_report = []
    type_map = {"interior": "İç Mekan", "exterior_front": "Ön Cephe", "exterior_front_no_ins": "Ön Cephe (Yalıtımsız)", "exterior_back": "Arka Cephe", "toilet": "Kara Sıva (Tuvalet)"}
    
    for item in flat_sections:
        sec_cost = item["comp_area"] * item["tech_price"]
        sec_bill = item["comp_area"] * item["pm_price"]
        sec_profit = sec_bill - sec_cost
        
        # استخراج تواريخ الإنجاز لكل خطوة بشكل منفصل وتجميعها
        done_dates = []
        for phase_code, phase_name, checked in item["phases"]:
            d = get_state_val(f"date_{phase_code}_{item['global_idx']}", "")
            if d:
                done_dates.append(f"{phase_name}: {d}")
        
        dates_str = " / ".join(done_dates) if done_dates else "İşlem Yok"
        
        labor_report.append({
            "Kat / Lokasyon": item["floor"],
            "Bölüm Adı": item["section"],
            "İş Tipi": type_map.get(item["type"], "Dış Cephe"),
            "Eşdeğer Bitmiş Alan": f"{item['comp_area']:.2f} m²",
            "Usta Birim Maliyeti": f"₺ {item['tech_price']:.2f}",
            "Usta Alacağı Tutar": f"₺ {sec_cost:,.2f}",
            "Havence Net Kazanç": f"₺ {sec_profit:,.2f}",
            "Aşama İnceleme ve Tarihler (تاريخ إنجاز البنود)": dates_str
        })
        
    st.dataframe(pd.DataFrame(labor_report), use_container_width=True)

# --- PAGE 4: INTERIOR WORK ---
elif app_page == "🏠 İç Mekan İşleri (Alçı & Sıva)":
    st.header("🏠 İç Mekan Alçı, Sıva ve Boya İşleri Kontrolü")
    
    for floor_name in project_structure.keys():
        interior_items = [x for x in flat_sections if x["floor"] == floor_name and x["type"] == "interior"]
        if interior_items:
            with st.expander(f"⬇️ {floor_name} - İç Mekan İmalatları", expanded=True):
                c1, c2 = st.columns(2)
                for i, item in enumerate(interior_items):
                    g_id = item["global_idx"]
                    col = c1 if i % 2 == 0 else c2
                    with col:
                        st.write(f"##### 📍 {item['section']} ({item['area']:.2f} m²)")
                        
                        for code, name, checked in item["phases"]:
                            label_map = {
                                "int_ano": "Ano Çıtası Çakılması [15%]",
                                "int_alc": "Makine Alçı Sıva Yapılması [40%]",
                                "int_sat": "Saten Alçı & Zımpara Hazırlık [25%]",
                                "int_boy": "Son Kat Boya Uygulaması [20%]"
                            }
                            st.checkbox(label_map[code], value=checked, key=f"ui_{code}_{g_id}", 
                                        on_change=handle_checkbox_change, args=(f"ui_{code}_{g_id}", f"cb_{code}_{g_id}", f"date_{code}_{g_id}"))
                        
                        st.write(f"Bölüm İlerlemesi: `%{item['progress']*100:.0f}` | Eşdeğer Alan: `{item['comp_area']:.2f} m²`")
                        st.markdown("---")

# --- PAGE 5: EXTERIOR WORK ---
elif app_page == "🧱 Dış Cephe İşleri":
    st.header("🧱 Dış Cephe Yalıtım, Sıva ve Boya İmalatları")
    
    exterior_items = [x for x in flat_sections if "exterior" in x["type"]]
    if exterior_items:
        c1, c2 = st.columns(2)
        for i, item in enumerate(exterior_items):
            g_id = item["global_idx"]
            col = c1 if i % 2 == 0 else c2
            with col:
                prefix_label = "🎯 Ön Cephe" if "front" in item["type"] else "📐 Arka Cephe"
                st.write(f"##### {prefix_label} - {item['section']} ({item['area']:.2f} m²)")
                
                label_map = {
                    "ext_siva": "Kaba Sıva Uygulaması",
                    "ext_mant": "Mantolama (Isı Yalıtımı) [40%]",
                    "ext_ast": "Dış Cephe Macun & Astar",
                    "ext_boy": "Dış Cephe Grenli/Düz Boya"
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
                
                st.write(f"Bölüm İlerlemesi: `%{item['progress']*100:.0f}` | Eşdeğer Alan: `{item['comp_area']:.2f} m²`")
                st.markdown("---")

# --- PAGE 6: TOILET WORK ---
elif app_page == "💧 Tuvalet & Islak Hacim (Kara Sıva)":
    st.header("💧 Tuvalet ve Islak Hacim Kara Sıva Kontrolü")
    
    for floor_name in project_structure.keys():
        toilet_items = [x for x in flat_sections if x["floor"] == floor_name and x["type"] == "toilet"]
        if toilet_items:
            with st.expander(f"⬇️ {floor_name} - Kara Sıva İmalatı", expanded=True):
                c1, c2 = st.columns(2)
                for i, item in enumerate(toilet_items):
                    g_id = item["global_idx"]
                    col = c1 if i % 2 == 0 else c2
                    with col:
                        st.write(f"##### 💧 {item['section']} ({item['area']:.2f} m²)")
                        code, name, checked = item["phases"][0]
                        st.checkbox("Kara Sıva Tamamlandı [%100]", value=checked, key=f"ui_{code}_{g_id}", 
                                    on_change=handle_checkbox_change, args=(f"ui_{code}_{g_id}", f"cb_{code}_{g_id}", f"date_{code}_{g_id}"))
                        st.write(f"Durum: `{'Tamamlandı' if checked else 'Bekliyor'}` | Eşdeğer Alan: `{item['comp_area']:.2f} m²`")
                        st.markdown("---")

# --- PAGE 7: TIMELINE LOG ---
elif app_page == "⏱️ Şantiye Günlüğü & Zaman Çizelgesi":
    st.header("⏱️ Şantiyede Tamamlanan İmalatların Zaman Çizelgesi")
    
    timeline_events = []
    for item in flat_sections:
        g_id = item["global_idx"]
        for phase_code, phase_name, _ in item["phases"]:
            d = get_state_val(f"date_{phase_code}_{g_id}", "")
            if d:
                timeline_events.append({
                    "Tarih": d, "Kat / Lokasyon": item["floor"], "İmalat Kalemi": item["section"], "Yapılan Aşama": phase_name
                })
                
    if timeline_events:
        df_time = pd.DataFrame(timeline_events)
        df_time['dt_parse'] = pd.to_datetime(df_time['Tarih'], format='%d.%m.%Y')
        df_time = df_time.sort_values(by='dt_parse', ascending=False).drop(columns=['dt_parse'])
        
        st.dataframe(df_time, use_container_width=True)
    else:
        st.info("Henüz şantiyede tamamlanan herhangi bir imalat adımı işaretlenmemiştir.")
