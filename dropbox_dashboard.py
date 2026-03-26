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
    # اسم ملف البيانات الفعلي الذي قدمته (تأكد من وجوده في نفس مجلد الكود)
    data_file = 'خريطة_ملفات_الدروبكس_المعدلة.csv'
    
    # التأكد من وجود الملف في نفس مجلد الكود
    if not os.path.exists(data_file):
        st.error(f"⚠️ لم يتم العثور على ملف البيانات: '{data_file}'. تأكد من وضعه في نفس مجلد الكود وان اسمه صحيح تماماً.")
        return pd.DataFrame()

    try:
        # قراءة الملف، مع التأكد من ترميز utf-8 للقراءة الحروف العربية
        df = pd.read_csv(data_file, encoding='utf-8') 
        
        # تنظيف البيانات الأساسي: إزالة الصفوف الفارغة بالكامل
        df.dropna(how='all', inplace=True)
        
        # تحويل عمود الحجم إلى ميغابايت (MB) من عمود 'Size (Bytes)' الموجود في ملفك
        if 'Size (Bytes)' in df.columns:
            df['Size (Bytes)'] = pd.to_numeric(df['Size (Bytes)'], errors='coerce').fillna(0)
            df['Size (MB)'] = df['Size (Bytes)'] / (1024 * 1024) # تحويل من بايت لـ MB
            df['Size (GB)'] = df['Size (MB)'] / 1024 # تحويل لـ GB
        else:
             st.warning("تنبيه: لم يتم العثور على عمود 'Size (Bytes)'.")
            
        # --- الإجراء الحاسم: دمج كافة أقسام 'جدير' في ملف واحد ---
        # إنشاء عمود للشركة الرئيسية (الجزء الأول من المسار)
        df['top_folder'] = df['parent_path'].apply(lambda x: str(x).split('/')[0])
        
        # استبدال كافة المسارات التي تبدأ بـ 'Jadeer' لتصبح 'Jadeer' فقط في عمود الشركة الرئيسية
        df.loc[df['top_folder'].str.startswith('Jadeer'), 'top_folder'] = 'Jadeer'
        
        # حساب العمق الهرمي
        df['path_depth'] = df['parent_path'].apply(lambda x: len(str(x).split('/')))

        return df
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
        return pd.DataFrame()

# --- دالة لإنشاء مؤشرات KPIs احترافية وديناميكية (المطورة بـ 8 مؤشرات) ---
def render_kpis(filtered_df, title_prefix="للكل"):
    st.markdown(f"<h3 class='section-header'>📌 مؤشرات أداء رئيسية متقدمة ({title_prefix})</h3>", unsafe_allow_html=True)
    
    # تنسيق بطاقات الـ KPIs داخل صف واحد عريض (8 أعمدة)
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    
    # حساب القيم الأساسية
    num_files = len(filtered_df)
    total_size_mb = filtered_df['Size (MB)'].sum()
    total_size_gb = filtered_df['Size (GB)'].sum()
    avg_size_mb = filtered_df['Size (MB)'].mean()
    
    # النوع الأكثر شيوعاً (حجماً)
    top_ext_size = filtered_df.groupby('extension')['Size (MB)'].sum().idxmax()
    top_ext_size_mb = filtered_df.groupby('extension')['Size (MB)'].sum().max()
    
    # العمق
    max_depth = filtered_df['path_depth'].max()

    # أكبر ملف منفرد
    largest_file = filtered_df.sort_values(by='Size (MB)', ascending=False).iloc[0]

    # عدد الشركات والملفات لكل شركة
    num_companies = len(filtered_df['top_folder'].unique())
    avg_files_per_company = num_files / num_companies if num_companies > 0 else 0

    # عرض الـ KPIs الـ 8 المفصلة والاحترافية
    with col1:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>إجمالي الملفات</div><div class='kpi-value'>{num_files:,}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>إجمالي الحجم (GB)</div><div class='kpi-value'>{total_size_gb:.2f}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>متوسط حجم الملف</div><div class='kpi-value'>{avg_size_mb:.2f}</div><div class='kpi-sub'>MB</div></div>", unsafe_allow_html=True)
    with col4:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>أكبر ملف منفرد</div><div class='kpi-value'>{largest_file['Size (MB)']:.1f}</div><div class='kpi-sub'>{largest_file['name'][:10]}... MB</div></div>", unsafe_allow_html=True)
    with col5:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>النوع المهيمن (حجماً)</div><div class='kpi-value'>.{top_ext_size}</div></div>", unsafe_allow_html=True)
    with col6:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>أكثر المجلدات عمقاً</div><div class='kpi-value'>{max_depth} levels</div></div>", unsafe_allow_html=True)
    with col7:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>الشركات المدمجة</div><div class='kpi-value'>{num_companies}</div></div>", unsafe_allow_html=True)
    with col8:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>متوسط الملفات/شركة</div><div class='kpi-value'>{avg_files_per_company:.1f}</div></div>", unsafe_allow_html=True)

# --- تحميل البيانات (هنا يتم تعريف متغير df) ---
df = load_data()

# --- التحقق من وجود البيانات ---
if not df.empty:
    
    # استخراج كافة المسارات الفرعية العميقة
    all_paths = sorted(list(df['parent_path'].unique()))
    
    # --- 1. قائمة منسدلة ديناميكية للفلترة ---
    st.markdown("<h2 class='section-header'>📂 فلترة البيانات واستكشاف المجلدات الديناميكية</h2>", unsafe_allow_html=True)
    st.write("اختر مجلداً محدداً من القائمة أدناه لتحديث لوحة التحكم بالكامل فوراً:")
    dropdown_options = ["(عرض كامل الـ 10K ملف)"] + sorted(list(df['top_folder'].unique())) + all_paths
    selected_filter = st.selectbox("", dropdown_options, index=0)
    
    st.markdown("---")

    # --- إدارة الـ KPIs الديناميكية (تفاعلية حقيقية ومستقرة) ---
    if selected_filter == "(عرض كامل الـ 10K ملف)":
        render_kpis(df, "للكل - تم دمج 'جدير'")
        current_data = df.copy()
    elif selected_filter in df['top_folder'].unique():
        filtered_df = df[df['top_folder'] == selected_filter].copy()
        render_kpis(filtered_df, f"لشركة: {selected_filter}")
        current_data = filtered_df.copy()
    else:
         filtered_df = df[df['parent_path'].str.startswith(selected_filter)].copy()
         render_kpis(filtered_df, f"للمجلد: {selected_filter}")
         current_data = filtered_df.copy()

    st.markdown("---")

    # --- 2. الرسم البياني الأول: مخطط Sunburst (الهيكل الهرمي) ---
    # هذا هو الرسم الأول من الثمانية
    st.markdown("<h2 class='section-header'>🏢 (1) استكشاف الهيكل الهرمي وتوزيع المساحة (تفاعلي)</h2>", unsafe_allow_html=True)
    
    fig_sun = px.sunburst(current_data, path=['top_folder', 'parent_path'], values='Size (MB)', color='top_folder', hover_data={'Size (MB)': ':.2f'})
    fig_sun.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    st.plotly_chart(fig_sun, use_container_width=True)
    
    st.markdown("---")

    # --- 3. قسم التحليل التفصيلي وإضافة المزيد من الرسومات (الآن المجموع 8) ---
    st.markdown("<h2 class='section-header'>📄 تحليل متقدم لـ 10K ملف (المجموع 8 رسومات بيانية)</h2>", unsafe_allow_html=True)
    
    # تجميع البيانات للرسومات القادمة
    ext_df = current_data.groupby('extension').agg(total_size_mb=('Size (MB)', 'sum'), file_count=('name', 'count')).reset_index()
    
    # --- صف الرسومات الأول (الرسومات 2 و 3 القديمة) ---
    st.markdown("### 📊 توزيع الحجم والعدد حسب نوع الملف")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        # (2) رسم بياني دائري (الحجم MB)
        fig_pie = px.pie(ext_df.head(8), names='نوع الملف', values='إجمالي الحجم (MB)', hole=0.4, title='توزيع حجم المساحة (MB) لأكبر 8 أنواع')
        st.plotly_chart(fig_pie, use_container_width=True)
    with chart_col2:
        # (3) رسم بياني شريطي (عدد الملفات)
        fig_bar_count = px.bar(ext_df.head(10), x='نوع الملف', y='عدد الملفات', title='أكبر 10 أنواع ملفات من حيث العدد')
        st.plotly_chart(fig_bar_count, use_container_width=True)

    # --- صف الرسومات الثاني (الرسومات 4 و 5 الجديدة) ---
    st.markdown("---")
    st.markdown("### 🏢 تحليل أداء الشركات وحجم الملفات")
    chart_col3, chart_col4 = st.columns(2)
    with chart_col3:
        # (4) شريطي أفقي: أكبر 10 شركات حجماً
        company_gb = current_data.groupby('top_folder')['Size (GB)'].sum().reset_index().sort_values(by='Size (GB)', ascending=False).head(10)
        fig_bar_company = px.bar(company_gb, x='Size (GB)', y='top_folder', orientation='h', title='أكبر 10 شركات استهلاكاً للمساحة (GB)', color='Size (GB)', color_continuous_scale='Blues')
        fig_bar_company.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar_company, use_container_width=True)
    with chart_col4:
        # (5) رسم بياني مبعثر (Scatter): عدد الملفات vs الحجم لكل شركة
        company_stats = current_data.groupby('top_folder').agg(num_files=('name', 'count'), total_gb=('Size (GB)', 'sum')).reset_index()
        fig_scatter = px.scatter(company_stats, x='num_files', y='total_gb', text='top_folder', size='total_gb', color='total_gb', title='العلاقة بين عدد الملفات وإجمالي الحجم لكل شركة', labels={'num_files': 'عدد الملفات', 'total_gb': 'إجمالي الحجم (GB)'})
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --- صف الرسومات الثالث (الرسومات 6 و 7 الجديدة) ---
    st.markdown("---")
    st.markdown("### 📦 تحليل توزيع الأنواع الهرمي والعمق")
    chart_col5, chart_col6 = st.columns(2)
    with chart_col5:
        # (6) Tree Map: توزيع الأنواع داخل الشركات
        fig_tree = px.treemap(current_data[current_data['extension'].isin(ext_df.head(5)['extension'])], path=['top_folder', 'extension'], values='Size (MB)', color='top_folder', title='مخطط Tree Map: توزيع أكبر 5 أنواع داخل الشركات')
        st.plotly_chart(fig_tree, use_container_width=True)
    with chart_col6:
        # (7) رسم بياني خطي (Line): الحجم حسب العمق
        depth_gb = current_data.groupby('path_depth')['Size (GB)'].sum().reset_index()
        fig_line = px.line(depth_gb, x='path_depth', y='Size (GB)', title='توزيع إجمالي الحجم (GB) حسب العمق الهرمي للمجلدات', markers=True)
        st.plotly_chart(fig_line, use_container_width=True)

    # --- الرسم الثامن والأخير (جديد) ---
    st.markdown("---")
    st.markdown("### 📄 تحليل مكدس للشركات الكبرى والأصناف")
    # (8) شريطي مكدس (Stacked Bar): توزيع الأنواع لأكبر 5 شركات عدداً
    top_5_cos_by_count = current_data['top_folder'].value_counts().head(5).index
    df_top_cos = current_data[current_data['top_folder'].isin(top_5_cos_by_count)]
    # التركيز على أكبر 3 امتدادات فقط للوضوح
    top_exts = ext_df.head(3)['extension'].tolist()
    df_top_cos_exts = df_top_cos[df_top_cos['extension'].isin(top_exts)]
    
    fig_stacked = px.bar(df_top_cos_exts, x='top_folder', y='Size (GB)', color='extension', title='توزيع أكبر 3 أنواع ملفات (حجماً) داخل أكبر 5 شركات عدداً', labels={'Size (GB)': 'الحجم (GB)', 'top_folder': 'الشركة'})
    st.plotly_chart(fig_stacked, use_container_width=True)

    st.markdown("---")

    # --- 4. خانات تحميل البيانات (Excel Download) ---
    st.markdown("<h2 class='section-header'>📥 تحميل تقارير البيانات (Excel)</h2>", unsafe_allow_html=True)
    st.write("احصل على ملف Excel يحتوي على كافة الصفوف الـ 10,000 والتفاصيل الكاملة.")
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DropboxData')
    processed_data = output.getvalue()
    st.download_button(label="📥 تحميل ملف Excel", data=processed_data, file_name='dropbox_data_10k.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

else:
    pass

st.markdown("---")
st.caption("تم إنشاء هذه اللوحة الاحترافية المطورة ببياناتك الفعلية من ملف 'خريطة ملفات الدروبكس.csv' باستخدام Streamlit, Pandas, & Plotly.")
