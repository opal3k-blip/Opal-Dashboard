import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Dropbox 10K Dynamic Pro Dashboard", layout="wide")

# --- تنسيق مخصص (CSS) لتحسين المظهر وجعل اللوحة احترافية جداً ---
st.markdown("""
<style>
    /* تنسيق الحاوية الرئيسية للمؤشرات */
    .kpi-container {
        background-color: #f9f9f9;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
    }
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
    # اسم ملف البيانات الفعلي الذي قدمته
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
        else:
             st.warning("تنبيه: لم يتم العثور على عمود 'Size (Bytes)'.")
            
        # --- الإجراء الحاسم: دمج كافة أقسام 'جدير' في ملف واحد ---
        df['top_folder'] = df['parent_path'].apply(lambda x: x.split('/')[0])
        df.loc[df['top_folder'].str.startswith('Jadeer'), 'top_folder'] = 'Jadeer'
        
        return df
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
        return pd.DataFrame()

# --- دالة لإنشاء مؤشرات KPIs احترافية وديناميكية (المطورة) ---
def render_kpis(filtered_df, total_files_all, title_prefix="للكل"):
    st.markdown(f"<h3 class='section-header'>📌 مؤشرات أداء رئيسية متقدمة ({title_prefix})</h3>", unsafe_allow_html=True)
    
    # تنسيق بطاقات الـ KPIs داخل حاوية مخصصة (9 أعمدة)
    col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns(9)
    
    # حساب القيم الأساسية
    num_files = len(filtered_df)
    total_size_mb = filtered_df['Size (MB)'].sum()
    total_size_gb = filtered_df['Size (GB)'].sum()
    avg_size_mb = filtered_df['Size (MB)'].mean()
    
    # النوع الأكثر شيوعاً (حجماً)
    top_ext_size = filtered_df.groupby('extension')['Size (MB)'].sum().idxmax()
    top_ext_size_mb = filtered_df.groupby('extension')['Size (MB)'].sum().max()
    
    # حساب أكثر المجلدات عمقاً
    filtered_df['path_depth'] = filtered_df['parent_path'].apply(lambda x: len(x.split('/')))
    max_depth = filtered_df['path_depth'].max()

    # أكبر ملف منفرد
    largest_file = filtered_df.sort_values(by='Size (MB)', ascending=False).iloc[0]

    # عدد الشركات الرئيسية المدمجة
    unique_companies = filtered_df['top_folder'].unique()
    num_companies = len(unique_companies)

    # حساب مؤشرات إضافية
    total_mb_all = filtered_df['Size (MB)'].sum()
    avg_files_per_company = num_files / num_companies if num_companies > 0 else 0
    num_extensions = len(filtered_df['extension'].unique())

    # عرض الـ KPIs الـ 9 المفصلة
    with col1:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>إجمالي الملفات</div><div class='kpi-value'>{num_files:,}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>إجمالي الحجم</div><div class='kpi-value'>{total_size_gb:.2f}</div><div class='kpi-sub'>GB</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>متوسط حجم الملف</div><div class='kpi-value'>{avg_size_mb:.2f}</div><div class='kpi-sub'>MB</div></div>", unsafe_allow_html=True)
    with col4:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>أكبر ملف منفرد</div><div class='kpi-value'>{largest_file['Size (MB)']:.1f}</div><div class='kpi-sub'>{largest_file['name'][:10]}... MB</div></div>", unsafe_allow_html=True)
    with col5:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>النوع المهيمن</div><div class='kpi-value'>.{top_ext_size}</div><div class='kpi-sub'>{top_ext_size_mb/1024:.1f} GB</div></div>", unsafe_allow_html=True)
    with col6:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>أكثر المجلدات عمقاً</div><div class='kpi-value'>{max_depth}</div><div class='kpi-sub'>مستويات</div></div>", unsafe_allow_html=True)
    with col7:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>الشركات الرئيسية</div><div class='kpi-value'>{num_companies}</div><div class='kpi-sub'>شركات مدمجة</div></div>", unsafe_allow_html=True)
    with col8:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>متوسط الملفات/شركة</div><div class='kpi-value'>{avg_files_per_company:.1f}</div><div class='kpi-sub'>ملف/شركة</div></div>", unsafe_allow_html=True)
    with col9:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>تنوع الملفات</div><div class='kpi-value'>{num_extensions}</div><div class='kpi-sub'>امتداد مختلف</div></div>", unsafe_allow_html=True)

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

    # --- إدارة الـ KPIs الديناميكية بناءً على الفلتر ---
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

    # --- 2. التحليل الهرمي والمساحي المطور ---
    st.markdown("<h2 class='section-header'>🏢 استكشاف الهيكل الهرمي وتوزيع المساحة (تفاعلي)</h2>", unsafe_allow_html=True)
    st.write("انقر فوق أي جزء لاستكشاف المجلدات الفرعية العميقة وتوزيع الحجم.")
    
    fig_sun = px.sunburst(current_data, path=['top_folder', 'parent_path'], values='Size (MB)', color='top_folder', hover_data={'top_folder': True, 'parent_path': True, 'Size (MB)': ':.2f'})
    fig_sun.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    st.plotly_chart(fig_sun, use_container_width=True)
    
    st.markdown("---")

    # --- 3. تحليل تفصيلي لمحتويات الملفات والشركات (القسم الجديد المطور) ---
    st.markdown("<h2 class='section-header'>📄 تحليل تفصيلي لمحتويات الملفات وأداء الشركات</h2>", unsafe_allow_html=True)
    
    # تجميع البيانات وحساب النسب (للجدول)
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
    st.dataframe(ext_formatted, use_container_width=True, height=300)
    
    # --- قسم الصور البيانية الجديد ---
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # 1. رسم بياني دائري (Pie Chart) للنسب مئوية للحجم
        st.markdown("#### رسم بياني دائري: توزيع النسب مئوية للحجم حسب النوع:")
        fig_pie = px.pie(ext_df.head(8), names='نوع الملف', values='إجمالي الحجم (MB)', hole=0.4, title='أكبر 8 أنواع ملفات (نسب مئوية)')
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # 3. رسم بياني مبعثر (Scatter Plot) - جديد - العلاقة بين عدد الملفات والحجم لكل شركة
        st.markdown("#### رسم بياني مبعثر: العلاقة بين عدد الملفات وإجمالي الحجم لكل شركة:")
        company_stats = current_data.groupby('top_folder').agg(num_files=('name', 'count'), total_gb=('Size (GB)', 'sum')).reset_index()
        fig_scatter = px.scatter(company_stats, x='num_files', y='total_gb', text='top_folder', size='total_gb', color='total_gb', title='كثافة الملفات vs الحجم لكل شركة', labels={'num_files': 'عدد الملفات', 'total_gb': 'إجمالي الحجم (GB)'})
        fig_scatter.update_traces(textposition='top center')
        st.plotly_chart(fig_scatter, use_container_width=True)

    with chart_col2:
        # 2. رسم بياني شريطي (Bar Chart) لعدد الملفات
        st.markdown("#### رسم بياني شريطي: عدد الملفات لكل نوع (أكبر 10):")
        fig_bar_count = px.bar(ext_df.head(10), x='نوع الملف', y='عدد الملفات', title='أكبر 10 أنواع من حيث عدد الملفات', labels={'عدد الملفات': 'عدد الملفات'})
        st.plotly_chart(fig_bar_count, use_container_width=True)
        
        # 4. مخطط شريطي أفقي (Horizontal Bar Chart) - جديد - أكبر 10 شركات حجماً
        st.markdown("#### مخطط شريطي أفقي: أكبر 10 شركات استهلاكاً للمساحة:")
        company_gb = current_data.groupby('top_folder')['Size (GB)'].sum().reset_index().sort_values(by='Size (GB)', ascending=False).head(10)
        fig_bar_company = px.bar(company_gb, x='Size (GB)', y='top_folder', orientation='h', title='أكبر 10 شركات حجماً (GB)', labels={'Size (GB)': 'الحجم (GB)', 'top_folder': 'الشركة'}, color='Size (GB)', color_continuous_scale='Blues')
        fig_bar_company.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar_company, use_container_width=True)

    st.markdown("---")

    # --- 4. خانات تحميل البيانات (Excel Download) ---
    st.markdown("<h2 class='section-header'>📥 تحميل تقارير البيانات (Excel)</h2>", unsafe_allow_html=True)
    st.write("احصل على ملف Excel يحتوي على كافة الصفوف الـ 10,000 والتفاصيل الكاملة.")
    
    excel_data = to_excel(df)
    st.download_button(label="📥 تحميل ملف Excel", data=excel_data, file_name='dropbox_data_10k.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

else:
    # سيتم عرض رسالة الخطأ من دالة load_data()
    pass

st.markdown("---")
st.caption("تم إنشاء هذه اللوحة الاحترافية المطور جداً ببياناتك الفعلية من ملف 'خريطة ملفات الدروبكس.csv' باستخدام Streamlit, Pandas, & Plotly.")
