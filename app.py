import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import plotly.express as px
from mlxtend.frequent_patterns import apriori, association_rules

st.set_page_config(page_title="Koperasi Sales Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_excel("dataset_lowermh.xlsx")
    df['transaction_datetime'] = pd.to_datetime(df['transaction_datetime'])
    df['transaction_date'] = df['transaction_datetime'].dt.date  # Menambahkan kolom transaction_date
    return df

df = load_data()

# Sidebar Navigation
menu = st.sidebar.selectbox("Menu:", ["📊 Dashboard", "🤝 Sistem Rekomendasi Produk Koperasi"], index=0)

# CSS for background
background_images = {
    "📊 Dashboard": "background_dashboard.jpg",
    "🤝 Sistem Rekomendasi Produk Koperasi": "background_asosiasi.jpg"
}

st.markdown(
    f"""
    <style>
    .stApp {{
        background: url("{background_images[menu]}") no-repeat center center fixed;
        background-size: cover;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

####### Dashboard #######
if menu == "📊 Dashboard":
    st.markdown("<h1 style='text-align: center;'> 🥛Dashboard Penjualan KUD Sarwa Mukti🥛</h1>", unsafe_allow_html=True)
    image = Image.open('coffe.jpg')
    st.image(image, use_column_width=True)

    st.markdown("""<style>
        .metric-container {background-color: #F5F5DC; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px;}
        .divider {border-top: 3px solid #8B4513; margin-top: 20px; margin-bottom: 20px;}
        .small-subheader {font-size: 22px; font-weight: bold; color: #8B4513;}
    </style>""", unsafe_allow_html=True)

    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("📈 Total Sales product", f"{df['transaction_qty'].sum():,}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("💰 Total Revenue", f"Rp.{(df['Revenue'].sum()):,}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("📦 Total Transaction", f"{df['new_invoice_id'].count()}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("🔄 Unique Products", f"{df['product_detail'].nunique()}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Revenue Trends
    st.markdown('<div class="small-subheader">📊Daily Revenue</div>', unsafe_allow_html=True)
    daily_qty = df.groupby('transaction_date')['Revenue'].sum().reset_index()
    fig_line = px.line(daily_qty, x='transaction_date', y='Revenue', title="Daily Revenue", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Transaction Trends
    st.markdown('<div class="small-subheader">📊Daily Transaction Quantity</div>', unsafe_allow_html=True)
    daily_qty = df.groupby('transaction_date')['transaction_qty'].sum().reset_index()
    fig_line = px.line(daily_qty, x='transaction_date', y='transaction_qty', title="Daily Transaction Quantity", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

    # Filter untuk memilih tanggal tertentu
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="small-subheader">📅 Pilih Tanggal untuk Melihat Tren Transaksi</div>', unsafe_allow_html=True)
    selected_date = st.date_input("Pilih tanggal:", value=pd.to_datetime(df['transaction_date'].max()), min_value=df['transaction_date'].min(), max_value=df['transaction_date'].max())

    filtered_df = df[df['transaction_date'] == selected_date]
    if not filtered_df.empty:
        daily_filtered = filtered_df.groupby('transaction_datetime')['transaction_qty'].sum().reset_index()
        fig_filtered_line = px.line(daily_filtered, x='transaction_datetime', y='transaction_qty', title=f"Tren Transaksi pada {selected_date}", markers=True)
        st.plotly_chart(fig_filtered_line, use_container_width=True)
    else:
        st.warning(f"Tidak ada transaksi pada {selected_date}")
    
    # Pie Charts for Product Category and Product Type in One Row
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="small-subheader">🍰 Distribusi Kategori Produk dan Tipe Produk</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        product_category_dist = df['product_category'].value_counts().reset_index()
        product_category_dist.columns = ['Product Category', 'Count']
        fig_pie_category = px.pie(product_category_dist, names='Product Category', values='Count', 
                                  title="Distribusi Kategori Produk")
        st.plotly_chart(fig_pie_category, use_container_width=True)

    with col2:
        product_type_dist = df['product_type'].value_counts().reset_index()
        product_type_dist.columns = ['Product Type', 'Count']
        fig_pie_type = px.pie(product_type_dist, names='Product Type', values='Count', 
                              title="Distribusi Tipe Produk")
        st.plotly_chart(fig_pie_type, use_container_width=True)

    # Top 10 Best-Selling Products
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="small-subheader">🔥 10 Produk Terlaris</div>', unsafe_allow_html=True)
    top_products = df.groupby('product_detail')['transaction_qty'].sum().sort_values(ascending=False).head(10).reset_index()
    fig_barh = px.bar(top_products, x='transaction_qty', y='product_detail', orientation='h', 
                      title="Top 10 Produk Paling Banyak Terjual", color='transaction_qty',
                      color_continuous_scale='Oranges')
    fig_barh.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_barh, use_container_width=True)

####### Sistem Rekomendasi Produk Kopi #######
elif menu == "🤝 Sistem Rekomendasi Produk Koperasi":
    st.title("🤝 Analisis Asosiasi dengan Apriori")

    df_assoc = df.dropna(subset=['new_invoice_id'])
    df_assoc['new_invoice_id'] = df_assoc['new_invoice_id'].astype(str)
    df_assoc = df_assoc[~df_assoc['new_invoice_id'].str.contains('C')]

    min_support = st.slider("🔧 Minimum Support", 0.01, 0.02)

    basket = df_assoc.groupby(['new_invoice_id', 'product_detail'])['transaction_qty'].sum().unstack().fillna(0)
    basket_sets = basket.applymap(lambda x: 1 if x > 0 else 0)

    frequent_itemsets = apriori(basket_sets, min_support=min_support, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric='lift', min_threshold=0.7)


    selected_products = st.text_input("Masukkan produk yang dibeli (pisahkan dengan koma):")
    if selected_products:
            selected_products = set(p.strip() for p in selected_products.split(','))

            recommendations = {}
            for _, row in rules.iterrows():
                antecedents = set(row['antecedents'])
                consequents = set(row['consequents'])

                if selected_products & antecedents:
                    for product in consequents:
                        recommendations[product] = recommendations.get(product, 0) + row['confidence']

            recommendations = {prod: score for prod, score in recommendations.items() if prod not in selected_products}
            top_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:3]

            if top_recommendations:
                st.success("✅ Produk yang direkomendasikan untuk Anda:")
                for product, score in top_recommendations:
                    st.write(f"🔹 **{product}** (Confidence: {score:.2f})")
            else:
                st.warning("⚠️ Tidak ada rekomendasi yang cocok dengan produk yang dipilih.")

            if rules.empty:
                st.warning("❌ Tidak ditemukan aturan asosiasi dengan support ini.")
            else:
                st.subheader("📌 Aturan Asosiasi Terbentuk")
                st.dataframe(rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']])
