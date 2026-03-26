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
        st.error(f"⚠️ لم يتم العثور على ملف البيانات: '{data_file}'. تأكد من وضعه في نفس مجلد الكود.")
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
        df['top_folder'] = df['parent_path'].apply(lambda x: x.split('/')[0])
        
        # استبدال كافة المسارات التي تبدأ بـ 'Jadeer' لتصبح 'Jadeer' فقط في عمود الشركة الرئيسية
        df.loc[df['top_folder'].str.startswith('Jadeer'), 'top_folder'] = 'Jadeer'
        
        return df
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
        return pd.DataFrame()

# --- دالة لإنشاء مؤشرات KPIs احترافية وديناميكية (المطورة بـ 8 مؤشرات) ---
def render_kpis(filtered_df, total_files, title_prefix="للكل"):
    st.markdown(f"<h3 class='section-header'>📌 مؤشرات أداء رئيسية متقدمة لـ 10K ملف ({title_prefix})</h3>", unsafe_allow_html=True)
    
    # تنسيق بطاقات الـ KPIs داخل صف واحد عريض (8 أعمدة)
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    
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

    # عدد الشركات الرئيسية المدمجة
    unique_companies = filtered_df['top_folder'].unique()
    num_companies = len(unique_companies)

    # متوسط عدد الملفات لكل شركة
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
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>النوع المهيمن (حجماً)</div><div class='kpi-value'>.{top_ext_size}</div><div class='kpi-sub'>{top_ext_size_mb/1024:.1f} GB ({top_ext_perc:.1f}%)</div></div>", unsafe_allow_html=True)
    with col6:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>أكثر المجلدات عمقاً</div><div class='kpi-value'>{max_depth} levels</div></div>", unsafe_allow_html=True)
    with col7:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>الشركات الرئيسية المدمجة</div><div class='kpi-value'>{num_companies}</div></div>", unsafe_allow_html=True)
    with col8:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>متوسط الملفات/شركة</div><div class='kpi-value'>{avg_files_per_company:.1f}</div></div>", unsafe_allow_html=True)

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
    st.write("انقر فوق أي جزء لاستكشاف المجلدات الفرعية العميقة وتوزيع الحجم.")
    
    # Sunburst Chart بالبيانات المجمعة المتسقة (تم إلغاء on_select لتجنب APIError)
    fig_sun = px.sunburst(current_data, # يعمل على البيانات المفلترة حالياً
                         path=['top_folder', 'parent_path'], # المسار الهرمي
                         values='Size (MB)', # الحجم للقياس
                         color='top_folder', # تلوين حسب الشركة المدمجة
                         hover_data={'top_folder': True, 'parent_path': True, 'Size (MB)': ':.2f'}) # تفاصيل إضافية عند التمرير
    
    fig_sun.update_layout(margin=dict(t=50, l=25, r=25, b=25)) # إعدادات الهامش
    st.plotly_chart(fig_sun, use_container_width=True) # عرض بدون ميزة Rerun التفاعلية المباشرة
    
    st.markdown("---")

    # --- 3. تحليل تفصيلي لمحتويات الملفات ونسبها (Pivot Analysis & Percentages) ---
    st.markdown("<h2 class='section-header'>📄 تحليل محتويات وأنواع الملفات وحجومها والنسب مئوية</h2>", unsafe_allow_html=True)
    
    # تجميع البيانات وحساب النسب (يعمل على البيانات المفلترة حالياً)
    ext_df = current_data.groupby('extension').agg(
        total_size_mb=('Size (MB)', 'sum'),
        file_count=('name', 'count')
    ).reset_index()
    
    # حساب النسب مئوية للحجم (مع التأكد من القسمة على صفر)
    total_size_mb_all_for_filter = current_data['Size (MB)'].sum()
    if total_size_mb_all_for_filter > 0:
        ext_df['percentage'] = (ext_df['total_size_mb'] / total_size_mb_all_for_filter) * 100
    else:
        ext_df['percentage'] = 0
        
    ext_df.columns = ['نوع الملف', 'إجمالي الحجم (MB)', 'عدد الملفات', 'النسبة مئوية (%)']
    
    # ترتيب من الأكبر حجماً للأصغر
    ext_df = ext_df.sort_values(by='إجمالي الحجم (MB)', ascending=False)
    
    # تنسيق الجدول للعرض
    ext_formatted = ext_df.copy()
    ext_formatted['إجمالي الحجم (MB)'] = ext_formatted['إجمالي الحجم (MB)'].map('{:,.2f}'.format)
    ext_formatted['عدد الملفات'] = ext_formatted['عدد الملفات'].map('{:,}'.format)
    ext_formatted['النسبة مئوية (%)'] = ext_formatted['النسبة مئوية (%)'].map('{:.1f}%'.format)
    
    # عرض الجدول التحليلي المتقدم
    st.markdown("#### جدول تحليلي لمحتويات وأنواع الملفات وحجومها ونسبها:")
    st.dataframe(ext_formatted, use_container_width=True, height=400)
    
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        # رسم بياني دائري (Pie Chart) للنسب مئوية للحجم
        st.markdown("#### رسم بياني دائري: توزيع النسب مئوية للحجم حسب النوع:")
        fig_pie = px.pie(ext_df.head(8), names='نوع الملف', values='إجمالي الحجم (MB)', hole=0.4, title='أكبر 8 أنواع ملفات (نسب مئوية)')
        st.plotly_chart(fig_pie, use_container_width=True)
    with chart_col2:
        # رسم بياني شريطي (Bar Chart) لعدد الملفات
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
    # سيتم عرض رسالة الخطأ من دالة load_data()
    pass

st.markdown("---")
st.caption("تم إنشاء هذه اللوحة الاحترافية جداً ببياناتك الفعلية من ملف 'خريطة ملفات الدروبكس.csv' باستخدام Streamlit, Pandas, & Plotly.")
