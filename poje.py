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
        "💰 Genel Finansal Durum & Hakediş", 
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

# Ağırlık Katsayıları
interior_weights = {"Ano": 0.15, "Alci": 0.40, "Saten": 0.25, "Boya": 0.20}
# Standart dış cephe (Yalıtımlı)
exterior_weights_insulated = {"Siva": 0.30, "Mantolama": 0.40, "Astar": 0.10, "Boya": 0.20}
# Yalıtımsız ön dış cephe dönüşleri (Sıva %45, Astar %15, Boya %40)
exterior_weights_no_insulation = {"Siva": 0.45, "Astar": 0.15, "Boya": 0.40}

# ==========================================
# 5. FIXED DATA STRUCTURE WITH NEW EXTERIOR METRAJ
# ==========================================
project_structure = {
    "Kat -1 (Bodrum Katı)": {
        "Dükkan -1 (Net Alan)": {"area": 66.71, "type": "interior"},
        "Bodrum Depoları": {"area": 30.22, "type": "interior"},
        "Bodrum Ortak Koridor": {"area": 50.72, "type": "interior"},
        "Bodrum İç Merdiven": {"area": 6.96, "type": "interior"},
        "Arka Daire (Alt Kat)": {"area": 187.47, "type": "interior"},
        "Bodrum Lavabo & WC": {"area": 15.50, "type": "toilet"}
    },
    "Zemin Giriş Katı": {
        "Ana Giriş & Uzun Hol": {"area": 24.32, "type": "interior"},
        "Ortak Koridor & Zemin Salon": {"area": 50.38, "type": "interior"},
        "Zemin Kat Merdiveni": {"area": 6.96, "type": "interior"},
        "Net Zemin Dükkan": {"area": 24.06, "type": "interior"},
        "Arka Zemin Daire": {"area": 106.56, "type": "interior"},
        "Zemin Daire & Dükkan Tuvaletleri": {"area": 12.20, "type": "toilet"}
    },
    "Normal Kat 1": {
        "Ön Daire (1)": {"area": 163.17, "type": "interior"},
        "Arka Daire (1)": {"area": 106.56, "type": "interior"},
        "Ortak Merdiven & Hol (1)": {"area": 50.76, "type": "interior"},
        "Ön Daire Tuvaletleri (1)": {"area": 18.40, "type": "toilet"},
        "Arka Daire Tuvaletleri (1)": {"area": 14.20, "type": "toilet"}
    },
    "Normal Kat 2": {
        "Ön Daire (2)": {"area": 163.17, "type": "interior"},
        "Arka Daire (2)": {"area": 106.56, "type": "interior"},
        "Ortak Merdiven & Hol (2)": {"area": 50.76, "type": "interior"},
        "Ön Daire Tuvaletleri (2)": {"area": 18.40, "type": "toilet"},
        "Arka Daire Tuvaletleri (2)": {"area": 14.20, "type": "toilet"}
    },
    "Normal Kat 3": {
        "Ön Daire (3)": {"area": 163.17, "type": "interior"},
        "Arka Daire (3)": {"area": 106.56, "type": "interior"},
        "Ortak Merdiven & Hol (3)": {"area": 50.76, "type": "interior"},
        "Ön Daire Tuvaletleri (3)": {"area": 18.40, "type": "toilet"},
        "Arka Daire Tuvaletleri (3)": {"area": 14.20, "type": "toilet"}
    },
    "Son Kat (Dublex / Çatı Katı)": {
        "Son Kat Ön Daire": {"area": 163.17, "type": "interior"},
        "Son Kat Arka Daire": {"area": 106.56, "type": "interior"},
        "Son Kat Merdiven & Geçişler": {"area": 50.76, "type": "interior"},
        "Dublex Daire Tuvaletleri": {"area": 22.60, "type": "toilet"}
    },
    "Binanın Dış Cepheleri": {
        "Arka Dış Cephe - Ana Yüzey": {"area": 104.40, "type": "exterior"},
        "Arka Dış Cephe - 1. Yan": {"area": 136.50, "type": "exterior"},
        "Arka Dış Cephe - 2. Yan": {"area": 83.00, "type": "exterior"},
        "Arka Dış Cephe - 3. Yan": {"area": 33.00, "type": "exterior"},
        "Ön Dış Cephe - Ana Yüzey": {"area": 80.00, "type": "exterior"},
        "Ön Dış Cephe - 1. Yan (Yalıtımsız)": {"area": 68.25, "type": "exterior_no_ins"},
        "Ön Dış Cephe - 2. Yan (Yalıtımsız)": {"area": 41.50, "type": "exterior_no_ins"}
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
            phases = [("int_ano", "Ano Çıtası"), ("int_alc", "Alçı Sıva"), ("int_sat", "Saten Alçı"), ("int_boy", "İç Cephe Boya")]
            p_states = [p1, p2, p3, p4]
            
        elif sec_type == "exterior":
            p1 = get_state_val(f"cb_ext_siva_{global_idx}", False)
            p2 = get_state_val(f"cb_ext_mant_{global_idx}", False)
            p3 = get_state_val(f"cb_ext_ast_{global_idx}", False)
            p4 = get_state_val(f"cb_ext_boy_{global_idx}", False)
            sec_progress = ((exterior_weights_insulated["Siva"] if p1 else 0) + 
                            (exterior_weights_insulated["Mantolama"] if p2 else 0) + 
                            (exterior_weights_insulated["Astar"] if p3 else 0) + 
                            (exterior_weights_insulated["Boya"] if p4 else 0))
            current_pm = pm_price_ext
            current_tech = tech_price_ext
            phases = [("ext_siva", "Kaba Sıva"), ("ext_mant", "Mantolama"), ("ext_ast", "Dış Cephe Astar"), ("ext_boy", "Dış Cephe Boya")]
            p_states = [p1, p2, p3, p4]
            
        elif sec_type == "exterior_no_ins":
            p1 = get_state_val(f"cb_ext_siva_{global_idx}", False)
            p3 = get_state_val(f"cb_ext_ast_{global_idx}", False)
            p4 = get_state_val(f"cb_ext_boy_{global_idx}", False)
            sec_progress = ((exterior_weights_no_insulation["Siva"] if p1 else 0) + 
                            (exterior_weights_no_insulation["Astar"] if p3 else 0) + 
                            (exterior_weights_no_insulation["Boya"] if p4 else 0))
            current_pm = pm_price_ext
            current_tech = tech_price_ext
            phases = [("ext_siva", "Kaba Sıva"), ("ext_ast", "Dış Cephe Astar"), ("ext_boy", "Dış Cephe Boya")]
            p_states = [p1, False, p3, p4]
            
        else: # toilet (Kara Sıva)
            p1 = get_state_val(f"cb_toi_ksiva_{global_idx}", False)
            sec_progress = 1.0 if p1 else 0.0
            current_pm = pm_price_toilet
            current_tech = tech_price_toilet
            phases = [("toi_ksiva", "Kara Sıva Uygulaması")]
            p_states = [p1, False, False, False]

        completed_area = area * sec_progress
        total_project_area += area
        total_completed_equivalent_area += completed_area
        
        total_billing_owner += completed_area * current_pm
        total_labor_cost += completed_area * current_tech
        
        flat_sections.append({
            "global_idx": global_idx, "floor": floor_name, "section": sec_name, "area": area, "type": sec_type,
            "progress": sec_progress, "comp_area": completed_area, "pm_price": current_pm, "tech_price": current_tech,
            "phases": phases, "p1": p_states[0], "p2": p_states[1], "p3": p_states[2], "p4": p_states[3]
        })
        global_idx += 1

overall_progress_pct = (total_completed_equivalent_area / total_project_area) if total_project_area > 0 else 0

# ==========================================
# 7. MULTI-PAGE ROUTING LOGIC
# ==========================================

# --- PAGE 1: SCHEDULE TRACKING ---
if app_page == "🏁 Proje Durumu & İş Programı":
    st.header("🏁 Proje Başlangıç/Bitiş Tarihleri & Planlanan Zaman Takibi")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        start_date = st.date_input("🗓️ Proje Fiili Başlangıç Tarihi:", value=datetime.strptime(get_state_val("proj_start_date", "2026-01-01"), "%Y-%m-%d").date())
        update_state_val("proj_start_date", start_date.strftime("%Y-%m-%d"))
    with col_t2:
        end_date = st.date_input("🗓️ Hedeflenen Proje Bitiş Tarihi:", value=datetime.strptime(get_state_val("proj_end_date", "2026-08-01"), "%Y-%m-%d").date())
        update_state_val("proj_end_date", end_date.strftime("%Y-%m-%d"))
        
    st.markdown("---")
    
    today_dt = date.today()
    total_days = (end_date - start_date).days
    days_passed = (today_dt - start_date).days
    
    if total_days > 0:
        expected_progress_pct = max(0.0, min(100.0, (days_passed / total_days) * 100))
    else:
        expected_progress_pct = 100.0
        
    actual_progress_pct = overall_progress_pct * 100
    
    st.subheader("📊 İş Programı Karşılaştırma Analizi")
    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.metric("Şantiyedeki Gerçek İlerleme", f"%{actual_progress_pct:.2f}")
    c_m2.metric("Zaman Göre Olması Gereken", f"%{expected_progress_pct:.2f}")
    
    if actual_progress_pct >= expected_progress_pct:
        c_m3.success("🟢 On Schedule (Zamanlamaya Uygun)")
        st.balloons()
    else:
        c_m3.error("🔴 Delayed (Gecikme Var)")
        
    st.markdown("---")
    st.info(f"💡 Toplam Ayrılan Süre: `{total_days}` Gün | Bugüne Kadar Geçen Süre: `{max(0, days_passed)}` Gün.")

# --- PAGE 2: FINANCIAL REPORT ---
elif app_page == "💰 Genel Finansal Durum & Hakediş":
    st.header("💰 Şantiye Finansal Raporları & Toplam Kar/Zarar")
    st.markdown(f"#### 📊 Toplam Şantiye Tamamlanma Oranı: `%{overall_progress_pct*100:.2f}`")
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("İşverenden Alınacak Toplam Hakediş", f"₺ {total_billing_owner:,.2f}")
    col_b.metric("Ustalara Ödenecek Toplam Maliyet", f"₺ {total_labor_cost:,.2f}")
    col_c.metric("Havence Net Kar", f"₺ {total_billing_owner - total_labor_cost:,.2f}")
    
    st.markdown("---")
    
    table_rows_html = ""
    report_list = []
    type_map = {"interior": "İç Mekan", "exterior": "Dış Cephe (Yalıtımlı)", "exterior_no_ins": "Dış Cephe (Yalıtımsız)", "toilet": "Kara Sıva (Tuvalet)"}
    
    for item in flat_sections:
        sec_bill = item["comp_area"] * item["pm_price"]
        sec_cost = item["comp_area"] * item["tech_price"]
        
        report_list.append({
            "Kat / Bölge": item["floor"], "Bölüm": item["section"], "Kategori": type_map[item["type"]],
            "Alan": f"{item['area']:.2f} m²", "İlerleme": f"%{item['progress']*100:.0f}",
            "İşveren Hakediş": f"₺ {sec_bill:,.2f}", "Usta Maliyeti": f"₺ {sec_cost:,.2f}"
        })
        
        table_rows_html += f"""
        <tr>
            <td>{item['floor']}</td><td>{item['section']}</td><td>{type_map[item['type']]}</td>
            <td>{item['area']:.2f} m²</td><td>%{item['progress']*100:.0f}</td>
            <td>₺ {sec_bill:,.2f}</td><td>₺ {sec_cost:,.2f}</td>
        </tr>
        """
        
    html_content = f"""
    <table>
        <thead>
            <tr><th>Kat/Bölge</th><th>Bölüm</th><th>Kategori</th><th>Metraj</th><th>İlerleme %</th><th>İşveren Hakediş</th><th>Usta Maliyeti</th></tr>
        </thead>
        <tbody>
            {table_rows_html}
            <tr class="total">
                <td colspan="3">Genel Toplam</td><td>{total_project_area:,.2f} m²</td><td>%{overall_progress_pct*100:.2f}</td>
                <td>₺ {total_billing_owner:,.2f}</td><td>₺ {total_labor_cost:,.2f}</td>
            </tr>
        </tbody>
    </table>
    """
    
    st.download_button("🖨️ Kapsamlı Şantiye Hakediş Raporunu İndir (PDF/HTML)", 
                       make_report_wrapper("Havence - Şantiye Hakediş ve Finansal Raporu", html_content), 
                       file_name="Havence_Finansal_Hakedis_Raporu.html", mime="text/html")
    
    st.dataframe(pd.DataFrame(report_list), use_container_width=True)

# --- PAGE 3: INTERIOR WORK ---
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
                        st.checkbox("Ano Çıtası Çakılması [15%]", value=item["p1"], key=f"p_int_ano_{g_id}", 
                                    on_change=handle_checkbox_change, args=(f"p_int_ano_{g_id}", f"cb_int_ano_{g_id}", f"date_int_ano_{g_id}"))
                        st.checkbox("Makine Alçı Sıva Yapılması [40%]", value=item["p2"], key=f"p_int_alc_{g_id}", 
                                    on_change=handle_checkbox_change, args=(f"p_int_alc_{g_id}", f"cb_int_alc_{g_id}", f"date_int_alc_{g_id}"))
                        st.checkbox("Saten Alçı & Zımpara Hazırlık [25%]", value=item["p3"], key=f"p_int_sat_{g_id}", 
                                    on_change=handle_checkbox_change, args=(f"p_int_sat_{g_id}", f"cb_int_sat_{g_id}", f"date_int_sat_{g_id}"))
                        st.checkbox("Son Kat Boya Uygulaması [20%]", value=item["p4"], key=f"p_int_boy_{g_id}", 
                                    on_change=handle_checkbox_change, args=(f"p_int_boy_{g_id}", f"cb_int_boy_{g_id}", f"date_int_boy_{g_id}"))
                        st.write(f"Bölüm İlerlemesi: `%{item['progress']*100:.0f}` | Eşdeğer Alan: `{item['comp_area']:.2f} m²`")
                        st.markdown("---")

# --- PAGE 4: EXTERIOR WORK (UPDATED WITH BREAKDOWN & INSULATION CHECK) ---
elif app_page == "🧱 Dış Cephe İşleri":
    st.header("🧱 Dış Cephe Yalıtım, Sıva ve Boya İmalatları")
    
    exterior_items = [x for x in flat_sections if x["type"] in ["exterior", "exterior_no_ins"]]
    if exterior_items:
        c1, c2 = st.columns(2)
        for i, item in enumerate(exterior_items):
            g_id = item["global_idx"]
            col = c1 if i % 2 == 0 else c2
            with col:
                st.write(f"##### 🧱 {item['section']} ({item['area']:.2f} m²)")
                
                # Kaba Sıva her iki tipte de var
                st.checkbox("Kaba Sıva Uygulaması", value=item["p1"], key=f"p_ext_siva_{g_id}", 
                            on_change=handle_checkbox_change, args=(f"p_ext_siva_{g_id}", f"cb_ext_siva_{g_id}", f"date_ext_siva_{g_id}"))
                
                # Sadece yalıtımlı cephede Mantolama adımı görünür
                if item["type"] == "exterior":
                    st.checkbox("Mantolama (Isı Yalıtımı) [40%]", value=item["p2"], key=f"p_ext_mant_{g_id}", 
                                on_change=handle_checkbox_change, args=(f"p_ext_mant_{g_id}", f"cb_ext_mant_{g_id}", f"date_ext_mant_{g_id}"))
                
                st.checkbox("Dış Cephe Macun & Astar", value=item["p3"], key=f"p_ext_ast_{g_id}", 
                            on_change=handle_checkbox_change, args=(f"p_ext_ast_{g_id}", f"cb_ext_ast_{g_id}", f"date_ext_ast_{g_id}"))
                
                st.checkbox("Dış Cephe Grenli/Düz Boya", value=item["p4"], key=f"p_ext_boy_{g_id}", 
                            on_change=handle_checkbox_change, args=(f"p_ext_boy_{g_id}", f"cb_ext_boy_{g_id}", f"date_ext_boy_{g_id}"))
                
                st.write(f"Bölüm İlerlemesi: `%{item['progress']*100:.0f}` | Eşdeğer Alan: `{item['comp_area']:.2f} m²`")
                st.markdown("---")

# --- PAGE 5: TOILET WORK ---
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
                        st.checkbox("Kara Sıva Tamamlandı [%100]", value=item["p1"], key=f"p_toi_ksiva_{g_id}", 
                                    on_change=handle_checkbox_change, args=(f"p_toi_ksiva_{g_id}", f"cb_toi_ksiva_{g_id}", f"date_toi_ksiva_{g_id}"))
                        st.write(f"Durum: `{'Tamamlandı' if item['p1'] else 'Bekliyor'}` | Eşdeğer Alan: `{item['comp_area']:.2f} m²`")
                        st.markdown("---")

# --- PAGE 6: TIMELINE LOG ---
elif app_page == "⏱️ Şantiye Günlüğü & Zaman Çizelgesi":
    st.header("⏱️ Şantiyede Tamamlanan İmalatların Zaman Çizelgesi")
    
    timeline_events = []
    for item in flat_sections:
        g_id = item["global_idx"]
        for phase_code, phase_name in item["phases"]:
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
