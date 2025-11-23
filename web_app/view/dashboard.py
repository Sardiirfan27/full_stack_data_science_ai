import streamlit as st
from dw_bigquery import load_data
from gemini_generate_analysis import main_analysis_flow,clean_output
import view.custom_viz as cv
import plotly.express as px
import warnings
warnings.filterwarnings(
    "ignore",
    message=".*width.*"
)

# def render():
#     st.title("📊 Telco Churn Monitoring Dashboard")
#     st.write("Welcome! Use the menu to navigate.")
#     st.info(
#         "This dashboard will visualize churn distributions, trends, and inference logs.\n"
#         "🚧 More analytics can be integrated here later."
#     )
    
#     # ===== Loading Indicator =====
#     with st.spinner("🔄 Fetching data from BigQuery... Please wait"):
#         df = load_data()

#     st.success(f"✅ Data loaded successfully ({len(df)} rows)")

#     st.subheader("Customer Data (All Columns)")
#     st.dataframe(df)
#     return df


# ================== LOAD DATA ====================
# ✅ Data will be cached
@st.cache_data(ttl=1200)
def get_data():
    return load_data()

# ================== FILTER DATA (CACHE) ====================
@st.cache_data
def filter_data(df, services, churn):
    """
    Filter the dataset based on user selections from the multiselect widgets.
    """
    return df[
        df['InternetService'].isin(services)
        & df['Churn'].isin(churn)
    ]

# ================== MAIN DASHBOARD ==================
def render():
    # load data
    df_telco = get_data()
    
    st.title("📊Customer Churn Analysis")  
    # =====================================================
    # 🔹 KPI CARDS SECTION (WITH CONTAINER)
    # =====================================================
    with st.container():

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Customers", df_telco['customerID'].nunique())

        with col2:
            churn_count = df_telco[df_telco["Churn"] == "Yes"].shape[0]
            st.metric("Churn Customers", churn_count)

        with col3:
            churn_rate = round((churn_count / df_telco['customerID'].nunique()) * 100, 2)
            st.metric("Churn Rate (%)", churn_rate)

        with col4:
            avg_monthly = df_telco["MonthlyCharges"].mean()
            st.metric("Avg Monthly Charges", f"${avg_monthly:.2f}")


    # =====================================================
    # 🔹 MAIN DASHBOARD SECTION (WITH CONTAINER)
    # =====================================================
    colors=['#00FFFF','#0099ff','#146c87', '#FF00FF',
            '#0033ff', '#ed1f91', '#3792d7', '#ed1f91']
    
    # Definisikan Tab
    tab_names = ["Main", "Services", "Generate Analysis"]
    # Pastikan nilai default sudah diset. Kita akan menggunakan indeks tab sebagai state.
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Main" # Index 0 = "Main"
        
    # 2. Tampilkan Tabs dan simpan indeks tab yang dipilih pengguna
    current_tab = st.tabs(tab_names, 
                          default=st.session_state.active_tab,
                        ) 

    tab1, tab2, tab3 = current_tab # Unpack the tab objects
   
    with tab1: 
        col_filter1, col_filter2 = st.columns(2, gap="small")
        with col_filter1:
            selected_services = st.multiselect("Select Services", ["DSL", "Fiber optic", "No"], 
                                               default=["DSL", "Fiber optic", "No"],
                                               key="service_filter1")
        with col_filter2:
            selected_churn = st.multiselect("Select Churn", ["No", "Yes"], 
                                            default=["No", "Yes"],
                                            key="churn_filter1")
        
        df = filter_data(df_telco, selected_services, selected_churn)
              
        with st.container(key="container_dashboard_1"):
            # ---------------- Row 1 ----------------
            col1, col2, col3 = st.columns([0.25,0.25,0.5], gap="small")

            with col1:
                churn_counts = df['Churn'].value_counts()
                labels = churn_counts.index
                values = churn_counts.values
                fig1 = cv.visualize_piechart(
                    labels=labels,
                    values=values,
                    colors=["#00FFFF", '#ed1f91'],
                    var="Churn"
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 =cv.visualize_boxplot(
                    df=df,
                    x="Churn",
                    y="MonthlyCharges",
                    hue="Churn",
                    colors=["#00FFFF", "#ed1f91"],
                    var="Monthly Charges"
                )
                st.plotly_chart(fig2, use_container_width=True)
                
            with col3:

                fig3= cv.visualize_histogram(
                    df,
                    x="MonthlyCharges",
                    hue="Churn",
                    colors=[ '#00FFFF','#ed1f91'],
                    nbins=30,
                    title="Monthly Charges Distribution"
                    
                )
                st.plotly_chart(fig3,use_container_width=True)
       

            # ---------------- Row 2 ----------------
            col4, col5 = st.columns(2, gap="small")

            with col4:
                fig4 = cv.visualize_histogram_with_boxplot(
                    df=df,
                    x="tenure",
                    hue="Churn",
                    nbins=20,
                    colors=["#00FFFF", "#ed1f91"],
                    title="Tenure Distribution"
                )
                st.plotly_chart(fig4, use_container_width=True)

            with col5:
                fig5 =cv.visualize_histogram_with_boxplot(
                    df=df,
                    x="TotalCharges",
                    hue="Churn",
                    nbins=20,
                    colors=["#00FFFF", "#ed1f91"],
                    title="Total Charges"
                )
                st.plotly_chart(fig5, use_container_width=True)
                
            # ---------------- Row 3 ----------------
            col6, col7 = st.columns(2, gap="small")

            with col6:
                fig6= px.sunburst(
                    df, 
                    path=['Contract','InternetService'], 
                    color='Contract',
                    color_discrete_map={
                        'Month-to-month':'#ed1f91', 
                        'One year':'#00FFFF', 
                        'Two year':'#3792d7'
                        })
        
                # Adding text to each group
                fig6.update_traces(textinfo='label + percent entry',
                insidetextorientation='horizontal',
                textfont_size=12)
            
                # Adding a suitable titleQ
                fig6.update_layout(
                    title='Distribution of Customers by Contract and Internet Service',
                    title_x=0)
                st.plotly_chart(fig6, use_container_width=True)
            
            with col7:
                fig7 = px.treemap(
                    df,
                    path=['InternetService', 'PaymentMethod'],   # Level 1 → Level 2
                    color='InternetService',
                    color_discrete_map={
                        'Fiber optic': '#ed1f91',
                        'No': '#00FFFF',
                        'DSL': '#3792d7'
                        }
                )
                fig7.update_traces(
                    textinfo="label+percent entry",
                    textfont_size=12,
                    hovertemplate=(
                        "<b>%{label}</b><br>"   # tetap tampilkan label normal
                        "Value: %{value}<br>"
                        "Percent of Parent: %{percentParent:.2%}<br>"
                        "Percent of Entry: %{percentEntry:.2%}<br>"
                        "<extra></extra>"
                    )
                )
                # Layout
                fig7.update_layout(
                    title='Distribution of Customer by Internet Service and Payment Method',
                    title_x=0,
                    margin=dict(t=50, l=0, r=0, b=0)
                )

                st.plotly_chart(fig7, use_container_width=True)
                
    with tab2:
        col_filter1, col_filter2 = st.columns(2, gap="small")
        with col_filter1:
            selected_services2 = st.multiselect("Select Services", ["DSL", "Fiber optic", "No"], 
                                               default=["DSL", "Fiber optic", "No"],
                                               key="services_filter2")
        with col_filter2:
            selected_churn2 = st.multiselect("Select Churn", ["No", "Yes"],
                                            default=["No", "Yes"],
                                            key="churn_filter2")
        
        df = filter_data(df_telco, selected_services2, selected_churn2)
        
        with st.container(key="container_dashboard_2"):
            st.subheader("📊 Services")
            col1, col2 = st.columns(2, gap="small")

            with col1:
                # total customers by internet service 
                counts = (
                            df["InternetService"].value_counts()
                            # .sort_values(ascending=True)
                            .reset_index()
                        )
                counts.columns = ['InternetService', "Count"]
                
                fig = cv.visualize_barchart(
                    df=counts,
                    x="InternetService",
                    y="Count",
                    #hue= "InternetService",
                    colors=["#FFEA00"],
                    var="Total Customers by Internet Service",
                    orientation="v"
                )
                st.plotly_chart(fig, use_container_width=True, key='tab2_col1')

            with col2:
                # pie chart: total customers by online security
                counts = (
                            df["OnlineSecurity"].value_counts()
                            .reset_index()
                        )
                counts.columns = ['OnlineSecurity', "Count"]
                fig = cv.visualize_piechart(
                    labels=counts['OnlineSecurity'],
                    values=counts['Count'],
                    colors=['#00FFFF','#FF00FF','#3792d7',],
                    explode=[0.01, 0.01, 0.01],
                    var="Online Security"
                )
                st.plotly_chart(fig, use_container_width=True, key='col2_tab2') 
            
            col3, col4,col5 = st.columns([0.4,0.2,0.2], gap="small")
            with col3:
                # bar chart grouped by Online Backup
                column = "OnlineBackup"
                df_group = (
                    df.groupby([column, "Churn"])
                    .size()
                    .reset_index(name="Count")
                )
                fig = px.bar(
                    df_group,
                    x=column,
                    y="Count",
                    color="Churn",
                    barmode="group",
                    title=f"{column} Distribution",
                    color_discrete_map={"Yes": "#ed1f91", "No": "#00FFFF"},
                )
                st.plotly_chart(fig, use_container_width=True)
                
            with col4:
                # pie chart grouped by Technical Support
                counts = df['TechSupport'].value_counts()
                fig1 = cv.visualize_piechart(
                    labels=counts.index,
                    values=counts.values,
                    colors=['#00FFFF','#FF00FF','#3792d7',],
                    var="Technical Support"
                )
                st.plotly_chart(fig1, use_container_width=True)
                            
            with col5:
                # pie chart grouped by Device Protection
                counts = df['DeviceProtection'].value_counts()
                fig1 = cv.visualize_piechart(
                    labels=counts.index,
                    values=counts.values,
                    colors=['#00FFFF','#FF00FF','#3792d7',],
                    var="Device Protection"
                )
                st.plotly_chart(fig1, use_container_width=True)
                
                
            col6, col7 = st.columns(2, gap="small")
            with col6:
                # bar chart: streaming tv
                fig = px.bar(
                    df,
                    x="StreamingTV",
                    color="Churn",
                    barmode="group",
                    title="Streaming TV Distribution",
                    color_discrete_map={"Yes": "#ed1f91", "No": "#00FFFF"},
                )
                st.plotly_chart(fig, use_container_width=True)
                
            with col7:
                # bar chart: streaming movies 
                fig = px.bar(
                    df,
                    x="StreamingMovies",
                    color="Churn",
                    barmode="group",
                    title="Streaming Movies Distribution",
                    color_discrete_map={"Yes": "#ed1f91", "No": "#00FFFF"},
                )
                st.plotly_chart(fig, use_container_width=True)
                
    with tab3:
        st.subheader("📊 Generate Analysis Using AI")
        # 🌟 Tambahkan kode ini untuk menyimpan status tab3
        st.session_state.active_tab = "Generate Analysis" # Index 2 = "Generate Analysis"
        # Expander panduan prompt
        with st.expander("💡 Klik disini untuk melihat contoh prompt"):
            st.markdown("""
                Berikut adalah contoh prompt yang dapat Anda gunakan:
                - **"Tampilkan tabel (pandas) jumlah pelanggan berdasarkan Contract dan apakah mereka Churn atau tidak."**
                - **"Buat bar chart perbandingan jumlah pelanggan churn berdasarkan jenis pembayaran (PaymentMethod)."**
                - **"Tampilkan pie chart proporsi pelanggan churn vs non-churn."**
                - **"Hitung jumlah pelanggan churn per Contract dan tampilkan tabel, bar chart dan insight dalam bahasa indonesia."**
                """
            )
        
        analysis_question = st.text_area(
            "Masukkan Pertanyaan atau Prompt Anda:",
            value="Hitung jumlah pelanggan yang 'Churn' (Yes) berdasarkan 'Contract' dan tampilkan dalam bentuk bar chart.",
            key="analysis_question_input"
        )
        if st.button("Generate Analysis",key="generate_analysis_button"):
            if not analysis_question:
                st.warning("Harap masukkan pertanyaan analisis terlebih dahulu.")
            else:
                
                # Menggunakan st.spinner untuk memberikan umpan balik visual
                with st.spinner("🧠 Sedang Memproses data dan menghasilkan analisa..."):
                        
                    df_result, python_code = main_analysis_flow(analysis_question)
                    if python_code and df_result is not None and not df_result.empty:
                        
                        # Bersihkan kode sekali lagi (meskipun sudah dilakukan di generate_python_chart_code)
                        # Ini adalah lapisan keamanan ekstra jika LLM gagal mengikuti system_instruction
                        # cleaned_code = clean_output(python_code) 
                        
                        st.success("✅ Analisis Selesai...")
                        
                        #  Tampilkan Kode yang Dihasilkan (untuk debugging/transparansi)
                        # with st.expander("Lihat Kode Python yang Dihasilkan"):
                        #     st.code(python_code, language='python')
                            
                        try:
                            # Jalankan kode yang sudah bersih
                            # Untuk keamanan, karena `df_result` adalah hasil kueri, kita harus membuatnya tersedia di lingkup global/lokal
                            # di mana `exec` dijalankan.
                            exec(python_code, globals(), {'df_result': df_result, 'st': st})
                            
                        except Exception as e:
                            st.error(f"❌ Gagal menjalankan kode Python yang dihasilkan: {e}")
                            st.code(python_code, language='python') # Tampilkan kode jika gagal
                    
                    elif df_result is not None and df_result.empty:
                            st.warning("⚠️ Kueri SQL berhasil dieksekusi, tetapi data yang dikembalikan kosong. Tidak dapat membuat chart.")
                    else:
                        st.error("❌ Gagal total dalam proses analisis (SQL atau Gemini API error).")
                        
if "initial_rerun_done" not in st.session_state:
   st.session_state.initial_rerun_done = True
   st.rerun()