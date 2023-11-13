import streamlit as st
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns

from datetime import datetime
from pathlib import Path
from matplotlib.ticker import FuncFormatter
import calendar
import os

# Baca data pelanggan, pesanan, dan pembayaran

os.chdir(Path(__file__).parents[1])

customer_data = pd.read_csv(Path(__file__).parents[1]/'Datasets/olist_customers_dataset.csv')
# geo_data = pd.read_csv(Path(__file__).parents[1]/'Datasets/olist_geolocation_dataset.csv')
order_items_data = pd.read_csv(Path(__file__).parents[1]/'Datasets/olist_order_items_dataset.csv')
order_payments_data = pd.read_csv(Path(__file__).parents[1]/'Datasets/olist_order_payments_dataset.csv')
order_reviews_data = pd.read_csv(Path(__file__).parents[1]/'Datasets/olist_order_reviews_dataset.csv')
orders_data = pd.read_csv(Path(__file__).parents[1]/'Datasets/olist_orders_dataset.csv')
products_data = pd.read_csv(Path(__file__).parents[1]/'Datasets/olist_products_dataset.csv')
sellers_data = pd.read_csv(Path(__file__).parents[1]/'Datasets/olist_sellers_dataset.csv')
product_category_data = pd.read_csv(Path(__file__).parents[1]/'Datasets/product_category_name_translation.csv')

# data cleaning

# Tabel customer
# mengubah tipe data kota customer menjadi string
customer_data['customer_city'] = customer_data['customer_city'].astype(str)
# kapitalisasi kota customer
customer_data['customer_city'] = customer_data['customer_city'].str.title()

# tabel order_items
# mengubah data tanggal order items menjadi data datetime
order_items_data['shipping_limit_date'] = pd.to_datetime(order_items_data['shipping_limit_date'])

# tabel order_payments
# mengubah tipe data tipe pembayaran menjadi string
order_payments_data['payment_type'] = order_payments_data['payment_type'].astype(str)
# menghapus underskor pada nama tipe pembayaran
order_payments_data['payment_type'] = order_payments_data['payment_type'].str.replace('_', ' ')
# kapitalisasi tipe pembayaran
order_payments_data['payment_type'] = order_payments_data['payment_type'].str.title()

# tabel order_reviews
# mengisi data order review yang kosong dengan "No Title"
order_reviews_data['review_comment_title'].fillna('No Title', inplace=True)
# mengisi data order review yang kosong dengan "No Message"
order_reviews_data['review_comment_message'].fillna('No Message', inplace=True)
# mengubah data tanggal order review menjadi data datetime
order_reviews_data['review_creation_date'] = pd.to_datetime(order_reviews_data['review_creation_date'])
order_reviews_data['review_answer_timestamp'] = pd.to_datetime(order_reviews_data['review_answer_timestamp'])

# tabel orders
# mengubah data tanggal order menjadi data datetime
orders_data['order_purchase_timestamp'] = pd.to_datetime(orders_data['order_purchase_timestamp'])
orders_data['order_approved_at'] = pd.to_datetime(orders_data['order_approved_at'])
orders_data['order_delivered_carrier_date'] = pd.to_datetime(orders_data['order_delivered_carrier_date'])
orders_data['order_delivered_customer_date'] = pd.to_datetime(orders_data['order_delivered_customer_date'])
orders_data['order_estimated_delivery_date'] = pd.to_datetime(orders_data['order_estimated_delivery_date'])

# --------------------------------------------------------------------- #
# -------------------- Visualisasi tipe pembayaran -------------------- #
# --------------------------------------------------------------------- #

def visualisasi_tipe_pembayaran():
    # Convert order_purchase_timestamp to datetime
    orders_data['order_purchase_timestamp'] = pd.to_datetime(orders_data['order_purchase_timestamp'])

    # Count the payment types
    counts = order_payments_data['payment_type'].value_counts()

    # Ambil 3 teratas
    top_3_counts = counts.head(3)

    # Create a Streamlit app
    st.subheader('Tipe Pembayaran Terbanyak')

    # Display the counts in a pie chart
    fig, ax = plt.subplots()
    ax.pie(top_3_counts, labels=top_3_counts.index, autopct='%1.1f%%', startangle=90, labeldistance=1.1, pctdistance=0.75)
    ax.axis('equal')
    ax.set_title('Tipe Pembayaran Terbanyak (Top 3)')

    # Display the pie chart using Streamlit
    st.pyplot(fig)

# ----------------------------------------------------------------------- #
# -------------------- Visualisasi Retensi pelanggan -------------------- #
# ----------------------------------------------------------------------- #

def visualisasi_review():
    # Bagian kode yang Anda miliki
    order_reviews_data['review_month'] = order_reviews_data['review_answer_timestamp'].dt.month
    order_reviews_data['review_year'] = order_reviews_data['review_answer_timestamp'].dt.year

    # Filter data berdasarkan tanggal awal hingga tanggal terbaru
    start_date = order_reviews_data['review_answer_timestamp'].min()
    end_date = order_reviews_data['review_answer_timestamp'].max()

    filtered_data = order_reviews_data[
        (order_reviews_data['review_answer_timestamp'] >= start_date) &
        (order_reviews_data['review_answer_timestamp'] <= end_date)
    ]

    # Group dan hitung rata-rata review score per bulan dan tahun
    monthly_mean = filtered_data.groupby(['review_year', 'review_month'])['review_score'].mean()

    # Buat label untuk sumbu x dengan format "<nomor_bulan> <tahun>"
    monthly_mean.index = monthly_mean.index.map(lambda x: f"{calendar.month_name[x[1]]} {x[0]}")

    # Hitung rata-rata keseluruhan
    overall_mean = monthly_mean.mean()

    # Visualisasi menggunakan Streamlit
    st.subheader('Rata-rata Review Pelanggan Secara Keseluruhan')
    # Plotting sebagai grafik garis
    fig, ax = plt.subplots(figsize=(10, 5))
    monthly_mean.plot(kind='line', marker='o', linestyle='-', ax=ax)
    ax.axhline(y=overall_mean, color='r', linestyle='--', label=f'Rata-rata Keseluruhan ({overall_mean:.2f})')

    plt.xticks(rotation=45)
    plt.xlabel('Tanggal (Bulan - Tahun)')
    plt.ylabel('Rata-rata Review Score')
    plt.title('Rata-rata Review Score Over Time')
    plt.legend()
    st.pyplot(fig)

# ------------------------------------------------------------------------------- #
# -------------------- Visualisasi Jumlah Pelanggan per Kota -------------------- #
# ------------------------------------------------------------------------------- #

def visualisasi_kota():
    st.subheader('Jumlah Pelanggan per Kota (Top 20 Cities)')
    # Group dan hitung jumlah pelanggan unik per kota
    top_20_cities = customer_data.groupby('customer_city')['customer_id'].nunique().sort_values(ascending=False).head(20)

    # Set up the appearance of the plot
    plt.figure(figsize=(20, 8))
    sns.set(style="whitegrid")

    # Create a bar plot
    ax = sns.barplot(x=top_20_cities.values, y=top_20_cities.index, palette="mako")

    # Add labels and title
    plt.xlabel('Jumlah Pelanggan')
    plt.ylabel('Kota Pelanggan')
    plt.title('Jumlah Pelanggan per Kota (Top 20 Cities)')

    # Adjust the rotation of city labels for better readability
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, horizontalalignment='right')
    
    # Add values next to the bars
    for i, v in enumerate(top_20_cities.values):
        ax.text(v + 3, i + .25, str(round(v, 3)), color='black')

    # Adjust x-axis values to thousands format
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: '{:,.0f}'.format(x * 1)))

    # Show the plot using Streamlit
    st.pyplot(plt)

# ------------------------------------------------------------ #
# -------------------- Visualisasi produk -------------------- #
# ------------------------------------------------------------ #

def visualisasi_produk():
    st.subheader('Kategori produk yang paling banyak dibeli')
    # menghitung jumlah pembayaran produk terbanyak
    order_product = pd.merge(orders_data, order_items_data, on='order_id')
    order_product = pd.merge(order_product, order_payments_data, on='order_id')
    order_product = pd.merge(order_product, products_data, on='product_id')
    order_product = pd.merge(order_product, product_category_data, on='product_category_name')

    order_product.groupby('product_category_name_english')['payment_value'].sum().sort_values(ascending=False).head(10)
    
    # Group dan hitung total payment value per kategori produk
    category_payment_sum = order_product.groupby('product_category_name_english')['payment_value'].sum().sort_values(ascending=False)

    # Menyesuaikan tampilan plot
    plt.figure(figsize=(30, 20))
    sns.set(style="whitegrid")
    ax = sns.barplot(x=category_payment_sum.values, y=category_payment_sum.index, palette="viridis")

    # menambahkan label dan judul
    plt.xlabel('Total Payment Value')
    plt.ylabel('Product Category')
    plt.title('Total Payment Value by Product Category (Top Categories)')

    # Add values next to the bars
    for i, v in enumerate(category_payment_sum.values):
        ax.text(v + 3, i + .25, str(round(v, 3)), color='black', fontweight='bold')

    # Adjust x-axis values to thousands format
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: '{:,.0f}'.format(x * 1)))

    # Show the plot using Streamlit
    st.pyplot(plt)

# -------------------------------------------------------------------- #
# -------------------- Visualisasi data pelanggan -------------------- #
# -------------------------------------------------------------------- #

def visualisasi_retensi():
    orders_data = pd.read_csv(Path(__file__).parents[1]/'Datasets/olist_orders_dataset.csv')
    # mengubah tipe data order_purchase_timestamp ke datetime
    orders_data['order_purchase_timestamp'] = pd.to_datetime(orders_data['order_purchase_timestamp'])

    # menggabungkan data order dan order payment
    order_payment_data = order_payments_data.groupby('order_id')['payment_value'].sum().reset_index()
    orders_data = orders_data.merge(order_payment_data, on='order_id', how='left')

    # menghitung Recency, Frequency, and Monetary
    snapshot_date = orders_data['order_purchase_timestamp'].max() + pd.DateOffset(days=1)
    rfm_data = orders_data.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (snapshot_date - x.max()).days,
        'order_id': 'nunique',
        'payment_value': 'sum'
    }).reset_index()

    # merubah nama kolom
    rfm_data.rename(columns={
        'order_purchase_timestamp': 'Recency',
        'order_id': 'Frequency',
        'payment_value': 'Monetary'
    }, inplace=True)

    # menghitung skor RFM
    rfm_data['Recency_Score'] = pd.qcut(rfm_data['Recency'], q=4, labels=[4, 3, 2, 1])
    rfm_data['Frequency_Score'] = pd.qcut(rfm_data['Frequency'], q=4, duplicates='drop')
    rfm_data['Monetary_Score'] = pd.qcut(rfm_data['Monetary'], q=4, labels=[1, 2, 3, 4])

    # membuat strealit chart
    st.subheader('Visualisasi Retensi pelanggan dengan RFM')

    # Display the RFM data
    st.write('RFM Data:')
    st.write(rfm_data.head())

    # Create separate bar plots for Recency and Monetary
    fig, axes = plt.subplots(2, 1, figsize=(10, 12))

    # Recency Plot
    rfm_data['Recency_Score'].value_counts().sort_index().plot(kind='bar', ax=axes[0])
    axes[0].set_title('Recency Analysis')
    axes[0].set_xlabel('Recency Score')
    axes[0].set_ylabel('Count')

    # Monetary Plot
    rfm_data['Monetary_Score'].value_counts().sort_index().plot(kind='bar', ax=axes[1])
    axes[1].set_title('Monetary Analysis')
    axes[1].set_xlabel('Monetary Score')
    axes[1].set_ylabel('Count')

    # Adjust layout
    plt.tight_layout()

    # Display the plots using Streamlit
    st.pyplot(fig)


# menjalankan fungsi visualisasi
st.title('Brazilian E-Commerce Public Dataset Visualization')
visualisasi_tipe_pembayaran()
visualisasi_review()
visualisasi_kota()
visualisasi_produk()
visualisasi_retensi()