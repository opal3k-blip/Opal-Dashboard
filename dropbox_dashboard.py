import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

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
        # قراءة البيانات الخام بأبسط طريقة ممكنة لتجنب مشاكل الترميز
        # نخبره بوضوح أن الترميز هو utf-8 لقراءة الحروف العربية
        df = pd.read_csv(data_file, encoding='utf-8') 
        df.dropna(how='all', inplace=True) # إزالة الصفوف الفارغة بالكامل
        
        # تحويل عمود الحجم إلى ميغابايت (MB) وجيجابايت (GB) من عمود 'Size (Bytes)' الموجود في ملفك
        if 'Size (Bytes)' in df.columns:
            # التأكد من تحويل عمود الحجم إلى رقم ومعالجة القيم غير الرقمية
            df['Size (Bytes)'] = pd.to_numeric(df['Size (Bytes)'], errors='coerce').fillna(0)
            df['Size (MB)'] = df['Size (Bytes)'] / (1024 * 1024)
            df['Size (GB)'] = df['Size (MB)'] / 1024
        else:
             st.warning("تنبيه: لم يتم العثور على عمود 'Size (Bytes)'.")
            
        # --- الإجراء الحاسم: دمج كافة أقسام 'جدير' في ملف واحد ---
        # إنشاء عمود للشركة الرئيسية (الجزء الأول من المسار)
        df['top_folder'] = df['parent_path'].apply(lambda x: str(x).split('/')[0])
        
        # استبدال كافة المسارات التي تبدأ بـ 'Jadeer' لتصبح 'Jadeer' فقط في عمود الشركة الرئيسية
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
def create_pdf_summary(kpi_data, title_prefix):
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
