import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Dropbox 10K Dynamic Dashboard - الإصلاح", layout="wide")

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
        st.error(f"⚠️ لم يتم العثور على ملف البيانات: '{data_file}'. تأكد من وضعه في نفس مجلد الكود.")
        return pd.DataFrame()

    try:
        # قراءة الملف، مع التأكد من ترميز utf-8 للقراءة الحروف العربية
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
    
    # حساب الشركة الأكثر استهلاكاً (أول جزء من المسار)
    filtered_df['top_folder'] = filtered_df['parent_path'].apply(lambda x: x.split('/')[0])
    top_company = filtered_df.groupby('top_folder')['Size (MB)'].sum().idxmax()
    top_company_size_mb = filtered_df.groupby('top_folder')['Size (MB)'].sum().max()
    # لتجنب خطأ القسمة على صفر إذا كانت البيانات فارغة
    total_mb_all = filtered_df['Size (MB)'].sum()
    if total_mb_all > 0:
        top_company_perc = (top_company_size_mb / total_mb_all) * 100
    else:
        top_company_perc = 0
    
    # النوع الأكثر شيوعاً (حجماً)
    top_ext_size = filtered_df.groupby('extension')['Size (MB)'].sum().idxmax()
    top_ext_size_mb = filtered_df.groupby('extension')['Size (MB)'].sum().max()
    if total_mb_all > 0:
        top_ext_perc = (top_ext_size_mb / total_mb_all) * 100
    else:
        top_ext_perc = 0
    
    # حساب أكثر المجلدات عمقاً
    filtered_df['path_depth'] = filtered_df['parent_path'].apply(lambda x: len(x.split('/')))
    max_depth = filtered_df['path_depth'].max()

    # عرض الـ KPIs الـ 6 المفصلة
    with col1:
        st.markdown(f"<div class='kpi-box'><div class='kpi-title'>إجمالي الملفات</div><div class='kpi-value'>{num_files:,}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='kpi-box'><div class='kpi-title'>إجمالي الحجم (GB)</div><div class='kpi-value'>{total_size_gb:.2f}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='kpi-box'><div class='kpi-title'>متوسط حجم الملف</div><div class='kpi-value'>{avg_size_mb:.2f}</div><div class='kpi-sub'>MB</div></div>", unsafe_allow_html=True)
    with col4:
         st.markdown(f"<div class='kpi-box'><div class='kpi-title'>الشركة الأكثر استهلاكاً</div><div class='kpi-value'>{top_company}</div><div class='kpi-sub'>{top_company_size_mb/1024:.1f} GB ({top_company_perc:.1f}%)</div></div>", unsafe_allow_html=True)
    with col5:
         st.markdown(f"<div class='kpi-box'><div class='kpi-title'>النوع الأكثر شيوعاً (حجماً)</div><div class='kpi-value'>.{top_ext_size}</div><div class='kpi-sub'>{top_ext_size_mb/1024:.1f} GB ({top_ext_perc:.1f}%)</div></div>", unsafe_allow_html=True)
    with col6:
         st.markdown(f"<div class='kpi-box'><div class='kpi-title'>أكثر المجلدات عمقاً</div><div class='kpi-value'>{max_depth}</div><div class='kpi-sub'>مستويات هرمية</div></div>", unsafe_allow_html=True)

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
    
    # --- 1. التحليل الهرمي العميق (Sunburst Chart) - الإصلاح ---
    st.markdown("<h2 class='section-header'>🏢 استكشاف الهيكل الهرمي وتوزيع المساحة (تفاعلي - تم الإصلاح)</h2>", unsafe_allow_html=True)
    st.write("انقر فوق أي جزء لاستكشاف المجلدات الفرعية العميقة وتحديث المؤشرات.")
    
    # أولاً: تجميع البيانات يدوياً لضمان اتساق مخطط Sunburst
    # نقوم بتجميع كافة الملفات حسب parent_path وحساب إجمالي حجمها
    folder_agg_df = df.groupby('parent_path')['Size (MB)'].sum().reset_index()
    
    # ثانياً: استخراج المجلدات الرئيسية والثانوية لبناء الهيكل الهرمي في مخطط Sunburst
    # نحتاج لعمود 'top_folder' (الشركة رئيسية) و عمود 'full_path' (المسار الكامل)
    folder_agg_df['top_folder'] = folder_agg_df['parent_path'].apply(lambda x: x.split('/')[0])
    
    # ثالثاً: رسم مخطط Sunburst بالبيانات المجمعة المتسقة
    fig_sun = px.sunburst(folder_agg_df, 
                         path=['top_folder', 'parent_path'], # المسار الهرمي
                         values='Size (MB)', # الحجم المجمع للقياس
                         color='top_folder', # تلوين حسب الشركة
                         title='انقر فوق أي جزء لاستكشاف المجلدات الفرعية العميقة وتوزيع الحجم',
                         hover_data={'top_folder': True, 'parent_path': True, 'Size (MB)': ':.2f'}) # تفاصيل إضافية عند التمرير
    
    fig_sun.update_layout(margin=dict(t=50, l=25, r=25, b=25)) # إعدادات الهامش
    
    # جعل المخطط تفاعلي مع Streamlit
    sunburst_event = st.plotly_chart(fig_sun, use_container_width=True, on_select="rerun", selection_mode="point")
    
    st.markdown("---")

    # --- 2. إدارة الـ KPIs الديناميكية (تفاعلية) ---
    # تحديد البيانات التي تم اختيارها من مخطط Sunburst
    selected_points = sunburst_event.get("selection", {}).get("points", [])
    
    if selected_points:
        # استخراج المسار الذي تم النقر عليه (مثلاً ["Jadeer"])
        clicked_path_str = selected_points[0].get("id", "")
        clicked_path = clicked_path_str.split('/')
        
        # فلترة البيانات بناءً على المسار
        if len(clicked_path) == 1:
            # النقر على الشركة الرئيسية
            df['top_folder'] = df['parent_path'].apply(lambda x: x.split('/')[0])
            filtered_df = df[df['top_folder'] == clicked_path[0]].copy()
            render_kpis(filtered_df, len(df), f"لشركة: {clicked_path[0]}")
        else:
             # النقر على مجلد فرعي عميق
             full_path_str = clicked_path_str # مثل "Jadeer/مشاريع"
             filtered_df = df[df['parent_path'].str.startswith(full_path_str)].copy()
             render_kpis(filtered_df, len(df), f"للمجلد: {full_path_str}")
             
    else:
        # عرض الـ KPIs الافتراضية لكافة الملفات (10K)
        render_kpis(df, len(df), "للكل")

    st.markdown("---")

    # --- 3. تحليل تفصيلي لمحتويات الملفات ونسبها (Pivot Analysis & Percentages) ---
    st.markdown("<h2 class='section-header'>📄 تحليل محتويات وأنواع الملفات والنسب مئوية</h2>", unsafe_allow_html=True)
    
    # تجميع البيانات بشكل متقدم (Pivot-like aggregation) وحساب النسب
    ext_analysis_df = df.groupby('extension').agg(
        total_size_mb=('Size (MB)', 'sum'),
        file_count=('name', 'count')
    ).reset_index()
    
    # حساب النسب مئوية للحجم (مع التأكد من القسمة على صفر)
    total_size_mb_all = df['Size (MB)'].sum()
    if total_size_mb_all > 0:
        ext_analysis_df['percentage'] = (ext_analysis_df['total_size_mb'] / total_size_mb_all) * 100
    else:
        ext_analysis_df['percentage'] = 0
        
    ext_analysis_df.columns = ['نوع الملف', 'إجمالي الحجم (MB)', 'عدد الملفات', 'النسبة مئوية (%)']
    
    # ترتيب من الأكبر حجماً للأصغر
    ext_analysis_df = ext_analysis_df.sort_values(by='إجمالي الحجم (MB)', ascending=False)
    
    # تنسيق الجدول للعرض
    ext_analysis_df_formatted = ext_analysis_df.copy()
    ext_analysis_df_formatted['إجمالي الحجم (MB)'] = ext_analysis_df_formatted['إجمالي الحجم (MB)'].map('{:,.2f}'.format)
    ext_analysis_df_formatted['عدد الملفات'] = ext_analysis_df_formatted['عدد الملفات'].map('{:,}'.format)
    ext_analysis_df_formatted['النسبة مئوية (%)'] = ext_analysis_df_formatted['النسبة مئوية (%)'].map('{:.1f}%'.format)
    
    st.markdown("#### جدول تحليلي لمحتويات وأنواع الملفات ونسبها:")
    st.dataframe(ext_analysis_df_formatted, use_container_width=True, height=400)
    
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("#### رسم بياني دائري: توزيع النسب مئوية للحجم حسب النوع:")
        fig_pie = px.pie(ext_analysis_df.head(8), names='نوع الملف', values='إجمالي الحجم (MB)', hole=0.4, title='أكبر 8 أنواع ملفات (نسب مئوية)')
        st.plotly_chart(fig_pie, use_container_width=True)
    with chart_col2:
        st.markdown("#### رسم بياني شريطي: عدد الملفات لكل نوع (أكبر 10):")
        fig_bar_count = px.bar(ext_analysis_df.head(10), x='نوع الملف', y='عدد الملفات', title='أكبر 10 أنواع من حيث عدد الملفات', labels={'عدد الملفات': 'عدد الملفات'})
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
st.caption("تم إنشاء هذه اللوحة الاحترافية ببياناتك الفعلية من ملف 'خريطة ملفات الدروبكس.csv' باستخدام Streamlit, Pandas, & Plotly.")
