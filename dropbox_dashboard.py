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
            df['Size (MB)'] = pd.to_numeric(df['Size (Bytes)']) / (1024 * 1024) # تحويل من بايت لـ MB
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

# --- دالة لإنشاء مؤشرات KPIs احترافية وديناميكية ---
def render_kpis(filtered_df, total_files, title_prefix="للكل"):
    st.markdown(f"<h3 class='section-header'>📌 مؤشرات أداء رئيسية متقدمة لـ 10K ملف ({title_prefix})</h3>", unsafe_allow_html=True)
    
    # تنسيق بطاقات الـ KPIs داخل حاوية مخصصة
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

    # عدد الشركات الرئيسية المدمجة
    num_companies = len(filtered_df['top_folder'].unique())

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
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>أكثر المجلدات عمقاً</div><div class='kpi-value'>{max_depth}</div><div class='kpi-sub'>مستويات هرمية</div></div>", unsafe_allow_html=True)
    with col7:
         st.markdown(f"<div class='kpi-card'><div class='kpi-title'>الشركات الرئيسية المدمجة</div><div class='kpi-value'>{num_companies}</div><div class='kpi-sub'>ملفات مدمجة</div></div>", unsafe_allow_html=True)

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
    st.markdown("<h2 class='section-header'>🏢 استكشاف الهيكل الهرمي وتوزيع المساحة (تفاعلي - تم دمج 'جدير')</h2>", unsafe_allow_html=True)
    st.write("انقر فوق أي جزء لاستكشاف المجلدات الفرعية العميقة وتحديث المؤشرات والنسب مئوية.")
    
    # أولاً: رسم مخطط Sunburst التفاعلي
    # Sunburst Chart: الشركة المدمجة -> المسار الهرمي العميق -> الملفات
    fig_sun = px.sunburst(df, 
                         path=['top_folder', 'parent_path'], # المسار الهرمي
                         values='Size (MB)', # الحجم للقياس
                         color='top_folder', # تلوين حسب الشركة المدمجة
                         hover_data={'top_folder': True, 'parent_path': True, 'Size (MB)': ':.2f'}) # تفاصيل إضافية عند التمرير
    
    fig_sun.update_layout(margin=dict(t=50, l=25, r=25, b=25)) # إعدادات الهامش
    
    # جعل المخطط تفاعلي مع Streamlit
    sunburst_event = st.plotly_chart(fig_sun, use_container_width=True, on_select="rerun", selection_mode="point")
    
    st.markdown("---")

    # --- 2. إدارة الـ KPIs الديناميكية (تفاعلية) ---
    # تحديد البيانات التي تم اختيارها من مخطط Sunburst
    selected_points = sunburst_event.get("selection", {}).get("points", [])
    
    # --- النقطة الحاسمة: التنسيق (Indentation) هنا مهم جداً ---
    if selected_points:
        # استخراج المسار الذي تم النقر عليه (مثلاً ["Jadeer"])
        clicked_path_str = selected_points[0].get("id", "")
        clicked_path = clicked_path_str.split('/')
        
        # فلترة البيانات بناءً على المسار
        if len(clicked_path) == 1:
            filtered_df = df[df['top_folder'] == clicked_path[0]].copy()
            render_kpis(filtered_df, len(df), f"لشركة المدمجة: {clicked_path[0]}")
            current_data = filtered_df.copy() # الاحتفاظ بالبيانات الحالية للتحليل
        else:
             full_path_str = clicked_path_str # مثل "Jadeer/مشاريع"
             filtered_df = df[df['parent_path'].str.startswith(full_path_str)].copy()
             render_kpis(filtered_df, len(df), f"ل للمجلد للمجلد: {full_path_str}")
             current_data = filtered_df.copy() # الاحتفاظ بالبيانات الحالية للتحليل
             
    else:
        # عرض الـ KPIs الافتراضية لكافة الملفات (10K) - تم إصلاح النقطة العمياء
        render_kpis(df, len(df), "للكل - تم دمج 'جدير'")
        current_data = df.copy() # الاحتفاظ بالبيانات الحالية للتحليل (ملف الكل)

    st.markdown("---")

    # --- 3. تحليل تفصيلي لمحتويات الملفات ونسبها (Pivot Analysis & Percentages) ---
    st.markdown("<h2 class='section-header'>📄 تحليل محتويات وأنواع الملفات وحجومها والنسب مئوية</h2>", unsafe_allow_html=True)
    
    # تجميع البيانات بشكل متقدم وحساب النسب (يعمل على البيانات المفلترة حالياً)
    ext_df = current_data.groupby('extension').agg(
        total_size_mb=('Size (MB)', 'sum'),
        file_count=('name', 'count')
    ).reset_index()
    
    # حساب النسب مئوية للحجم
    total_size_mb_all_for_filter = current_data['Size (MB)'].sum()
    if total_size_mb_all_for_filter > 0:
        ext_df['percentage'] = (ext_df['total_size_mb'] / total_size_mb_all_for_filter) * 100
    else:
        ext_df['percentage'] = 0
        
    ext_df.columns = ['نوع الملف', 'إجمالي الحجم (MB)', 'عدد الملفات', 'النسبة مئوية (%)']
    
    # ترتيب من الأكبر حجماً للأصغر
    ext_df = ext_df.sort_values(by='إجمالي الحجم (MB)', ascending=False)
    
    # تنسيق الجدول لعرض النسب مئوية بشكل جميل
    ext_formatted = ext_df.copy()
    ext_formatted['إجمالي الحجم (MB)'] = ext_formatted['إجمالي الحجم (MB)'].map('{:,.2f}'.format)
    ext_formatted['عدد الملفات'] = ext_formatted['عدد الملفات'].map('{:,}'.format)
    ext_formatted['النسبة مئوية (%)'] = ext_formatted['النسبة مئوية (%)'].map('{:.1f}%'.format)
    
    # عرض الجدول التحليلي المتقدم
    st.markdown("#### جدول تحليلي لمحتويات وأنواع الملفات وحجومها ونسبها:")
    st.dataframe(ext_formatted, use_container_width=True, height=400)
    
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        # رسم بياني دائري للنسب مئوية
        st.markdown("#### رسم بياني دائري: توزيع النسب مئوية للحجم حسب النوع:")
        fig_pie = px.pie(ext_df.head(8), names='نوع الملف', values='إجمالي الحجم (MB)', hole=0.4, title='أكبر 8 أنواع ملفات (نسب مئوية)')
        st.plotly_chart(fig_pie, use_container_width=True)
    with chart_col2:
        # رسم بياني شريطي لعدد الملفات
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
st.caption("تم إنشاء هذه اللوحة الاحترافية جداً جداً جداً ببياناتك الفعلية من ملف 'خريطة ملفات الدروبكس.csv' باستخدام Streamlit, Pandas, & Plotly.")
