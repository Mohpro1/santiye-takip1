import streamlit as st
import pandas as pd
from datetime import datetime, date
import requests
import json

# ==========================================
# 1. SAYFA AYARLARI
# ==========================================
st.set_page_config(page_title="Havence - Şantiye & Kârlılık Takip Sistemi", layout="wide", page_icon="🏗️")

# ==========================================
# 2. SUPABASE REST API BAĞLANTI AYARLARI
# ==========================================
SUPABASE_URL = "https://lhndsijncxofuvhwkarc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxobmRzaWpuY3hvZnV2aHdrYXJjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA4OTI3ODgsImV4cCI6MjA5NjQ2ODc4OH0.RYoa2eW56J-F116D-nJcMEdX0WwgJQu5hH9ELJ-hqJs"

ROW_ID = "havence_project_state" 
API_URL = f"{SUPABASE_URL}/rest/v1/total_progress_data"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def load_data_from_supabase():
    try:
        url = f"{API_URL}?id=eq.{ROW_ID}"
        get_headers = headers.copy()
        get_headers["Prefer"] = "return=representation"
        response = requests.get(url, headers=get_headers, timeout=10)
        if response.status_code == 200:
            res_json = response.json()
            if res_json and len(res_json) > 0:
                return res_json[0].get("val", {})
    except Exception as e:
        st.sidebar.warning(f"🔄 Veritabanı senkronizasyon kontrolü: {e}")
    return {}

def save_data_to_supabase(data):
    try:
        payload = {"id": ROW_ID, "val": data}
        upsert_headers = headers.copy()
        upsert_headers["Prefer"] = "return=representation,resolution=merge-duplicates"
        response = requests.post(API_URL, headers=upsert_headers, json=payload, timeout=10)
        
        if response.status_code not in [200, 201]:
            put_url = f"{API_URL}?id=eq.{ROW_ID}"
            put_headers = headers.copy()
            put_headers["Prefer"] = "return=representation"
            requests.put(put_url, headers=put_headers, json=payload, timeout=10)
    except Exception as e:
        st.error(f"Veri kaydedilirken hata oluştu (API): {e}")

if "saved_state" not in st.session_state:
    st.session_state.saved_state = load_data_from_supabase()

def get_state_val(key, default):
    return st.session_state.saved_state.get(key, default)

def update_state_val(key, val):
    if isinstance(val, (date, datetime)):
        val = val.isoformat()
    st.session_state.saved_state[key] = val
    save_data_to_supabase(st.session_state.saved_state)

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
# 3. RENKLENDİRME STİL MOTORU (100% OLANLAR YEŞİL)
# ==========================================
def highlight_completed(row):
    if 'Tamamlanma Oranı' in row and row['Tamamlanma Oranı'] == '% 100':
        return ['background-color: #d4edda; color: #155724; font-weight: bold;'] * len(row)
    elif 'İlerleme Oranı' in row and row['İlerleme Oranı'] == '% 100':
         return ['background-color: #d4edda; color: #155724; font-weight: bold;'] * len(row)
    return [''] * len(row)

# ==========================================
# 4. RAPOR ÇIKTI ŞABLONU (PDF UYUMLU HTML)
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
            body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #333; margin: 30px; line-height: 1.6; }}
            .no-print {{ text-align: center; margin-bottom: 25px; }}
            .btn {{ background-color: #1E4620; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-weight: bold; font-size: 16px; cursor: pointer; }}
            .header {{ text-align: center; border-bottom: 3px solid #1E4620; padding-bottom: 15px; margin-bottom: 30px; }}
            .title {{ font-size: 24px; font-weight: bold; color: #1E4620; }}
            .date {{ font-size: 14px; color: #666; margin-top: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; }}
            th, td {{ border: 1px solid #dddddd; padding: 12px; font-size: 14px; text-align: left; }}
            th {{ background-color: #f5f5f5; font-weight: bold; color: #111; }}
            tr:nth-child(even) {{ background-color: #fafafa; }}
            .completed-row {{ background-color: #d4edda !important; color: #155724 !important; font-weight: bold; }}
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
# 5. YAN MENÜ & BİRİM FİYATLAR
# ==========================================
st.sidebar.image("https://img.icons8.com/clouds/100/000000/building.png", width=80)
st.sidebar.title("Havence Yönetim")
st.sidebar.markdown("---")

app_page = st.sidebar.radio(
    "📂 Modül Seçimi Yapın:",
    [
        "🏁 Proje Durumu & İş Programı",
        "💰 İşveren Hakediş Raporu", 
        "👷 Usta Hak Edişleri",             
        "📊 Havence Kârlılık Analizi",       
        "🏠 İç Mekan İşleri (Alçı & Boya)", 
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

pm_price_wall_int = st.sidebar.number_input("İşveren Satış - Çevre Duvarı (İç)", value=get_state_val("global_pm_price_wall_int", 500.0), step=10.0)
update_state_val("global_pm_price_wall_int", pm_price_wall_int)
tech_price_wall_int = st.sidebar.number_input("Usta Maliyeti - Çevre Duvarı (İç)", value=get_state_val("global_tech_price_wall_int", 350.0), step=10.0)
update_state_val("global_tech_price_wall_int", tech_price_wall_int)

interior_weights = {"int_ano": 0.15, "int_alc": 0.40, "int_sat": 0.25, "int_boy": 0.20}
exterior_weights_insulated = {"ext_siva": 0.30, "ext_mant": 0.40, "ext_ast": 0.10, "ext_boy": 0.20}
exterior_weights_no_insulation = {"ext_siva": 0.45, "ext_ast": 0.15, "ext_boy": 0.40}

# ==========================================
# 6. PROJE YAPISI VE METRAJLARI
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
        "Ön Dış Cephe - 2. Yan (Yalıtımsız)": {"area": 41.50, "type": "exterior_front_no_ins"},
        "Arka Çevre Duvarı - Dış Yüzey": {"area": 40.00, "type": "exterior_back"},
        "Arka Çevre Duvarı - İç Yüzey": {"area": 77.00, "type": "exterior_wall_interior"}
    }
}

# ==========================================
# 7. HESAPLAMA MOTORU
# ==========================================
flat_sections = []
total_project_area = 0
total_completed_equivalent_area = 0

total_billing_owner_current = 0
total_labor_cost_current = 0

total_project_owner_value = 0
total_project_labor_value = 0

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
            raw_phases = [("int_ano", "Ano Çıtası Çakılması"), ("int_alc", "Kaba/Makine Alçı Sıva"), ("int_sat", "Saten Alçı & Zımpara"), ("int_boy", "İç Cephe Boyası")]
            for code, name in raw_phases:
                is_checked = get_state_val(f"cb_{code}_{global_idx}", False)
                if is_checked:
                    sec_progress += interior_weights[code]
                phases.append((code, name, is_checked))
                
        elif "exterior" in sec_type:
            if sec_type == "exterior_wall_interior":
                current_pm = pm_price_wall_int
                current_tech = tech_price_wall_int
            else:
                current_pm = pm_price_ext
                current_tech = tech_price_ext

            if "no_ins" not in sec_type:
                raw_phases = [("ext_siva", "Kaba Sıva Uygulaması"), ("ext_mant", "Mantolama (Isı Yalıtım)"), ("ext_ast", "Dış Cephe Astar & Macun"), ("ext_boy", "Dış Cephe Boyası")]
                for code, name in raw_phases:
                    is_checked = get_state_val(f"cb_{code}_{global_idx}", False)
                    if is_checked:
                        sec_progress += exterior_weights_insulated[code]
                    phases.append((code, name, is_checked))
            else:
                raw_phases = [("ext_siva", "Kaba Sıva Uygulaması"), ("ext_ast", "Dış Cephe Astar & Macun"), ("ext_boy", "Dış Cephe Boyası")]
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

        if sec_progress > 0.98:
            sec_progress = 1.0

        completed_area = area * sec_progress
        total_project_area += area
        total_completed_equivalent_area += completed_area
        
        total_billing_owner_current += completed_area * current_pm
        total_labor_cost_current += completed_area * current_tech
        
        total_project_owner_value += area * current_pm
        total_project_labor_value += area * current_tech
        
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
# 8. SAYFA MODÜL YÖNLENDİRMELERİ
# ==========================================

# --- MODÜL 1: PROJE GENEL DURUMU ---
if app_page == "🏁 Proje Durumu & İş Programı":
    st.header("🏗️ Havence - Şantiye İlerleme Analiz Paneli")
    
    st.markdown("### 📊 Ana İmalat Kalemleri İlerleme Göstergeleri")
    g_col1, g_col2, g_col3, g_col4 = st.columns(4)
    
    with g_col1:
        int_pct = (groups_data["interior"]["comp_area"] / groups_data["interior"]["total_area"] * 100) if groups_data["interior"]["total_area"] > 0 else 0
        st.metric("🏠 İç Mekan İşleri", f"% {int_pct:.1f}")
        st.progress(int_pct / 100)
        
    with g_col2:
        front_pct = (groups_data["exterior_front"]["comp_area"] / groups_data["exterior_front"]["total_area"] * 100) if groups_data["exterior_front"]["total_area"] > 0 else 0
        st.metric("🧱 Ön Dış Cephe", f"% {front_pct:.1f}")
        st.progress(front_pct / 100)
        
    with g_col3:
        back_pct = (groups_data["exterior_back"]["comp_area"] / groups_data["exterior_back"]["total_area"] * 100) if groups_data["exterior_back"]["total_area"] > 0 else 0
        st.metric("🧱 Arka Cephe & Çevre Duvarı", f"% {back_pct:.1f}")
        st.progress(back_pct / 100)
        
    with g_col4:
        toi_pct = (groups_data["toilet"]["comp_area"] / groups_data["toilet"]["total_area"] * 100) if groups_data["toilet"]["total_area"] > 0 else 0
        st.metric("💧 Tuvaletler & Islak Hacimler", f"% {toi_pct:.1f}")
        st.progress(toi_pct / 100)

    st.markdown("---")
    st.subheader("🗓️ Zaman Planı ve Takvimi")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        start_date = st.date_input("Proje Başlangıç Tarihi:", value=datetime.strptime(get_state_val("proj_start_date", "2026-01-01"), "%Y-%m-%d").date())
        update_state_val("proj_start_date", start_date.strftime("%Y-%m-%d"))
    with col_t2:
        end_date = st.date_input("Proje Hedef Bitiş Tarihi:", value=datetime.strptime(get_state_val("proj_end_date", "2026-08-01"), "%Y-%m-%d").date())
        update_state_val("proj_end_date", end_date.strftime("%Y-%m-%d"))
        
    today_dt = date.today()
    total_days = (end_date - start_date).days
    days_passed = (today_dt - start_date).days
    
    expected_progress_pct = max(0.0, min(100.0, (days_passed / total_days) * 100)) if total_days > 0 else 100.0
    actual_progress_pct = overall_progress_pct * 100
    
    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.metric("Şantiyedeki Genel İlerleme Oranı", f"% {actual_progress_pct:.2f}")
    c_m2.metric("Takvime Göre Olması Gereken", f"% {expected_progress_pct:.2f}")
    
    if actual_progress_pct >= expected_progress_pct:
        c_m3.success("🟢 Zamanlamaya Uygun İlerliyor")
    else:
        c_m3.error("🔴 Zaman Planının Gerisinde")

# --- MODÜL 2: İŞVEREN HAKEDİŞ RAPORU ---
elif app_page == "💰 İşveren Hakediş Raporu":
    st.header("💰 İşveren Dönemsel Hakediş Alacak Raporu")
    
    owner_payments_history = get_state_val("owner_payments_history_list", [])
    
    st.subheader("📥 İşverenden Alınan Parçalı Ödeme Girişi")
    op_col1, op_col2, op_col3 = st.columns([2, 2, 1])
    with op_col1:
        new_op_amount = st.number_input("Alınan Ödeme Tutarı (₺):", min_value=0.0, step=1000.0, key="new_op_amt")
    with op_col2:
        new_op_date = st.date_input("Ödeme Alınma Tarihi:", value=date.today(), key="new_op_dt")
    with op_col3:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("📥 Yeni Ödeme Ekle", use_container_width=True):
            if new_op_amount > 0:
                owner_payments_history.append({"Tarih": new_op_date.strftime("%d.%m.%Y"), "Miktar": new_op_amount})
                update_state_val("owner_payments_history_list", owner_payments_history)
                st.rerun()

    total_owner_received = sum([p["Miktar"] for p in owner_payments_history])
    owner_rest = total_billing_owner_current - total_owner_received
    
    if owner_payments_history:
        with st.expander("🔍 İşveren Alınan Ödemeler Detay Listesi", expanded=False):
            df_op_hist = pd.DataFrame(owner_payments_history)
            st.dataframe(df_op_hist, use_container_width=True)
            if st.button("🗑️ Tüm Ödeme Geçmişini Temizle", key="clear_op_hist"):
                update_state_val("owner_payments_history_list", [])
                st.rerun()
                
    st.markdown("---")
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Proje Toplam Sözleşme Bedeli", f"₺ {total_project_owner_value:,.2f}")
    m_col2.metric("Şu Ana Kadar Hak Edilen", f"₺ {total_billing_owner_current:,.2f}")
    m_col3.metric("İşverenin Ödediği Toplam", f"₺ {total_owner_received:,.2f}")
    if owner_rest >= 0:
        m_col4.metric("İşverenden Kalan Alacak", f"₺ {owner_rest:,.2f}", delta="- Kalan Alacak", delta_color="inverse")
    else:
        m_col4.metric("İşverenden Fazla Alınan (Avans)", f"₺ {abs(owner_rest):,.2f}", delta="+ Avans", delta_color="normal")
            
    report_list = []
    type_map = {
        "interior": "İç Mekan İmalatları", "exterior_front": "Ön Cephe (Yalıtımlı)", 
        "exterior_front_no_ins": "Ön Cephe (Yalıtımsız)", "exterior_back": "Arka Cephe Sistemi", 
        "exterior_wall_interior": "Çevre Duvarı (İç Yüzey)", "toilet": "Kara Sıva (Tuvaletler)"
    }
    
    html_rows = ""
    for item in flat_sections:
        sec_bill = item["comp_area"] * item["pm_price"]
        last_date = "İşlem Yok"
        for phase_code, _, _ in item["phases"]:
            d = get_state_val(f"date_{phase_code}_{item['global_idx']}", "")
            if d: last_date = d

        category_name = type_map.get(item["type"], "Dış Cephe")
        prog_pct_int = int(item["progress"] * 100)
        
        report_list.append({
            "Kat / Yapı Bölgesi": item["floor"], "Bölüm / Mahal": item["section"], "İmalat Kategorisi": category_name,
            "Toplam Metraj": f"{item['area']:.2f} m²", "Tamamlanma Oranı": f"% {prog_pct_int}",
            "Birim Fiyat": f"₺ {item['pm_price']:.2f}", "Hakediş Tutarı": f"₺ {sec_bill:,.2f}", "Son Onay Tarihi": last_date
        })
        
        row_class = ' class="completed-row"' if prog_pct_int == 100 else ''
        html_rows += f"""
        <tr{row_class}>
            <td>{item['floor']}</td><td>{item['section']}</td><td>{category_name}</td>
            <td>{item['area']:.2f} m²</td><td>% {prog_pct_int}</td><td>₺ {item['pm_price']:.2f}</td>
            <td>₺ {sec_bill:,.2f}</td><td>{last_date}</td>
        </tr>
        """
        
    full_html_report = f"""
    <table>
        <thead>
            <tr>
                <th>Kat / Bölge</th><th>Bölüm / Mahal</th><th>Kategori</th><th>Toplam Metraj</th>
                <th>İlerleme</th><th>Birim Fiyat</th><th>Hakediş Tutarı</th><th>Son Onay Tarihi</th>
            </tr>
        </thead>
        <tbody>
            {html_rows}
            <tr class="total" style="background-color: #e3f2fd !important;">
                <td colspan="6" style="text-align: right;">PROJE TOPLAM SÖZLEŞME BEDELİ (%100 KAPASİTE):</td>
                <td colspan="2">₺ {total_project_owner_value:,.2f}</td>
            </tr>
            <tr class="total">
                <td colspan="6" style="text-align: right;">MEVCUT HAK EDİLEN TOPLAM TUTAR:</td>
                <td colspan="2">₺ {total_billing_owner_current:,.2f}</td>
            </tr>
            <tr class="total" style="background-color: #fff3cd !important;">
                <td colspan="6" style="text-align: right;">İŞVERENDEN ALINAN TOPLAM ÖDEME:</td>
                <td colspan="2">₺ {total_owner_received:,.2f}</td>
            </tr>
            <tr class="total" style="background-color: #f8d7da !important;">
                <td colspan="6" style="text-align: right;">KALAN BAKİYE DURUMU:</td>
                <td colspan="2">₺ {owner_rest:,.2f}</td>
            </tr>
        </tbody>
    </table>
    """
    
    final_report_code = make_report_wrapper("Havence - Resmi İşveren Hakediş Raporu", full_html_report)
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="📄 Raporu PDF / HTML Olarak İndir (İşveren İçin)",
        data=final_report_code,
        file_name=f"Havence_Isveren_Hakedis_{date.today().strftime('%d_%m_%Y')}.html",
        mime="text/html"
    )
        
    st.markdown("---")
    df_styled = pd.DataFrame(report_list)
    st.dataframe(df_styled.style.apply(highlight_completed, axis=1), use_container_width=True)

# --- MODÜL 3: USTA HAK EDİŞLERİ ---
elif app_page == "👷 Usta Hak Edişleri":
    st.header("👷 Alt Yüklenici / Usta Hak Ediş Takip Paneli")
    
    labor_payments_history = get_state_val("labor_payments_history_list", [])
    
    st.subheader("📤 Ustalara Yapılan Parçalı Ödeme Girişi")
    lp_col1, lp_col2, lp_col3 = st.columns([2, 2, 1])
    with lp_col1:
        new_lp_amount = st.number_input("Ustalara Ödenen Tutar (₺):", min_value=0.0, step=1000.0, key="new_lp_amt")
    with lp_col2:
        new_lp_date = st.date_input("Ödeme Yapılma Tarihi:", value=date.today(), key="new_lp_dt")
    with lp_col3:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("📤 Ödeme Kaydet", use_container_width=True):
            if new_lp_amount > 0:
                labor_payments_history.append({"Tarih": new_lp_date.strftime("%d.%m.%Y"), "Miktar": new_lp_amount})
                update_state_val("labor_payments_history_list", labor_payments_history)
                st.rerun()

    total_labor_paid = sum([p["Miktar"] for p in labor_payments_history])
    labor_rest = total_labor_cost_current - total_labor_paid
    
    if labor_payments_history:
        with st.expander("🔍 Ustalara Yapılan Ödemeler Geçmiş Listesi", expanded=False):
            df_lp_hist = pd.DataFrame(labor_payments_history)
            st.dataframe(df_lp_hist, use_container_width=True)
            if st.button("🗑️ Tüm Usta Ödeme Geçmişini Temizle", key="clear_lp_hist"):
                update_state_val("labor_payments_history_list", [])
                st.rerun()

    st.markdown("---")
    l_col1, l_col2, l_col3, l_col4 = st.columns(4)
    l_col1.metric("Toplam Usta Bütçesi (%100 Bitince)", f"₺ {total_project_labor_value:,.2f}")
    l_col2.metric("Ustalara Hak Edilen (Şu An)", f"₺ {total_labor_cost_current:,.2f}")
    l_col3.metric("Ustalara Ödenen Toplam", f"₺ {total_labor_paid:,.2f}")
    if labor_rest >= 0:
        l_col4.metric("Ustalara Kalan Borcumuz", f"₺ {labor_rest:,.2f}", delta="- Kalan Borç", delta_color="inverse")
    else:
        l_col4.metric("Ustalara Fazla Ödenen (Avans)", f"₺ {abs(labor_rest):,.2f}", delta="+ Fazla Ödenen", delta_color="normal")
            
    labor_report = []
    type_map = {
        "interior": "İç Mekan İmalatları", "exterior_front": "Ön Cephe Sistemi", 
        "exterior_front_no_ins": "Ön Cephe (Yalıtımsız)", "exterior_back": "Arka Cephe Sistemi", 
        "exterior_wall_interior": "Çevre Duvarı (İç Yüzey)", "toilet": "Tuvalet Kara Sıva"
    }
    
    html_rows_labor = ""
    for item in flat_sections:
        sec_cost = item["comp_area"] * item["tech_price"]
        prog_pct_int = int(item["progress"] * 100)
        
        done_dates = []
        for phase_code, phase_name, checked in item["phases"]:
            d = get_state_val(f"date_{phase_code}_{item['global_idx']}", "")
            if d: done_dates.append(f"{phase_name}: {d}")
        dates_str = " / ".join(done_dates) if done_dates else "Kayıt Yok"
        
        category_name = type_map.get(item["type"], "Dış Cephe")
        labor_report.append({
            "Konum / Kat": item["floor"], "Bölüm / Mahal": item["section"], "İsh Sınıfı / Kategori": category_name,
            "İlerleme Oranı": f"% {prog_pct_int}", "Eşdeğer Biten Alan": f"{item['comp_area']:.2f} m²",
            "Usta Birim Maliyeti": f"₺ {item['tech_price']:.2f}", "Usta Alacağı Tutar": f"₺ {sec_cost:,.2f}", "Onay Tarihleri": dates_str
        })
        
        row_class = ' class="completed-row"' if prog_pct_int == 100 else ''
        html_rows_labor += f"""
        <tr{row_class}>
            <td>{item['floor']}</td><td>{item['section']}</td><td>{category_name}</td>
            <td>% {prog_pct_int}</td><td>{item['comp_area']:.2f} m²</td><td>₺ {item['tech_price']:.2f}</td>
            <td>₺ {sec_cost:,.2f}</td><td>{dates_str}</td>
        </tr>
        """

    full_html_labor = f"""
    <table>
        <thead>
            <tr>
                <th>Kat / Bölge</th><th>Bölüm / Mahal</th><th>Kategori</th><th>İlerleme</th>
                <th>Eşdeğer Alan</th><th>Birim Maliyet</th><th>Usta Alacağı</th><th>Aşama Detayları</th>
            </tr>
        </thead>
        <tbody>
            {html_rows_labor}
            <tr class="total" style="background-color: #e3f2fd !important;">
                <td colspan="6" style="text-align: right;">TOPLAM USTA MALİYET BÜTÇESİ (%100 BİTTİĞİNDE):</td>
                <td colspan="2">₺ {total_project_labor_value:,.2f}</td>
            </tr>
            <tr class="total">
                <td colspan="6" style="text-align: right;">ŞU ANA KADAR HAK EDİLEN USTA TOPLAM ALACAĞI:</td>
                <td colspan="2">₺ {total_labor_cost_current:,.2f}</td>
            </tr>
            <tr class="total" style="background-color: #fff3cd !important;">
                <td colspan="6" style="text-align: right;">USTALARA ÖDENEN TOPLAM MİKTAR:</td>
                <td colspan="2">₺ {total_labor_paid:,.2f}</td>
            </tr>
            <tr class="total" style="background-color: #f8d7da !important;">
                <td colspan="6" style="text-align: right;">USTALARA KALAN BORÇ DURUMU:</td>
                <td colspan="2">₺ {labor_rest:,.2f}</td>
            </tr>
        </tbody>
    </table>
    """
    
    final_labor_report_code = make_report_wrapper("Havence - Resmi Alt Yüklenici / Usta Hakediş Raporu", full_html_labor)
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="📄 Raporu PDF / HTML Olarak İndir (Ustalar İçin)",
        data=final_labor_report_code,
        file_name=f"Havence_Usta_Hakedis_Raporu_{date.today().strftime('%d_%m_%Y')}.html",
        mime="text/html"
    )

    st.markdown("---")
    st.sidebar.markdown("---")
    df_labor_styled = pd.DataFrame(labor_report)
    st.dataframe(df_labor_styled.style.apply(highlight_completed, axis=1), use_container_width=True)

# --- MODÜL 4: HAVENCE KARLILIK & GENEL MUHASEBE ANALİZİ ---
elif app_page == "📊 Havence Kârlılık Analizi":
    st.header("📊 Havence Şantiye Finansal Kârlılık ve Hak Ediş Analiz Paneli")
    
    # Mevcut Listeleri Session State'ten çekme
    expenses_list = get_state_val("accounting_expenses", [])
    external_income_list = get_state_val("accounting_income", [])
    
    # Hakediş Bazlı Kârlılık Hesaplamaları
    net_profit_current = total_billing_owner_current - total_labor_cost_current
    margin_current = ((net_profit_current / total_billing_owner_current) * 100 if total_billing_owner_current > 0 else 0)
    
    total_expected_profit = total_project_owner_value - total_project_labor_value
    expected_margin = ((total_expected_profit / total_project_owner_value) * 100 if total_project_owner_value > 0 else 0)

    # --- YENİ MUHASEBE GİRİŞ FORMLARI ---
    st.markdown("---")
    st.subheader("📝 Şantiye Finansal Hareket Girişleri (Harcama, Gelir ve Usta Ödemesi)")
    
    acc_tabs = st.tabs(["💸 Şantiye Gideri Kaydet", "💰 Harici Gelir / İşveren Avansı Ekle", "👷 Kasadan Usta Ödemesi (Avans)"])
    
    # TAB 1: HARCAMA/GİDER GİRİŞİ
    with acc_tabs[0]:
        col_e1, col_e2, col_e3 = st.columns([2, 3, 2])
        with col_e1:
            exp_date = st.date_input("Harcama Tarihi", value=date.today(), key="exp_input_dt")
        with col_e2:
            exp_info = st.text_input("Gider Açıklaması / Detay Bilgisi", placeholder="Örn: Tesisat boruları, Nakliye bedeli, Hırdavat")
        with col_e3:
            exp_cost = st.number_input("Harcama Maliyeti (₺)", min_value=0.0, step=100.0, key="exp_input_cost")
            
        if st.button("💸 Harcamayı Kaydet", use_container_width=True):
            if exp_cost > 0 and exp_info:
                expenses_list.append({
                    "id": len(expenses_list) + 1,
                    "Tarih": exp_date.strftime("%d.%m.%Y"),
                    "Açıklama": exp_info,
                    "Maliyet": exp_cost
                })
                update_state_val("accounting_expenses", expenses_list)
                st.success(f"Kaydedildi: {exp_info} - ₺{exp_cost:,.2f}")
                st.rerun()

    # TAB 2: GELİR GİRİŞİ (İŞVEREN VEYA HARCİ KAYNAK)
    with acc_tabs[1]:
        col_i1, col_i2, col_i3 = st.columns([2, 3, 2])
        with col_i1:
            inc_date = st.date_input("Gelir Tarihi", value=date.today(), key="inc_input_dt")
        with col_i2:
            inc_info = st.text_input("Gelir Kaynağı / Bilgi Notu", placeholder="Örn: İşveren hakediş ödemesi, Ortak kasa transferi")
        with col_i3:
            inc_amount = st.number_input("Gelen Tutar (₺)", min_value=0.0, step=500.0, key="inc_input_amt")
            
        if st.button("💰 Geliri Kasaya Ekle", use_container_width=True):
            if inc_amount > 0 and inc_info:
                external_income_list.append({
                    "id": len(external_income_list) + 1,
                    "Tarih": inc_date.strftime("%d.%m.%Y"),
                    "Kaynak / Detay": inc_info,
                    "Miktar": inc_amount
                })
                update_state_val("accounting_income", external_income_list)
                st.success(f"Gelir Kaydedildi: {inc_info} - ₺{inc_amount:,.2f}")
                st.rerun()
                
    # TAB 3: USTAYA FİİLİ ÖDENEN (KASADAN ALINAN)
    with acc_tabs[2]:
        st.markdown("💡 *Bu alandan yapılan girişler direkt olarak '👷 Usta Hak Edişleri' sayfasındaki ödeme geçmişine de yansır.*")
        labor_payments_history = get_state_val("labor_payments_history_list", [])
        col_l1, col_l2 = st.columns([2, 2])
        with col_l1:
            new_lp_amount = st.number_input("Ustalara Ödenen Tutar (₺):", min_value=0.0, step=1000.0, key="acc_lp_amt")
        with col_l2:
            new_lp_date = st.date_input("Ödeme Yapılma Tarihi:", value=date.today(), key="acc_lp_dt")
            
        if st.button("📤 Usta Avans/Ödemesini Onayla", use_container_width=True):
            if new_lp_amount > 0:
                labor_payments_history.append({"Tarih": new_lp_date.strftime("%d.%m.%Y"), "Miktar": new_lp_amount})
                update_state_val("labor_payments_history_list", labor_payments_history)
                st.success(f"Usta ödemesi sisteme işlendi: ₺{new_lp_amount:,.2f}")
                st.rerun()

    # --- TOPLAM HESAPLAMALAR ---
    total_expenses_sum = sum([item["Maliyet"] for item in expenses_list])
    total_income_sum = sum([item["Miktar"] for item in external_income_list])
    total_labor_paid_sum = sum([p["Miktar"] for p in get_state_val("labor_payments_history_list", [])])
    
    # Gerçek Nakit Dengesi (Net Kasa)
    net_cash_balance = total_income_sum - (total_expenses_sum + total_labor_paid_sum)

    st.markdown("---")
    st.subheader("🎯 Proje Geneli Finansal Dağılım Özetleri")
    
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.markdown("#### ⏳ Şimdiki Durum (Mevcut İlerlemeye Göre)")
        st.metric("İşveren Mevcut Hakediş (Gelir)", f"₺ {total_billing_owner_current:,.2f}")
        st.metric("Usta Mevcut Maliyeti (Gider)", f"₺ {total_labor_cost_current:,.2f}")
        st.metric("Havence Şimdiki Net Kâr", f"₺ {net_profit_current:,.2f}", delta=f"% {margin_current:.1f} Mevcut Marj")
        
    with p_col2:
        st.markdown("#### 🏁 Tam Kapasite Durumu (%100 Tamamlandığında)")
        st.metric("Toplam Hedeflenen Proje Değeri", f"₺ {total_project_owner_value:,.2f}")
        st.metric("Toplam Hedeflenen Usta Maliyeti", f"₺ {total_project_labor_value:,.2f}")
        st.metric("Havence Toplam Beklenen Net Kâr", f"₺ {total_expected_profit:,.2f}", delta=f"% {expected_margin:.1f} Hedeflenen Marj")

    # --- KASA DURUMU VE NAKİT AKIŞI GÖSTERGESİ ---
    st.markdown("---")
    st.subheader("🏪 Havence Şantiye Gerçek Nakit Akışı Bilgileri (Kasa)")
    
    k_col1, k_col2, k_col3, k_col4 = st.columns(4)
    k_col1.metric("Kasaya Giren Toplam Nakit", f"₺ {total_income_sum:,.2f}")
    k_col2.metric("Malzeme / Şantiye Giderleri", f"₺ {total_expenses_sum:,.2f}")
    k_col3.metric("Ustalara Ödenen Nakit", f"₺ {total_labor_paid_sum:,.2f}")
    
    if net_cash_balance >= 0:
        k_col4.metric("💰 Güncel Kasa Net Durumu (Kârda)", f"₺ {net_cash_balance:,.2f}", delta="Nakit Akışı Pozitif", delta_color="normal")
    else:
        k_col4.metric("⚠️ Güncel Kasa Net Durumu (İçeride)", f"₺ {net_cash_balance:,.2f}", delta="Nakit Akışı Negatif / Finanse Ediliyor", delta_color="inverse")

    # --- DETAYLI LİSTELER PANELİ ---
    st.markdown("---")
    show_list_col1, show_list_col2 = st.columns(2)
    
    with show_list_col1:
        st.markdown("#### 📝 Detaylı Gider Listesi (Malzeme & Diğer)")
        if expenses_list:
            df_exp = pd.DataFrame(expenses_list)[["Tarih", "Açıklama", "Maliyet"]]
            st.dataframe(df_exp, use_container_width=True)
            if st.button("🗑️ Tüm Gider Listesini Temizle", key="clear_all_expenses"):
                update_state_val("accounting_expenses", [])
                st.rerun()
        else:
            st.info("Kayıtlı herhangi bir şantiye gideri bulunmuyor.")
            
    with show_list_col2:
        st.markdown("#### 📥 Detaylı Gelir Listesi (İşveren & Dış Kaynak)")
        if external_income_list:
            df_inc = pd.DataFrame(external_income_list)[["Tarih", "Kaynak / Detay", "Miktar"]]
            st.dataframe(df_inc, use_container_width=True)
            if st.button("🗑️ Tüm Gelir Listesini Temizle", key="clear_all_income"):
                update_state_val("accounting_income", [])
                st.rerun()
        else:
            st.info("Kayıtlı herhangi bir şantiye geliri bulunmuyor.")

# --- DİĞER MODÜLLER (İÇ/DIŞ CEPE UYGULAMALARI VB.) ---
else:
    st.header(f"🏗️ {app_page}")
    st.markdown("Seçilen alandaki yapı bölümlerinin imalat aşamalarını aşağıdan yönetebilirsiniz.")
    
    type_filter = "interior"
    if "Dış Cephe" in app_page:
        type_filter = "exterior"
    elif "Tuvalet" in app_page:
        type_filter = "toilet"
    elif "Zaman Çizelgesi" in app_page:
        st.info("Şantiye Günlüğü ve Zaman Çizelgesi aktif çalışma modülünded r.")
        type_filter = "none"

    if type_filter != "none":
        for floor_name, sections in project_structure.items():
            valid_secs = {k: v for k, v in sections.items() if (type_filter in v["type"])}
            if valid_secs:
                with st.expander(f"🏢 {floor_name}", expanded=True):
                    for sec_name, info in valid_secs.items():
                        # Global index tespiti
                        matching_item = next((x for x in flat_sections if x["floor"] == floor_name and x["section"] == sec_name), None)
                        if matching_item:
                            g_id = matching_item["global_idx"]
                            st.markdown(f"**📍 {sec_name}** ({info['area']:.2f} m²)")
                            
                            cols = st.columns(len(matching_item["phases"]))
                            for i, (p_code, p_name, checked) in enumerate(matching_item["phases"]):
                                with cols[i]:
                                    cb_key = f"cb_ui_{p_code}_{g_id}"
                                    save_key = f"cb_{p_code}_{g_id}"
                                    date_key = f"date_{p_code}_{g_id}"
                                    
                                    is_checked = st.checkbox(p_name, value=checked, key=cb_key, 
                                                             on_change=handle_checkbox_change, args=(cb_key, save_key, date_key))
                                    
                                    current_date = get_state_val(date_key, "")
                                    if current_date:
                                        st.caption(f"🗓️ {current_date}")
                            st.markdown("---")
