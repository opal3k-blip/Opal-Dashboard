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

# --- دالة لتحميل وتنظيف البيانات ---
@st.cache_data
def load_data():
    # اسم ملف البيانات الفعلي الذي قدمته (يجب أن يكون في نفس مجلد الكود)
    data_file = 'خريطة_ملفات_الدروبكس_المعدلة.csv'
    
    if not os.path.exists(data_file):
        st.error(f"⚠️ لم يتم العثور على ملف البيانات: '{data_file}'. تأكد من وضعه في نفس مجلد الكود.")
        return pd.DataFrame()

    try:
        # قراءة البيانات الخام بطريقة utf-8 لقراءة الحروف العربية
        df = pd.read_csv(data_file, encoding='utf-8') 
        df.dropna(how='all', inplace=True) # إزالة الصفوف الفارغة بالكامل
        
        # تحويل عمود الحجم إلى ميغابايت (MB) من عمود 'Size (Bytes)' الموجود في ملفك
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
        df.loc[df['top_folder'].str.startswith('Jadeer'), 'top_folder'] = 'Jadeer'
        
        return df
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف أو تحليله: {e}")
        return pd.DataFrame()

# --- دالة لإنشاء مؤشرات KPIs احترافية وديناميكية (12 مؤشر كامل) ---
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
    total_mb_all_for_dominance = filtered_df['Size (MB)'].sum()
    top_ext_by_size = filtered_df.groupby('extension')['Size (MB)'].sum().idxmax()
    top_ext_size_gb = filtered_df.groupby('extension')['Size (GB)'].sum().max()
    top_ext_percentage = (top_ext_size_gb * 1024 / total_mb_all_for_dominance) * 100 if total_mb_all_for_dominance > 0 else 0

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

# --- دالة لإنشاء ملف Excel للتحميل ---
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DropboxData')
    processed_excel = output.getvalue()
    return processed_excel

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

    # --- 2. إدارة الـ KPIs الديناميكية بناءً على الفلتر (12 مؤشر) ---
    if selected_filter_val == "(عرض كامل الـ 10,000 ملف الحقيقيين)":
        render_kpis(main_df, len(main_df), "للكل الحقيقيين ")
        current_data_view = main_df.copy()
    elif selected_filter_val in main_df['top_folder'].unique():
        # النقر على الشركة الرئيسية المدمجة
        filtered_view_df = main_df[main_df['top_folder'] == selected_filter_val].copy()
        render_kpis(filtered_view_df, len(main_df), f"لشركة: {selected_filter_val}")
        current_data_view = filtered_view_df.copy()
    else:
         # النقر على مجلد فرعي عميق
         filtered_view_df = main_df[main_df['parent_path'].str.startswith(str(selected_filter_val))].copy()
         render_kpis(filtered_view_df, len(main_df), f"ل للمجلد: {selected_filter_val}")
         current_data_view = filtered_view_df.copy()

    st.markdown("---")

    # --- 3. التحليل الهرمي العميق وتوسيع قسم التحليل السفلي (الآن 6 صور) ---
    st.markdown("<h2 class='section-header'>🏢 استكشاف الهيكل الهرمي وقسم التحليل السفلي المطور (6 رسومات)</h2>", unsafe_allow_html=True)
    st.write("انقر فوق أي جزء لاستكشاف المجلدات الفرعية العميقة وتوزيع الحجم.")
    
    # Sunburst Chart بالبيانات المجمعة المتسقة والحقيقية
    fig_sun = px.sunburst(current_data_view, 
                         path=['top_folder', 'parent_path'], values='Size (MB)', # المسار الهرمي العميق
                         color='top_folder', hover_data={'top_folder': True, 'parent_path': True, 'Size (MB)': ':.2f'}) 
    
    fig_sun.update_layout(margin=dict(t=50, l=25, r=25, b=25)) # إعدادات الهامش
    st.plotly_chart(fig_sun, use_container_width=True) # عرض بدون ميزة Rerun التفاعلية المباشرة لتجنب APIError
    
    st.markdown("---")

    # --- 4. تحليل تفصيلي لمحتويات الملفات ونسبها (Pivot Analysis & Percentages) ---
    # لقد تم نقل هذا القسم ليكون ضمن قسم التحليل السفلي الجديد
    st.markdown("<h2 class='section-header'>📄 تحليل متقدم وشامل للأنواع والشركات ونسب الاستهلاك (6 رسومات متفاعلة)</h2>", unsafe_allow_html=True)
    
    # تجميع البيانات وحساب النسب بدقة (يعمل على البيانات المفلترة حالياً)
    ext_analysis_df_orig = current_data_view.groupby('extension').agg(
        total_size_mb=('Size (MB)', 'sum'),
        file_count=('name', 'count')
    ).reset_index()
    
    # حساب النسب مئوية للحجم الإجمالي الحقيقي (مع التأكد من القسمة على صفر)
    total_mb_all_for_analisis = current_data_view['Size (MB)'].sum()
    if total_mb_all_for_analisis > 0:
        ext_analysis_df_orig['percentage'] = (ext_analysis_df_orig['total_size_mb'] / total_mb_all_for_analisis) * 100
    else:
        ext_analysis_df_orig['percentage'] = 0
        
    ext_analysis_df_orig.columns = ['نوع الملف', 'إجمالي الحجم (MB)', 'عدد الملفات', 'النسبة مئوية (%)']
    ext_analysis_df_orig = ext_analysis_df_orig.sort_values(by='إجمالي الحجم (MB)', ascending=False)
    
    # تنسيق الجدول بشكل احترافي
    ext_formatted_view_final = ext_analysis_df_orig.copy()
    ext_formatted_view_final['إجمالي الحجم (MB)'] = ext_formatted_view_final['إجمالي الحجم (MB)'].map('{:,.2f}'.format)
    ext_formatted_view_final['عدد الملفات'] = ext_formatted_view_final['عدد الملفات'].map('{:,}'.format)
    ext_formatted_view_final['النسبة مئوية (%)'] = ext_formatted_view_final['النسبة مئوية (%)'].map('{:.1f}%'.format)
    
    # عرض الجدول التحليلي المتقدم
    st.markdown("#### جدول تحليلي لمحتويات وأنواع الملفات وحجومها ونسبها الحقيقية:")
    st.dataframe(ext_formatted_view_final, use_container_width=True, height=400)
    
    st.markdown("---")
    
    # --- توسيع جزئية العرض السفلي (الآن 6 رسومات بيانية متفاعلة) ---
    
    # شبكة الرسومات الأول (الرسومات الـ 2 الموجودة سابقاً)
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        # رسم بياني دائري (الحجم MB) الحقيقي لأكبر 8 أنواع
        st.markdown("#### رسم بياني دائري: توزيع النسب مئوية للحجم حسب النوع الحقيقي:")
        fig_pie_chart_final = px.pie(ext_analysis_df_orig.head(8), names='نوع الملف', values='إجمالي الحجم (MB)', hole=0.4, title='أكبر 8 أنواع ملفات حجماً (نسب مئوية حقيقية)')
        st.plotly_chart(fig_pie_chart_final, use_container_width=True)
    with chart_col2:
        # رسم بياني شريطي (عدد الملفات) الحقيقي لأكبر 10 أنواع
        st.markdown("#### رسم بياني شريطي: عدد الملفات لكل نوع حقيقي (أكبر 10):")
        fig_bar_count_chart_final = px.bar(ext_analysis_df_orig.head(10), x='نوع الملف', y='عدد الملفات', title='أكبر 10 أنواع من حيث عدد الملفات الحقيقي', labels={'عدد الملفات': 'عدد الملفات الحقيقي'})
        st.plotly_chart(fig_bar_count_chart_final, use_container_width=True)

    # شبكة الرسومات الثانية (الرسومات الـ 2 الجديدة والمطورة)
    st.markdown("---")
    st.markdown("#### تحليل كثافة الملفات ومساحة الشركات الكبرى (جديد ومطور):")
    chart_col3, chart_col4 = st.columns(2)
    with chart_col3:
        # شريطي أفقي (جديد): أكبر 10 شركات حجماً بالجيجابايت (GB)
        st.markdown("#### مخطط شريطي أفقي: أكبر 10 شركات استهلاكاً للمساحة الحقيقية:")
        company_gb_view = current_data_view.groupby('top_folder')['Size (GB)'].sum().reset_index().sort_values(by='Size (GB)', ascending=False).head(10)
        fig_bar_company_final = px.bar(company_gb_view, x='Size (GB)', y='top_folder', orientation='h', title='أكبر 10 شركات حجماً (GB)', color='Size (GB)', color_continuous_scale='Blues')
        fig_bar_company_final.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar_company_final, use_container_width=True)
    with chart_col4:
        # رسم بياني مبعثر Scatter (جديد): العلاقة بين عدد الملفات والحجم لكل شركة
        st.markdown("#### رسم بياني مبعثر: العلاقة بين عدد الملفات وإجمالي الحجم (GB) لكل شركة:")
        company_scatter_stats = current_data_view.groupby('top_folder').agg(num_files=('name', 'count'), total_gb=('Size (GB)', 'sum')).reset_index()
        fig_scatter_chart_final = px.scatter(company_scatter_stats, x='num_files', y='total_gb', text='top_folder', size='total_gb', color='total_gb', title='العلاقة بين عدد الملفات والحجم لكل شركة', labels={'num_files': 'عدد الملفات الحقيقي', 'total_gb': 'إجمالي الحجم (GB)'})
        st.plotly_chart(fig_scatter_chart_final, use_container_width=True)

    # شبكة الرسومات الثالثة (الرسومات الـ 2 الجديدة والمطورة)
    st.markdown("---")
    st.markdown("#### تحليل توزيع الأنواع الهرمي والتنوع المكدس (جديد ومطور):")
    chart_col5, chart_col6 = st.columns(2)
    with chart_col5:
        # مخطط Tree Map هرمي (جديد): توزيع الحجم حسب الشركة ونوع الملف
        st.markdown("#### مخطط Tree Map هرمي: توزيع حجم المساحة حسب الشركة والنوع للملفات الكبرى:")
        fig_tree_map_chart = px.treemap(current_data_view[current_data_view['extension'].isin(ext_analysis_df_orig.head(5)['نوع الملف'])], path=['top_folder', 'extension'], values='Size (MB)', color='top_folder', title='مخطط Tree Map هرمي: توزيع مساحة الأنواع الكبرى داخل الشركات')
        st.plotly_chart(fig_tree_map_chart, use_container_width=True)
    with chart_col6:
        # رسم بياني شريطي مكدس Stacked Bar (جديد): توزيع الأنواع لأكبر 5 شركات عدداً
        # اختيار الشركات الكبرى
        top_5_cos_by_count_list = current_data_view['top_folder'].value_counts().head(5).index
        stacked_df_data = current_data_view[current_data_view['top_folder'].isin(top_5_cos_by_count_list)]
        # التركيز على أنواع ملفات رئيسية (PDF, images, excel, docs) لوضوح الرسم
        doc_exts = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'png', 'jpg', 'jpeg']
        stacked_df_data_docs = stacked_df_data[stacked_df_data['extension'].str.lower().isin(doc_exts)]
        
        st.markdown("#### رسم بياني شريطي مكدس: توزيع أنواع الملفات الرئيسية داخل أكبر 5 شركات عدداً:")
        fig_stacked_bar_chart = px.bar(stacked_df_data_docs, x='top_folder', y='Size (GB)', color='extension', title='توزيع الأنواع الكبرى داخل الشركات عدداً', labels={'Size (GB)': 'الحجم (GB)', 'top_folder': 'الشركة'})
        st.plotly_chart(fig_stacked_bar_chart, use_container_width=True)

    st.markdown("---")

    # --- 5. خانات تحميل البيانات الكاملة والحقيقية (Excel Download) ---
    st.markdown("<h2 class='section-header'>📥 تحميل تقارير البيانات الكاملة والحقيقية (Excel)</h2>", unsafe_allow_html=True)
    st.write("احصل على ملف Excel يحتوي على كافة الصفوف الـ 10,000 الحقيقية والتفاصيل الكاملة.")
    
    excel_full_data_view_final = to_excel(main_df)
    st.download_button(label="📥 تحميل ملف Excel الكامل والحقيقي", data=excel_full_data_view_final, file_name='dropbox_data_10k_full_view.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

else:
    # سيتم عرض رسالة الخطأ من دالة load_data()
    pass

st.markdown("---")
st.caption("تم إنشاء هذه اللوحة الاحترافية ببياناتك الفعلية من ملف 'خريطة ملفات الدروبكس.csv' باستخدام Streamlit, Pandas, & Plotly.")
