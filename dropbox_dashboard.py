import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io

# --- 1. محاولة استيراد مكتبات PDF (مهم جداً) ---
# لإنشاء ملفات PDF على خادم Streamlit Cloud، نحتاج لمكتبة ReportLab.
# إذا لم يتم تثبيتها عبر ملف requirements.txt، سيعمل التطبيق بدونه ولكن لن يظهر زر تحميل PDF.
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    PDF_ENABLED = True
except ModuleNotFoundError:
    # في حال لم يتم تثبيت المكتبة، نقوم بإيقاف ميزة PDF لتجنب توقف التطبيق
    PDF_ENABLED = False

# --- 2. إعدادات الصفحة والتنسيق ---
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

# --- دالة لتحميل وتنظيف البيانات (مع دمج 'جدير' وطريقة مضمونة) ---
@st.cache_data
def load_data():
    # اسم ملف البيانات الفعلي الذي قدمته (يجب أن يكون في نفس مجلد الكود)
    data_file = 'خريطة_ملفات_الدروبكس_المعدلة.csv'
    
    # التأكد من وجود الملف في نفس مجلد الكود
    if not os.path.exists(data_file):
        st.error(f"⚠️ لم يتم العثور على ملف البيانات: '{data_file}'. تأكد من وضعه في نفس مجلد الكود.")
        return pd.DataFrame()

    try:
        # قراءة البيانات الخام بطريقة utf-8 لقراءة الحروف العربية
        df = pd.read_csv(data_file, encoding='utf-8') 
        df.dropna(how='all', inplace=True) # إزالة الصفوف الفارغة بالكامل
        
        # تحويل عمود الحجم إلى ميغابايت (MB) وجيجابايت (GB) من عمود 'Size (Bytes)' الموجود في ملفك
        if 'Size (Bytes)' in df.columns:
            df['Size (Bytes)'] = pd.to_numeric(df['Size (Bytes)'], errors='coerce').fillna(0)
            df['Size (MB)'] = df['Size (Bytes)'] / (1024 * 1024)
            df['Size (GB)'] = df['Size (MB)'] / 1024
        else:
             st.warning("تنبيه: لم يتم العثور على عمود 'Size (Bytes)'.")
            
        # --- الإجراء الحاسم: دمج كافة أقسام 'جدير' في ملف واحد ---
        # إنشاء عمود للشركة الرئيسية (الجزء الأول من المسار)
        df['top_folder'] = df['parent_path'].apply(lambda x: str(x).split('/')[0])
        df.loc[df['top_folder'].str.startswith('Jadeer'), 'top_folder'] = 'Jadeer'
        
        # حساب العمق الهرمي للمجلدات
        df['path_depth_lvl'] = df['parent_path'].apply(lambda x: len(str(x).split('/')))
        
        return df
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف أو تحليله: {e}")
        return pd.DataFrame()

# --- دالة لإنشاء مؤشرات KPIs احترافية وديناميكية ومضمونة التشغيل (12 مؤشر) ---
def render_kpis(filtered_df, total_files_all, title_prefix="للكل"):
    st.markdown(f"<h3 class='section-header'>📌 مؤشرات أداء رئيسية متقدمة لـ 10K ملف الحقيقيين ({title_prefix})</h3>", unsafe_allow_html=True)
    
    # تنسيق الـ KPIs الـ 12 في صفين (6 مؤشرات في كل صف)
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    # حساب القيم الأساسية للصف الأول (6 مؤشرات أساسية)
    num_total_files = len(filtered_df)
    total_size_gb_all = filtered_df['Size (GB)'].sum()
    
    # الشركة الأكثر استهلاكاً
    top_consumption_company = filtered_df.groupby('top_folder')['Size (MB)'].sum().idxmax()
    top_consumption_size_gb = filtered_df.groupby('top_folder')['Size (GB)'].sum().max()
    
    # أكبر ملف منفرد
    largest_file_info = filtered_df.sort_values(by='Size (MB)', ascending=False).iloc[0]

    # النوع المهيمن (حجماً)
    top_ext_by_size = filtered_df.groupby('extension')['Size (MB)'].sum().idxmax()
    top_ext_size_gb = filtered_df.groupby('extension')['Size (GB)'].sum().max()
    total_size_mb_all = filtered_df['Size (MB)'].sum()
    top_ext_percentage = (top_ext_size_gb * 1024 / total_size_mb_all) * 100 if total_size_mb_all > 0 else 0

    # عدد الشركات الرئيسية المدمجة
    num_unique_companies = len(filtered_df['top_folder'].unique())

    # عرض الصف الأول
    with col1:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>إجمالي الملفات</div><div class='kpi-value'>{num_total_files:,}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>إجمالي الحجم (GB)</div><div class='kpi-value'>{total_size_gb_all:.2f}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>الشركة الأكثر استهلاكاً</div><div class='kpi-value'>{top_consumption_company}</div><div class='kpi-sub'>{top_consumption_size_gb:.1f} GB</div></div>", unsafe_allow_html=True)
    with col4:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>أكبر ملف منفرد</div><div class='kpi-value'>{largest_file_info['Size (MB)']:.1f}</div><div class='kpi-sub'>{largest_file_info['name'][:10]}... MB</div></div>", unsafe_allow_html=True)
    with col5:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>النوع المهيمن (حجماً)</div><div class='kpi-value'>.{top_ext_by_size}</div><div class='kpi-sub'>{top_ext_size_gb:.1f} GB ({top_ext_percentage:.1f}%)</div></div>", unsafe_allow_html=True)
    with col6:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>عدد الشركات الرئيسية</div><div class='kpi-value'>{num_unique_companies}</div><div class='kpi-sub'>شركات مدمجة</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True) # فاصلاً صغيراً

    # حساب القيم الأساسية للصف الثاني (6 مؤشرات تحليلية متقدمة)
    col7, col8, col9, col10, col11, col12 = st.columns(6)

    # متوسط حجم الملف (MB)
    avg_size_mb_all = filtered_df['Size (MB)'].mean()
    # متوسط عدد الملفات لكل شركة
    avg_files_per_company_num = num_total_files / num_unique_companies if num_unique_companies > 0 else 0
    # أكثر المجلدات عمقاً
    # حساب المسار الهرمي للوضوح
    filtered_df['path_depth_lvl'] = filtered_df['parent_path'].apply(lambda x: len(str(x).split('/')))
    max_h_depth = filtered_df['path_depth_lvl'].max()
    # عدد الامتدادات المختلفة
    num_unique_extensions = len(filtered_df['extension'].unique())
    # نسبة دمج 'جدير'
    jadeer_total_size_gb_val = filtered_df[filtered_df['top_folder'] == 'Jadeer']['Size (GB)'].sum()
    jadeer_percentage_val = (jadeer_total_size_gb_val / total_size_gb_all) * 100 if total_size_gb_all > 0 else 0
    # متوسط الحجم لكل شركة (GB)
    avg_size_per_company_gb = total_size_gb_all / num_unique_companies if num_unique_companies > 0 else 0

    # عرض الصف الثاني
    with col7:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>متوسط حجم الملف</div><div class='kpi-value'>{avg_size_mb_all:.2f}</div><div class='kpi-sub'>MB</div></div>", unsafe_allow_html=True)
    with col8:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>متوسط الملفات/شركة</div><div class='kpi-value'>{avg_files_per_company_num:.1f}</div><div class='kpi-sub'>ملف لكل شركة</div></div>", unsafe_allow_html=True)
    with col9:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>أكثر المجلدات عمقاً</div><div class='kpi-value'>{max_h_depth} levels</div></div>", unsafe_allow_html=True)
    with col10:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>تنوع الملفات (امتدادات)</div><div class='kpi-value'>{num_unique_extensions}</div></div>", unsafe_allow_html=True)
    with col11:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>نسبة دمج 'جدير'</div><div class='kpi-value'>{jadeer_percentage_val:.1f}%</div><div class='kpi-sub'>{jadeer_total_size_gb_val:.1f} GB</div></div>", unsafe_allow_html=True)
    with col12:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>متوسط الحجم/شركة</div><div class='kpi-value'>{avg_size_per_company_gb:.1f}</div><div class='kpi-sub'>GB لكل شركة</div></div>", unsafe_allow_html=True)

    # إرجاع المؤشرات لاستخدامها في تقرير الـ PDF
    return {
        "إجمالي الملفات": f"{num_total_files:,}",
        "إجمالي الحجم (GB)": f"{total_size_gb_all:.2f}",
        "الشركة الأكثر استهلاكاً": f"{top_consumption_company} ({top_consumption_size_gb:.1f} GB)",
        "أكبر ملف منفرد": f"{largest_file_info['Size (MB)']:.1f} MB",
        "النوع المهيمن (حجماً)": f".{top_ext_by_size} ({top_ext_size_gb:.1f} GB)",
        "عدد الشركات الرئيسية": f"{num_unique_companies}",
        "متوسط حجم الملف (MB)": f"{avg_size_mb_all:.2f}",
        "متوسط الملفات/شركة": f"{avg_files_per_company_num:.1f}",
        "أكثر المجلدات عمقاً": f"{max_h_depth} levels",
        "تنوع الملفات (امتدادات)": f"{num_unique_extensions}",
        "نسبة دمج 'جدير'": f"{jadeer_percentage_val:.1f}%",
        "متوسط الحجم/شركة (GB)": f"{avg_size_per_company_gb:.1f}"
    }

# --- دالة لإنشاء ملف Excel للتحميل (موجودة سابقاً) ---
def to_excel(df):
    output = io.BytesIO()
    # استخدام محرك xlsxwriter لدعم التنسيق المتقدم
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DropboxData')
    processed_excel = output.getvalue()
    return processed_excel

# --- دالة لإنشاء ملف PDF ملخص لصف المؤشرات (جديد) ---
def create_pdf_summary_pro(kpi_data, title_prefix):
    # لا نقوم بإنشاء PDF إلا إذا كانت المكتبة مثبتة
    if not PDF_ENABLED:
        return None
        
    output = io.BytesIO()
    # إنشاء مستند PDF أنيق
    doc = SimpleDocTemplate(output, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # تعريف تنسيقات مخصصة للحروف العربية (تحتاج لمكتبات إضافية، لذا سنبقي النص إنجليزي لضمان التشغيل)
    story = []
    
    # العنوان الرئيسي
    title_style = ParagraphStyle(name='TitleStyle', parent=styles['Title'], fontSize=18, spaceAfter=20)
    title_text = f"Dropbox 10K Files Summary Report ({title_prefix})"
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 12))
    
    # إنشاء جدول للمؤشرات الـ 12
    # سنقوم بترجمة المفاتيح للإنجليزية لضمان ظهورها في PDF بدون مكتبات خطوط إضافية
    translations = {
        "إجمالي الملفات": "Total Files",
        "إجمالي الحجم (GB)": "Total Size (GB)",
        "الشركة الأكثر استهلاكاً": "Top Company (Consumption)",
        "أكبر ملف منفرد": "Largest Single File",
        "النوع المهيمن (حجماً)": "Dominant Type (by Size)",
        "عدد الشركات الرئيسية": "No. of Main Companies",
        "متوسط حجم الملف (MB)": "Avg. File Size (MB)",
        "متوسط الملفات/شركة": "Avg. Files per Company",
        "أكثر المجلدات عمقاً": "Max. Folder Depth",
        "تنوع الملفات (امتدادات)": "File Type Diversity",
        "نسبة دمج 'جدير'": "'Jadeer' Merge Percentage",
        "متوسط الحجم/شركة (GB)": "Avg. Size per Company (GB)"
    }
    
    data = [["KPI Metric", "Value"]] # عنوان الجدول
    for key, value in kpi_data.items():
        data.append([translations[key], value])
        
    # تنسيق الجدول
    table = Table(data, colWidths=[250, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(table)
    
    # إنشاء الـ PDF
    doc.build(story)
    pdf_out = output.getvalue()
    return pdf_out

# --- تحميل البيانات (هنا يتم تعريف متغير df) ---
# نقوم بوضع تحميل البيانات خارج st.empty() لضمان التنفيذ أولاً
main_df = load_data()

# --- التحقق من نجاح تحميل البيانات ---
# إذا كانت البيانات فارغة، فهذا يعني أن دالة تحميل البيانات فشلت وطبعت رسالة الخطأ الخاصة بها.
if main_df.empty:
    st.warning("⚠️ لا يمكن تحميل لوحة التحكم لعدم توفر البيانات. يرجى مراجعة رسالة الخطأ أعلاه.")
else:
    # --- استخلاص كافة المسارات الفرعية العميقة ---
    all_parent_paths_list = sorted(list(main_df['parent_path'].unique()))
    
    # --- 1. قائمة منسدلة ديناميكية للفلترة ---
    st.markdown("<h2 class='section-header'>📂 فلترة البيانات واستكشاف المجلدات الديناميكية</h2>", unsafe_allow_html=True)
    st.write("اختر مجلداً محدداً من القائمة أدناه لتحديث لوحة التحكم بالكامل فوراً:")
    
    # إنشاء القائمة: الكل + الشركات الرئيسية المدمجة + المجلدات الفرعية العميقة
    dropdown_filter_options = ["(عرض كامل الـ 10,000 ملف الحقيقيين)"] + sorted(list(main_df['top_folder'].unique())) + all_parent_paths_list
    selected_filter_val = st.selectbox("", dropdown_filter_options, index=0)
    
    st.markdown("---")

    # متغرات لتخزين البيانات الحالية لصف الـ PDFs
    current_kpi_values = {}
    current_title_prefix = ""

    # --- 2. إدارة الـ KPIs الديناميكية بناءً على الفلتر (12 مؤشر) ---
    if selected_filter_val == "(عرض كامل الـ 10,000 ملف الحقيقيين)":
        current_title_prefix = "All Files"
        current_kpi_values = render_kpis(main_df, len(main_df), "للكل الحقيقيين - تم دمج 'جدير'")
        current_data_view = main_df.copy()
    elif selected_filter_val in main_df['top_folder'].unique():
        # النقر على الشركة الرئيسية المدمجة
        current_title_prefix = f"Company: {selected_filter_val}"
        filtered_view_df = main_df[main_df['top_folder'] == selected_filter_val].copy()
        current_kpi_values = render_kpis(filtered_view_df, len(main_df), f"لشركة: {selected_filter_val}")
        current_data_view = filtered_view_df.copy()
    else:
         # النقر على مجلد فرعي عميق
         current_title_prefix = f"Folder: {selected_filter_val}"
         filtered_view_df = main_df[main_df['parent_path'].str.startswith(str(selected_filter_val))].copy()
         current_kpi_values = render_kpis(filtered_view_df, len(main_df), f"للمجلد: {selected_filter_val}")
         current_data_view = filtered_view_df.copy()

    st.markdown("---")

    # --- 3. التحليل الهرمي العميق (Sunburst Chart) - تفاعلي وآمن ---
    st.markdown("<h2 class='section-header'>🏢 استكشاف الهيكل الهرمي وتوزيع المساحة (تفاعلي وآمن)</h2>", unsafe_allow_html=True)
    st.write("انقر فوق أي جزء لاستكشاف المجلدات الفرعية العميقة وتوزيع الحجم.")
    
    # Sunburst Chart بالبيانات المجمعة المتسقة والحقيقية
    fig_sun = px.sunburst(current_data_view, # يعمل على البيانات المفلترة حالياً
                         path=['top_folder', 'parent_path'], # المسار الهرمي العميق
                         values='Size (MB)', # الحجم للقياس
                         color='top_folder', # تلوين حسب الشركة المدمجة
                         hover_data={'top_folder': True, 'parent_path': True, 'Size (MB)': ':.2f'}) # تفاصيل إضافية عند التمرير
    
    fig_sun.update_layout(margin=dict(t=50, l=25, r=25, b=25)) # إعدادات الهامش
    st.plotly_chart(fig_sun, use_container_width=True) # عرض بدون ميزة Rerun التفاعلية المباشرة لتجنب APIError
    
    st.markdown("---")

    # --- 4. تحليل تفصيلي لمحتويات الملفات ونسبها (Pivot Analysis & Percentages) ---
    st.markdown("<h2 class='section-header'>📄 تحليل محتويات وأنواع الملفات والحجوم والنسب مئوية</h2>", unsafe_allow_html=True)
    
    # تجميع البيانات وحساب النسب بدقة (يعمل على البيانات المفلترة حالياً)
    ext_analysis_df = current_data_view.groupby('extension').agg(
        total_size_mb=('Size (MB)', 'sum'),
        file_count=('name', 'count')
    ).reset_index()
    
    # حساب النسب مئوية للحجم الإجمالي الحقيقي (مع التأكد من القسمة على صفر)
    total_mb_for_percentage = current_data_view['Size (MB)'].sum()
    if total_mb_for_percentage > 0:
        ext_analysis_df['percentage'] = (ext_analysis_df['total_size_mb'] / total_mb_for_percentage) * 100
    else:
        ext_analysis_df['percentage'] = 0
        
    ext_analysis_df.columns = ['نوع الملف', 'إجمالي الحجم (MB)', 'عدد الملفات', 'النسبة مئوية (%)']
    ext_analysis_df = ext_analysis_df.sort_values(by='إجمالي الحجم (MB)', ascending=False)
    
    # تنسيق الجدول للعرض بشكل احترافي
    ext_formatted_view = ext_analysis_df.copy()
    ext_formatted_view['إجمالي الحجم (MB)'] = ext_formatted_view['إجمالي الحجم (MB)'].map('{:,.2f}'.format)
    ext_formatted_view['عدد الملفات'] = ext_formatted_view['عدد الملفات'].map('{:,}'.format)
    ext_formatted_view['النسبة مئوية (%)'] = ext_formatted_view['النسبة مئوية (%)'].map('{:.1f}%'.format)
    
    # عرض الجدول التحليلي المتقدم
    st.dataframe(ext_formatted_view, use_container_width=True, height=400)
    
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        # رسم بياني دائري (Pie Chart) للنسب مئوية للحجم الحقيقي لأكبر 8 أنواع
        st.markdown("#### رسم بياني دائري: توزيع النسب مئوية للحجم حسب النوع الحقيقي:")
        fig_pie_chart = px.pie(ext_analysis_df.head(8), names='نوع الملف', values='إجمالي الحجم (MB)', hole=0.4, title='أكبر 8 أنواع ملفات حجماً (نسب مئوية حقيقية)')
        st.plotly_chart(fig_pie_chart, use_container_width=True)
    with chart_col2:
        # رسم بياني شريطي (Bar Chart) لعدد الملفات الحقيقي لأكبر 10 أنواع
        st.markdown("#### رسم بياني شريطي: عدد الملفات لكل نوع حقيقي (أكبر 10):")
        fig_bar_count_chart = px.bar(ext_analysis_df.head(10), x='نوع الملف', y='عدد الملفات', title='أكبر 10 أنواع من حيث عدد الملفات الحقيقي', labels={'عدد الملفات': 'عدد الملفات الحقيقي'})
        st.plotly_chart(fig_bar_count_chart, use_container_width=True)

    st.markdown("---")

    # --- 5. خانات تحميل التقرير بتنسيق Excel & PDF (تعديل جذري) ---
    st.markdown("<h2 class='section-header'>📥 تحميل تقارير الأداء والبيانات الكاملة (Excel & PDF)</h2>", unsafe_allow_html=True)
    st.write("احصل على ملفات مفصلة لبياناتك الـ 10,000 بتنسيقات مختلفة:")
    
    col_dl1, col_dl2 = st.columns(2)
    
    # تحميل Excel (البيانات الكاملة - مضمونة التشغيل دائماً)
    with col_dl1:
        st.markdown("#### 🟢 تحميل البيانات الكاملة بتنسيق Excel")
        st.write("تحميل ملف Excel يحتوي على كافة الصفوف الـ 10,000 الحقيقية والتفاصيل الكاملة.")
        # إنشاء ملف Excel خارج الدالة لضمان توفر البيانات
        excel_full_data_report = to_excel(main_df)
        st.download_button(
            label="📥 تحميل ملف Excel الكامل والحقيقي",
            data=excel_full_data_report,
            file_name=f'dropbox_data_10k_full_report_{selected_filter_val[:15]}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    # تحميل PDF (الملخص) - يتم تفعيله كشرطياً
    with col_dl2:
        st.markdown("#### 🔴 تحميل ملخص الأداء بتنسيق PDF")
        if PDF_ENABLED:
            st.write("تحميل تقرير PDF أنيق يحتوي على ملخص لصف المؤشرات الـ 12 الرئيسية الحالية.")
            # إنشاء ملف PDF خارج الدالة لضمان توفر البيانات
            pdf_summary_report = create_pdf_summary_pro(current_kpi_values, current_title_prefix)
            st.download_button(
                label="📥 تحميل ملخص الأداء بتنسيق PDF",
                data=pdf_summary_report,
                file_name=f'dropbox_kpi_summary_{current_title_prefix.replace(": ", "_")}.pdf',
                mime='application/pdf'
            )
        else:
            # رسالة تعليمية في حال لم يتم تثبيت مكتبة PDF على خادم Streamlit Cloud
            st.warning("⚠️ ميزة الـ PDF متوقفة حالياً. \n\n**لتفعيل زر تحميل PDF**، يجب عليك التأكد من إضافة مكتبة `reportlab` إلى ملف **`requirements.txt`** في مجلد مشروعك على GitHub.")
            st.write("محتوى ملف requirements.txt المقترح:")
            st.code("reportlab\npandas\nplotly\nstreamlit\nxlsxwriter")

st.markdown("---")
st.caption("تم إنشاء هذه اللوحة الاحترافية ببياناتك الفعلية من ملف 'خريطة ملفات الدروبكس.csv' باستخدام Streamlit, Pandas, & Plotly.")
