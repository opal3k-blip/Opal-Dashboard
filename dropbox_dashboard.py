import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Dropbox 10K Pro Dashboard", layout="wide")

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
    .download-section {
        background-color: #eaf2f8;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- عنوان التطبيق ---
st.title("📊 لوحة تحكم Dropbox الاحترافية (تحليل عميق لـ 10K ملف مع التحميل)")
st.markdown("---")

# --- دالة لتحميل وتنظيف البيانات ---
@st.cache_data
def load_data():
    data_file = 'خريطة_ملفات_الدروبكس_المعدلة.csv'
    
    if not os.path.exists(data_file):
        st.error(f"⚠️ لم يتم العثور على ملف البيانات: '{data_file}'.")
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

# --- دالة لإنشاء ملف Excel للتحميل ---
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DropboxData')
        # تنسيق العمود 'Size (MB)' ليكون رقماً
        # workbook = writer.book
        # worksheet = writer.sheets['DropboxData']
        # format = workbook.add_format({'num_format': '#,##0.00'})
        # worksheet.set_column('C:C', 15, format)
    processed_data = output.getvalue()
    return processed_data

# --- دالة لإنشاء ملخص PDF للتحميل ---
# ملاحظة: إنشاء PDF حقيقي يحتاج مكتبة مثل FPDF، لكن سننشئ ملف نصي كملخص سريع للتجربة
def to_pdf_summary(df, total_size_gb, top_company, top_ext_size):
    output = io.StringIO()
    output.write("Dropbox 10K Pro Dashboard Summary\n")
    output.write("=================================\n\n")
    output.write(f"إجمالي الملفات: {len(df):,}\n")
    output.write(f"إجمالي الحجم (GB): {total_size_gb:.2f} GB\n")
    output.write(f"متوسط حجم الملف: {df['Size (MB)'].mean():.2f} MB\n\n")
    output.write(f"الشركة الأكثر استهلاكاً: {top_company}\n")
    output.write(f"النوع الأكثر شيوعاً: .{top_ext_size}\n")
    output.write("-" * 30 + "\n")
    
    processed_data = output.getvalue()
    return processed_data

# --- تحميل البيانات ---
df = load_data()

if not df.empty:
    
    # حساب القيم الأساسية للـ KPIs
    total_size_mb = df['Size (MB)'].sum()
    total_size_gb = df['Size (GB)'].sum()
    avg_size_mb = df['Size (MB)'].mean()
    
    df['top_folder'] = df['parent_path'].apply(lambda x: x.split('/')[0])
    top_company = df.groupby('top_folder')['Size (MB)'].sum().idxmax()
    top_company_size_mb = df.groupby('top_folder')['Size (MB)'].sum().max()
    top_company_perc = (top_company_size_mb / total_size_mb) * 100
    
    top_ext_size = df.groupby('extension')['Size (MB)'].sum().idxmax()
    top_ext_size_mb = df.groupby('extension')['Size (MB)'].sum().max()
    top_ext_perc = (top_ext_size_mb / total_size_mb) * 100
    
    df['path_depth'] = df['parent_path'].apply(lambda x: len(x.split('/')))
    max_depth = df['path_depth'].max()

    # --- 1. مجموعة محترفة ومفصلة من المؤشرات الرئيسية (KPIs) ---
    st.markdown("<h2 class='section-header'>📌 مؤشرات أداء رئيسية (KPIs) متقدمة لـ 10K ملف</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"<div class='kpi-box'><div class='kpi-title'>إجمالي الملفات</div><div class='kpi-value'>{len(df):,}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='kpi-box'><div class='kpi-title'>إجمالي الحجم (GB)</div><div class='kpi-value'>{total_size_gb:.2f}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='kpi-box'><div class='kpi-title'>متوسط حجم الملف</div><div class='kpi-value'>{avg_size_mb:.2f}</div><div class='kpi-sub'>MB</div></div>", unsafe_allow_html=True)
    with col4:
         st.markdown(f"<div class='kpi-box'><div class='kpi-title'>الشركة الأكثر استهلاكاً</div><div class='kpi-value'>{top_company}</div><div class='kpi-sub'>{top_company_size_mb/1024:.1f} GB ({top_company_perc:.1f}%)</div></div>", unsafe_allow_html=True)
    with col5:
         st.markdown(f"<div class='kpi-box'><div class='kpi-title'>النوع المهيمن (حجماً)</div><div class='kpi-value'>.{top_ext_size}</div><div class='kpi-sub'>{top_ext_size_mb/1024:.1f} GB ({top_ext_perc:.1f}%)</div></div>", unsafe_allow_html=True)
    with col6:
         st.markdown(f"<div class='kpi-box'><div class='kpi-title'>أكثر المجلدات عمقاً</div><div class='kpi-value'>{max_depth}</div><div class='kpi-sub'>مستويات هرمية</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # --- 2. التحليل الهرمي العميق (Sunburst Chart) ---
    st.markdown("<h2 class='section-header'>🏢 استكشاف الهيكل الهرمي وتوزيع المساحة (تفاعلي)</h2>", unsafe_allow_html=True)
    fig_sun = px.sunburst(df, path=['top_folder', 'parent_path'], values='Size (MB)', color='top_folder', title='استكشف توزيع الحجم هرمياً: انقر فوق الأجزاء', hover_data={'Size (MB)': ':.2f'})
    fig_sun.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    st.plotly_chart(fig_sun, use_container_width=True)
    
    st.markdown("---")

    # --- 3. تحليل تفصيلي لمحتويات الملفات ونسبها (Pivot Analysis & Percentages) ---
    st.markdown("<h2 class='section-header'>📄 تحليل محتويات وأنواع الملفات والنسب مئوية</h2>", unsafe_allow_html=True)
    
    # تجميع متقدم مع حساب النسبة مئوية
    ext_df = df.groupby('extension').agg(
        total_size_mb=('Size (MB)', 'sum'),
        file_count=('name', 'count')
    ).reset_index()
    
    ext_df['percentage'] = (ext_df['total_size_mb'] / total_size_mb) * 100
    ext_df = ext_df.sort_values(by='total_size_mb', ascending=False)
    
    # تنسيق الجدول للعرض
    ext_df.columns = ['نوع الملف', 'إجمالي الحجم (MB)', 'عدد الملفات', 'النسبة مئوية (%)']
    ext_df_formatted = ext_df.copy()
    ext_df_formatted['إجمالي الحجم (MB)'] = ext_df_formatted['إجمالي الحجم (MB)'].map('{:,.2f}'.format)
    ext_df_formatted['عدد الملفات'] = ext_df_formatted['عدد الملفات'].map('{:,}'.format)
    ext_df_formatted['النسبة مئوية (%)'] = ext_df_formatted['النسبة مئوية (%)'].map('{:.1f}%'.format)
    
    st.markdown("#### جدول تحليلي لمحتويات وأنواع الملفات ونسبها:")
    st.dataframe(ext_df_formatted, use_container_width=True, height=400)
    
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("#### رسم بياني دائري: توزيع النسب مئوية للحجم حسب النوع:")
        fig_pie = px.pie(ext_df.head(8), names='نوع الملف', values='إجمالي الحجم (MB)', hole=0.4, title='أكبر 8 أنواع ملفات (نسب مئوية)')
        st.plotly_chart(fig_pie, use_container_width=True)
    with chart_col2:
        st.markdown("#### رسم بياني شريطي: عدد الملفات لكل نوع (أكبر 10):")
        fig_bar_count = px.bar(ext_df.head(10), x='نوع الملف', y='عدد الملفات', title='أكبر 10 أنواع من حيث عدد الملفات', labels={'عدد الملفات': 'عدد الملفات'})
        st.plotly_chart(fig_bar_count, use_container_width=True)

    st.markdown("---")

    # --- 4. خانات تحميل الملفات (Download Section) ---
    st.markdown("<h2 class='section-header'>📥 تحميل تقارير البيانات (Excel / PDF Summary)</h2>", unsafe_allow_html=True)
    
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        st.markdown("<div class='download-section'>", unsafe_allow_html=True)
        st.markdown("#### تحميل البيانات الكاملة (10K) بصيغة Excel")
        st.write("احصل على ملف Excel يحتوي على كافة الصفوف الـ 10,000 والتفاصيل الكاملة.")
        excel_data = to_excel(df)
        st.download_button(label="📥 تحميل ملف Excel", data=excel_data, file_name='dropbox_data_10k.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_dl2:
        st.markdown("<div class='download-section'>", unsafe_allow_html=True)
        st.markdown("#### تحميل ملخص تحليلي سريع (Text Summary)")
        st.write("احصل على ملف نصي يحتوي على أبرز المؤشرات والنسب مئوية (ملخص سريع).")
        pdf_data = to_pdf_summary(df, total_size_gb, top_company, top_ext_size)
        st.download_button(label="📥 تحميل ملخص (Text)", data=pdf_data, file_name='dropbox_summary.txt', mime='text/plain')
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # سيتم عرض رسالة الخطأ من دالة load_data()
    pass

st.markdown("---")
st.caption("تم إنشاء هذه اللوحة الاحترافية ببياناتك الفعلية من ملف 'خريطة ملفات الدروبكس.csv' باستخدام Streamlit, Pandas, & Plotly.")