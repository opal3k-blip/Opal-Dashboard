import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Dropbox 10K Dynamic Dashboard", layout="wide")

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
        
        return df
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
        return pd.DataFrame()

# --- دالة لإنشاء مؤشرات KPIs احترافية وديناميكية ---
def render_kpis(filtered_df, total_size_mb_all, title_prefix="للكل"):
    st.markdown(f"<h3 class='section-header'>📌 مؤشرات أداء رئيسية متقدمة ({title_prefix})</h3>", unsafe_allow_html=True)
    
    # التأكد من عدم القسمة على صفر
    num_files = len(filtered_df)
    total_size_mb = filtered_df['Size (MB)'].sum()
    total_size_gb = filtered_df['Size (GB)'].sum()
    avg_size_mb = filtered_df['Size (MB)'].mean()
    
    # حساب الشركة الأكثر استهلاكاً
    filtered_df['top_folder'] = filtered_df['parent_path'].apply(lambda x: x.split('/')[0])
    grouped_company = filtered_df.groupby('top_folder')['Size (MB)'].sum()
    top_company = grouped_company.idxmax()
    top_company_size_mb = grouped_company.max()
    top_company_perc = (top_company_size_mb / total_size_mb) * 100 if total_size_mb > 0 else 0
    
    # النوع الأكثر شيوعاً (حجماً)
    grouped_ext = filtered_df.groupby('extension')['Size (MB)'].sum()
    top_ext_size = grouped_ext.idxmax()
    top_ext_size_mb = grouped_ext.max()
    top_ext_perc = (top_ext_size_mb / total_size_mb) * 100 if total_size_mb > 0 else 0
    
    # حساب أكثر المجلدات عمقاً
    filtered_df['path_depth'] = filtered_df['parent_path'].apply(lambda x: len(x.split('/')))
    max_depth = filtered_df['path_depth'].max()

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"<div class='kpi-box'><div class='kpi-title'>إجمالي الملفات</div><div class='kpi-value'>{num_files:,}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='kpi-box'><div class='kpi-title'>إجمالي الحجم (GB)</div><div class='kpi-value'>{total_size_gb:.2f}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='kpi-box'><div class='kpi-title'>متوسط حجم الملف</div><div class='kpi-value'>{avg_size_mb:.2f}</div><div class='kpi-sub'>MB</div></div>", unsafe_allow_html=True)
    with col4:
         st.markdown(f"<div class='kpi-box'><div class='kpi-title'>الشركة الأكثر استهلاكاً</div><div class='kpi-value'>{top_company}</div><div class='kpi-sub'>{top_company_size_mb/1024:.1f} GB ({top_company_perc:.1f}%)</div></div>", unsafe_allow_html=True)
    with col5:
         st.markdown(f"<div class='kpi-box'><div class='kpi-title'>النوع المهيمن (حجماً)</div><div class='kpi-value'>.{top_ext_size}</div><div class='kpi-sub'>{top_ext_size_mb/1024:.1f} GB ({top_ext_perc:.1f}%)</div></div>", unsafe_allow_html=True)
    with col6:
         st.markdown(f"<div class='kpi-box'><div class='kpi-title'>أكثر المجلدات عمقاً</div><div class='kpi-value'>{max_depth} مستويات</div></div>", unsafe_allow_html=True)

# --- دالة لإنشاء ملف Excel للتحميل ---
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DropboxData')
    processed_data = output.getvalue()
    return processed_data

# --- تحميل البيانات ---
df = load_data()

if not df.empty:
    
    # حساب القيم الأساسية
    total_size_mb_all = df['Size (MB)'].sum()
    df['top_folder'] = df['parent_path'].apply(lambda x: x.split('/')[0])
    all_paths = sorted(list(df['parent_path'].unique()))
    
    # --- 1. قائمة منسدلة ديناميكية للفلترة ---
    st.markdown("<h2 class='section-header'>📂 فلترة البيانات واستكشاف المجلدات الديناميكية</h2>", unsafe_allow_html=True)
    st.write("اختر مجلداً محدداً من القائمة أدناه لتحديث لوحة التحكم بالكامل فوراً:")
    
    # إنشاء القائمة: الكل + الشركات الرئيسية + المجلدات الفرعية العميقة
    dropdown_options = ["(عرض كامل الـ 10K ملف)"] + sorted(list(df['top_folder'].unique())) + all_paths
    selected_filter = st.selectbox("", dropdown_options, index=0)
    
    st.markdown("---")

    # --- إدارة الـ KPIs الديناميكية (تفاعلية حقيقية ومستقرة) ---
    if selected_filter == "(عرض كامل الـ 10K ملف)":
        render_kpis(df, total_size_mb_all, "للكل")
        current_data = df.copy()
    elif selected_filter in df['top_folder'].unique():
        # النقر على الشركة الرئيسية
        filtered_df = df[df['top_folder'] == selected_filter].copy()
        render_kpis(filtered_df, total_size_mb_all, f"لشركة: {selected_filter}")
        current_data = filtered_df.copy()
    else:
         # النقر على مجلد فرعي عميق
         filtered_df = df[df['parent_path'].str.startswith(selected_filter)].copy()
         render_kpis(filtered_df, total_size_mb_all, f"للمجلد: {selected_filter}")
         current_data = filtered_df.copy()

    st.markdown("---")

    # --- 2. التحليل الهرمي العميق (Sunburst Chart) - الإصلاح ---
    st.markdown("<h2 class='section-header'>🏢 استكشاف الهيكل الهرمي وتوزيع المساحة (تفاعلي)</h2>", unsafe_allow_html=True)
    
    # تجميع البيانات لضمان اتساق مخطط Sunburst (يعمل على البيانات المفلترة حالياً)
    folder_agg_df = current_data.groupby('parent_path')['Size (MB)'].sum().reset_index()
    folder_agg_df['top_folder'] = folder_agg_df['parent_path'].apply(lambda x: x.split('/')[0])
    
    # رسم مخطط Sunburst بالبيانات المجمعة المتسقة
    fig_sun = px.sunburst(folder_agg_df, path=['top_folder', 'parent_path'], values='Size (MB)', color='top_folder', title='انقر فوق أي جزء لاستكشاف المجلدات الفرعية العميقة وتوزيع الحجم', hover_data={'top_folder': True, 'parent_path': True, 'Size (MB)': ':.2f'})
    fig_sun.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    st.plotly_chart(fig_sun, use_container_width=True)
    
    st.markdown("---")

    # --- 3. تحليل تفصيلي لمحتويات الملفات ونسبها (Pivot Analysis & Percentages) ---
    st.markdown("<h2 class='section-header'>📄 تحليل محتويات وأنواع الملفات وحجومها والنسب مئوية</h2>", unsafe_allow_html=True)
    
    # تجميع البيانات بشكل متقدم وحساب النسب (يعمل على البيانات المفلترة حالياً)
    ext_df = current_data.groupby('extension').agg(
        total_size_mb=('Size (MB)', 'sum'),
        file_count=('name', 'count')
    ).reset_index()
    
    total_size_mb_current = current_data['Size (MB)'].sum()
    if total_size_mb_current > 0:
        ext_df['percentage'] = (ext_df['total_size_mb'] / total_size_mb_current) * 100
    else:
        ext_df['percentage'] = 0
        
    ext_df.columns = ['نوع الملف', 'إجمالي الحجم (MB)', 'عدد الملفات', 'النسبة مئوية (%)']
    ext_df = ext_df.sort_values(by='إجمالي الحجم (MB)', ascending=False)
    
    # تنسيق الجدول للعرض
    ext_formatted = ext_df.copy()
    ext_formatted['إجمالي الحجم (MB)'] = ext_formatted['إجمالي الحجم (MB)'].map('{:,.2f}'.format)
    ext_formatted['عدد الملفات'] = ext_formatted['عدد الملفات'].map('{:,}'.format)
    ext_formatted['النسبة مئوية (%)'] = ext_formatted['النسبة مئوية (%)'].map('{:.1f}%'.format)
    
    st.markdown("#### جدول تحليلي لمحتويات وأنواع الملفات ونسبها:")
    st.dataframe(ext_formatted, use_container_width=True, height=400)
    
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("#### رسم بياني دائري: توزيع إجمالي الحجم حسب النوع (نسب مئوية):")
        fig_pie = px.pie(ext_df.head(8), names='نوع الملف', values='إجمالي الحجم (MB)', hole=0.4, title='أكبر 8 أنواع ملفات (نسب مئوية)')
        st.plotly_chart(fig_pie, use_container_width=True)
    with chart_col2:
        st.markdown("#### رسم بياني شريطي: عدد الملفات لكل نوع (أكبر 10):")
        fig_bar_count = px.bar(ext_df.head(10), x='نوع الملف', y='عدد الملفات', title='أكبر 10 أنواع من حيث عدد الملفات', labels={'عدد الملفات': 'عدد الملفات'})
        st.plotly_chart(fig_bar_count, use_container_width=True)

    st.markdown("---")

    # --- 4. خانات تحميل البيانات (Excel Download) ---
    st.markdown("<h2 class='section-header'>📥 تحميل تقارير البيانات (Excel)</h2>", unsafe_allow_html=True)
    st.write("احصل على ملف Excel يحتوي على كافة الصفوف الـ 10,000 والتفاصيل الكاملة.")
    excel_data = to_excel(df)
    st.download_button(label="📥 تحميل ملف Excel", data=excel_data, file_name='dropbox_data_10k.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

else:
    pass

st.markdown("---")
st.caption("تم إنشاء هذه اللوحة الاحترافية ببياناتك الفعلية من ملف 'خريطة ملفات الدروبكس.csv' باستخدام Streamlit, Pandas, & Plotly.")
