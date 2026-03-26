import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Dropbox 10K Dynamic Pro Dashboard", layout="wide")

# --- تنسيق مخصص (CSS) لجعل اللوحة احترافية جداً ---
st.markdown("""
<style>
    /* تنسيق بطاقة المؤشر الواحد */
    .kpi-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        text-align: center;
        border: 1px solid #e1e4e8;
    }
    /* تنسيق عنوان المؤشر */
    .kpi-title {
        font-size: 14px;
        color: #6a737d;
        font-weight: 500;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    /* تنسيق قيمة المؤشر الرئيسية */
    .kpi-value {
        font-size: 26px;
        font-weight: 800;
        color: #1f77b4;
    }
    /* تنسيق النص الفرعي للمؤشر */
    .kpi-sub {
        font-size: 13px;
        color: #888;
        margin-top: 5px;
    }
    /* تنسيق العناوين الرئيسية */
    .section-header {
        color: #1f77b4;
        font-weight: bold;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 12px;
        margin-top: 40px;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# --- عنوان التطبيق ---
st.title("📊 لوحة تحكم Dropbox الاحترافية الديناميكية (تحليل عميق لـ 10K ملف)")
st.markdown("---")

# --- دالة لتحميل وتنظيف البيانات (مع دمج 'جدير') ---
@st.cache_data
def load_data():
    data_file = 'خريطة_ملفات_الدروبكس_المعدلة.csv'
    
    if not os.path.exists(data_file):
        st.error(f"⚠️ لم يتم العثور على ملف البيانات: '{data_file}'. تأكد من وضعه في نفس مجلد الكود.")
        return pd.DataFrame()

    try:
        df = pd.read_csv(data_file, encoding='utf-8') 
        df.dropna(how='all', inplace=True)
        
        if 'Size (Bytes)' in df.columns:
            df['Size (MB)'] = pd.to_numeric(df['Size (Bytes)']) / (1024 * 1024)
            df['Size (GB)'] = df['Size (MB)'] / 1024
            
        # --- دمج 'جدير' ---
        df['top_folder'] = df['parent_path'].apply(lambda x: x.split('/')[0])
        df.loc[df['top_folder'].str.startswith('Jadeer'), 'top_folder'] = 'Jadeer'
        
        return df
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
        return pd.DataFrame()

# --- دالة لإنشاء مؤشرات KPIs احترافية وديناميكية ---
def render_kpis(filtered_df, total_files, title_prefix="للكل"):
    st.markdown(f"<h3 class='section-header'>📌 مؤشرات أداء رئيسية متقدمة لـ 10K ملف ({title_prefix})</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    
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

    # أكبر ملف منفرد
    largest_file = filtered_df.sort_values(by='Size (MB)', ascending=False).iloc[0]

    # عرض الـ KPIs الـ 7 المفصلة والاحترافية
    with col1:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>إجمالي الملفات</div><div class='kpi-value'>{num_files:,}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>إجمالي الحجم (GB)</div><div class='kpi-value'>{total_size_gb:.2f}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>متوسط حجم الملف</div><div class='kpi-value'>{avg_size_mb:.2f}</div><div class='kpi-sub'>MB</div></div>", unsafe_allow_html=True)
    with col4:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>أكبر ملف منفرد</div><div class='kpi-value'>{largest_file['Size (MB)']:.1f}</div><div class='kpi-sub'>{largest_file['name'][:15]}... MB</div></div>", unsafe_allow_html=True)
    with col5:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>النوع المهيمن (حجماً)</div><div class='kpi-value'>.{top_ext_size}</div><div class='kpi-sub'>{top_ext_size_mb/1024:.1f} GB ({top_ext_perc:.1f}%)</div></div>", unsafe_allow_html=True)
    with col6:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>أكثر المجلدات عمقاً</div><div class='kpi-value'>{max_depth} مستويات</div></div>", unsafe_allow_html=True)
    with col7:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>الشركات الرئيسية المدمجة</div><div class='kpi-value'>{len(filtered_df['top_folder'].unique())}</div></div>", unsafe_allow_html=True)

# --- دالة لإنشاء ملف Excel للتحميل ---
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DropboxData')
    processed_data = output.getvalue()
    return processed_data

# --- تحميل البيانات ---
df = load_data()

# --- التحقق من وجود البيانات ---
if not df.empty:
    
    # استخراج كافة المسارات الفرعية العميقة
    all_paths = sorted(list(df['parent_path'].unique()))
    
    # --- 1. قائمة منسدلة ديناميكية للفلترة ---
    st.markdown("<h2 class='section-header'>📂 فلترة البيانات واستكشاف المجلدات الديناميكية</h2>", unsafe_allow_html=True)
    st.write("اختر مجلداً محدداً من القائمة أدناه لتحديث لوحة التحكم بالكامل فوراً:")
    
    # إنشاء القائمة: الكل + الشركات الرئيسية المدمجة + المجلدات الفرعية العميقة
    dropdown_options = ["(عرض كامل الـ 10K ملف)"] + sorted(list(df['top_folder'].unique())) + all_paths
    selected_filter = st.selectbox("", dropdown_options, index=0)
    
    st.markdown("---")

    # --- إدارة الـ KPIs الديناميكية (تفاعلية حقيقية ومستقرة) ---
    if selected_filter == "(عرض كامل الـ 10K ملف)":
        render_kpis(df, len(df), "للكل - تم دمج 'جدير'")
        current_data = df.copy()
    elif selected_filter in df['top_folder'].unique():
        # النقر على الشركة الرئيسية المدمجة
        filtered_df = df[df['top_folder'] == selected_filter].copy()
        render_kpis(filtered_df, len(df), f"لشركة: {selected_filter}")
        current_data = filtered_df.copy()
    else:
         # النقر على مجلد فرعي عميق
         filtered_df = df[df['parent_path'].str.startswith(selected_filter)].copy()
         render_kpis(filtered_df, len(df), f"للمجلد: {selected_filter}")
         current_data = filtered_df.copy()

    st.markdown("---")

    # --- 2. التحليل الهرمي العميق (Sunburst Chart) - إلغاء التفاعل لمنع الخطأ ---
    st.markdown("<h2 class='section-header'>🏢 استكشاف الهيكل الهرمي وتوزيع المساحة (تفاعلي - تم دمج 'جدير')</h2>", unsafe_allow_html=True)
    
    # Sunburst Chart بالبيانات المجمعة المتسقة (تم
