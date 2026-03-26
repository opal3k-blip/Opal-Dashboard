import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Dropbox 10K Dynamic Pro Dashboard", layout="wide")

# --- تنسيق مخصص (CSS) لتحسين المظهر ---
st.markdown("""
<style>
    .kpi-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .kpi-title {
        font-size: 16px;
        color: #5c5c5c;
        margin-bottom: 5px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: bold;
        color: #1f77b4;
    }
    .kpi-sub {
        font-size: 14px;
        color: #888;
    }
    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 10px;
        margin-top: 30px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- عنوان التطبيق ---
st.title("📊 لوحة تحكم Dropbox الاحترافية الديناميكية (تحليل عميق لـ 10K ملف)")
st.markdown("---")

# --- دالة لتحميل وتنظيف البيانات ---
@st.cache_data
def load_data():
    # اسم ملف البيانات الفعلي الذي قدمته (تأكد من وجوده في نفس مجلد الكود)
    data_file = 'خريطة_ملفات_الدروبكس_المعدلة.csv'
    
    # التأكد من وجود الملف في نفس مجلد الكود
    if not os.path.exists(data_file):
        st.error(f"⚠️ لم يتم العثور على ملف البيانات: '{data_file}'. تأكد من وضعه في نفس مجلد الكود وأن اسمه صحيح تماماً.")
        return pd.DataFrame()

    try:
        # قراءة الملف، مع التأكد من ترميز utf-8 لقراءة الحروف العربية
        df = pd.read_csv(data_file, encoding='utf-8') 
        
        # تنظيف البيانات الأساسي: إزالة الصفوف الفارغة بالكامل
        df.dropna(how='all', inplace=True)
        
        # تحويل عمود الحجم إلى ميغابايت (MB) من عمود 'Size (Bytes)' الموجود في ملفك
        if 'Size (Bytes)' in df.columns:
            df['Size (MB)'] = pd.to_numeric(df['Size (Bytes)']) / (1024 * 1024) # تحويل من بايت لـ MB
            df['Size (GB)'] = df['Size (MB)'] / 1024 # تحويل لـ GB
        else:
             st.warning("تنبيه: لم يتم العثور على عمود 'Size (Bytes)'.")
            
        return df
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
        return pd.DataFrame()

# --- دالة لإنشاء مؤشرات KPIs احترافية وديناميكية ---
def render_kpis(filtered_df, total_files, title_prefix="للكل"):
    st.markdown(f"<h3 class='section-header'>📌 مؤشرات أداء رئيسية متقدمة لـ 10K ملف ({title_prefix})</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    # حساب القيم الأساسية
    num_files = len(filtered_df)
    total_size_mb = filtered_df['Size (MB)'].sum()
    total_size_gb = filtered_df['Size (GB)'].sum()
    avg_size_mb = filtered_df['Size (MB)'].mean()
    
    # النوع الأكثر شيوعاً (حجماً)
    total_mb_all = filtered_df['Size (MB)'].sum()
    top_ext_size = filtered_df.groupby('extension')['Size (MB)'].sum().idxmax()
    top_ext_size_mb = filtered_df.groupby('extension')['Size (MB)'].sum().max()
    if total_mb_all > 0:
        top_ext_perc = (top_ext_size_mb / total_mb_all) * 100
    else:
        top_ext_perc = 0
    
    # حساب أكثر المجلدات عمقاً
    filtered_df['path_depth'] = filtered_df['parent_path'].apply(lambda x: len(x.split('/')))
    max_depth = filtered_df['path_depth'].max()

    # عرض الـ KPIs الـ 6 المفصلة والاحترافية
    with col1:
        st.markdown(f"<div class='kpi-box'><div class='kpi-title'>إجمالي الملفات</div><div class='kpi-value'>{num_files:,}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='kpi-box'><div class='kpi-title'>إجمالي الحجم (GB)</div><div class='kpi-value'>{total_size_gb:.2f}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='kpi-box'><div class='kpi-title'>متوسط حجم الملف</div><div class='kpi-value'>{avg_size_mb:.2f}</div><div class='kpi-sub'>MB</div></div>", unsafe_allow_html=True)
    with col4:
         st.markdown(f"<div class='kpi-box'><div class='kpi-title'>النوع المهيمن (حجماً)</div><div class='kpi-value'>.{top_ext_size}</div><div class='kpi-sub'>{top_ext_size_mb/1024:.1f} GB ({top_ext_perc:.1f}%)</div></div>", unsafe_allow_html=True)
    with col5:
         st.markdown(f"<div class='kpi-box'><div class='kpi-title'>أكثر المجلدات عمقاً</div><div class='kpi-value'>{max_depth} مستويات</div></div>", unsafe_allow_html=True)
    with col6:
         st.markdown(f"<div class='kpi-box'><div class='kpi-title'>عدد الشركات الرئيسية المدمجة</div><div class='kpi-value'>{len(filtered_df['parent_path'].apply(lambda x: x.split('/')[0]).unique())}</div></div>", unsafe_allow_html=True)

# --- دالة لإنشاء ملف Excel للتحميل ---
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DropboxData')
    processed_data = output.getvalue()
    return processed_data

# --- تحميل البيانات (هنا يتم تعريف متغير df) ---
df = load_data()

# --- التحقق من وجود البيانات ---
if not df.empty:
    
    # إنشاء حاوية لتحديث الـ KPIs والمخططات بناءً على الاختيار
    st.markdown("<h2 class='section-header'>🏢 استكشاف الهيكل الهرمي وتوزيع المساحة (تفاعلي)</h2>", unsafe_allow_html=True)
    st.write("انقر فوق أي جزء لاستكشاف المجلدات الفرعية العميقة وتحديث المؤشرات والنسب مئوية.")
    
    # أولاً: رسم مخطط Sunburst التفاعلي
    fig_sun = px.sunburst(df, path=['top_folder', 'parent_path'], values='Size (MB)', color='top_folder', hover_data={'top_folder': True, 'parent_path': True, 'Size (MB)': ':.2f'})
    fig_sun.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    
    # جعل المخطط تفاعلي مع Streamlit
    sunburst_event = st.plotly_chart(fig_sun, use_container_width=True, on_select="rerun", selection_mode="point")
    
    st.markdown("---")

    # --- 2. إدارة الـ KPIs الديناميكية (تفاعلية) ---
    # تحديد البيانات التي تم اختيارها من مخطط Sunburst
    selected_points = sunburst_event.get("selection", {}).get("points", [])
    
    if selected_points:
# استخراج المسار الذي تم النقر عليه (مثلاً ["Jadeer"])
