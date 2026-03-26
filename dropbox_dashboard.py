import streamlit as st
import pandas as pd
import plotly.express as px
import io
import xlsxwriter # تأكد من أن هذه المكتبة مثبتة لديك

# --- 1. إعدادات الصفحة الأساسية والتنسيق ---
st.set_page_config(page_title="Dropbox 10K Dashboard", layout="wide")

st.markdown("""
<style>
    .kpi-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05); text-align: center;
        border: 1px solid #e1e4e8; margin-bottom: 20px;
    }
    .kpi-title { font-size: 16px; color: #6a737d; margin-bottom: 8px; }
    .kpi-value { font-size: 30px; font-weight: bold; color: #1f77b4; }
    .kpi-sub { font-size: 14px; color: #888; }
</style>
""", unsafe_allow_html=True)

# --- العنوان ---
st.title("📊 لوحة تحكم Dropbox (10,000 ملف الحقيقيين)")
st.markdown("---")

# --- 2. تحميل البيانات بطريقة مضمونة جداً ومبسطة ---
@st.cache_data
def load_data_guaranteed():
    # اسم ملف البيانات الفعلي الذي قدمته (يجب أن يكون في نفس مجلد الكود)
    file_path = 'خريطة_ملفات_الدروبكس_المعدلة.csv'
    
    try:
        # قراءة البيانات الخام بأبسط طريقة ممكنة لتجنب أي مشاكل في الترميز أو الحقول الفارغة
        # نخبره بوضوح أن الترميز هو utf-8 لقراءة الحروف العربية
        raw_df = pd.read_csv(file_path, encoding='utf-8')
        
        # تنظيف البيانات الأساسي
        raw_df.dropna(how='all', inplace=True) # إزالة الصفوف الفارغة بالكامل
        
        # تحويل الحجم من بايت إلى ميغابايت (MB) وجيجابايت (GB)
        if 'Size (Bytes)' in raw_df.columns:
            raw_df['Size (Bytes)'] = pd.to_numeric(raw_df['Size (Bytes)'], errors='coerce').fillna(0)
            raw_df['Size (MB)'] = raw_df['Size (Bytes)'] / (1024 * 1024)
            raw_df['Size (GB)'] = raw_df['Size (MB)'] / 1024
            
        # إنشاء عمود الشركة المدمج (للتجميع المستقبلي إذا لزم الأمر)
        raw_df['Main Company'] = raw_df['parent_path'].apply(lambda x: str(x).split('/')[0])
        raw_df.loc[raw_df['Main Company'].str.startswith('Jadeer'), 'Main Company'] = 'Jadeer'
        
        return raw_df
    
    except Exception as e:
        # في حال حدوث خطأ، قم بطباعة رسالة واضحة للمستخدم
        st.error(f"⚠️ حدثت مشكلة في قراءة ملف البيانات: '{file_path}'. \n\nتأكد من أن الملف موجود في نفس مجلد الكود، وأن اسمه صحيح تماماً، وأنه ملف CSV برمز utf-8. \n\nالخطأ التقني: {e}")
        return pd.DataFrame()

# --- دالة لإنشاء ملف Excel للتحميل ---
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DropboxData')
    processed_excel = output.getvalue()
    return processed_excel

# --- تنفيذ تحميل البيانات ---
# نقوم بوضع تحميل البيانات خارج st.empty() لضمان التنفيذ أولاً
main_df = load_data_guaranteed()

# --- 3. بناء لوحة التحكم بناءً على نجاح التحميل ---
# إذا كانت البيانات فارغة، فهذا يعني أن دالة تحميل البيانات فشلت وطبعت رسالة الخطأ الخاصة بها.
if main_df.empty:
    st.warning("⚠️ لا يمكن تحميل لوحة التحكم لعدم توفر البيانات. يرجى مراجعة رسالة الخطأ أعلاه.")
else:
    # --- صف المؤشرات الاحترافية الـ 7 المدمج ---
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    
    # حساب القيم الأساسية بدقة من البيانات الحقيقية الـ 10K
    num_total_files = len(main_df)
    total_size_gb_all = main_df['Size (GB)'].sum()
    avg_size_mb_all = main_df['Size (MB)'].mean()
    
    # الشركة الأكثر استهلاكاً
    top_consumption_company = main_df.groupby('Main Company')['Size (MB)'].sum().idxmax()
    top_consumption_size_gb = main_df.groupby('Main Company')['Size (GB)'].sum().max()
    
    # النوع المهيمن (حجماً)
    top_ext_by_size = main_df.groupby('extension')['Size (MB)'].sum().idxmax()
    top_ext_size_gb = main_df.groupby('extension')['Size (GB)'].sum().max()
    
    # أكثر المجلدات عمقاً
    main_df['path_depth_lvl'] = main_df['parent_path'].apply(lambda x: len(str(x).split('/')))
    max_h_depth = main_df['path_depth_lvl'].max()
    
    # عرض المؤشرات السبعة الأنيقة
    with col1:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>إجمالي الملفات</div><div class='kpi-value'>{num_total_files:,}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>إجمالي الحجم (GB)</div><div class='kpi-value'>{total_size_gb_all:.2f}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>الشركة الأكثر استهلاكاً</div><div class='kpi
