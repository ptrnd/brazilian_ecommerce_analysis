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
geo_data = pd.read_csv(Path(__file__).parents[1]/'Datasets/olist_geolocation_dataset.csv')
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

# visualisasi
st.title('Brazilian E-Commerce Public Dataset Visualization')

# ---------------------------------------------------------------------- #
# -------------------- Visualisasi Review pelanggan -------------------- #
# ---------------------------------------------------------------------- #

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
    st.title('Rata-rata Review Pelanggan Secara Keseluruhan')
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

    # Menampilkan rata-rata keseluruhan
    st.write(f'Rata-rata keseluruhan: {overall_mean:.2f}')

# ...

# -------------------------------------------------------------------- #
# -------------------- Visualisasi data pelanggan -------------------- #
# -------------------------------------------------------------------- #

def visualisasi_perilaku():
    # Membaca data pesanan kembali di dalam fungsi
    orders_data = pd.read_csv(Path(__file__).parents[1] / 'Datasets/olist_orders_dataset.csv')

    # Gabungkan data pesanan dan pembayaran
    order_payment_data = order_payments_data.groupby('order_id')['payment_value'].sum().reset_index()
    orders_data = orders_data.merge(order_payment_data, on='order_id', how='left')

    # Hitung Recency, Frequency, dan Monetary
    snapshot_date = orders_data['order_purchase_timestamp'].max() + pd.to_timedelta('1 day')  # Menggunakan pd.to_timedelta
    rfm_data = orders_data.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (snapshot_date - pd.to_datetime(x.max())).dt.days,
        'order_id': 'nunique',
        'payment_value': 'sum'
    }).reset_index()

    # Ubah nama kolom
    rfm_data.rename(columns={
        'order_purchase_timestamp': 'Recency',
        'order_id': 'Frequency',
        'payment_value': 'Monetary'
    }, inplace=True)

    # Visualisasi data RFM
    st.title('RFM Analysis Dashboard')

    # Menggunakan st.beta_columns untuk menyusun visualisasi
    col1, col2, col3 = st.columns(3)

    # Visualisasi Recency
    col1.subheader('Distribution of Recency')
    plt.hist(rfm_data['Recency'], bins=30, color='skyblue', edgecolor='black')
    plt.xlabel('Recency (days)')
    plt.ylabel('Count')
    plt.xticks(rotation=45)  # Menambahkan rotasi pada label x
    col1.pyplot(plt)

    # Visualisasi Frequency
    col2.subheader('Distribution of Frequency')
    plt.hist(rfm_data['Frequency'], bins=30, color='lightcoral', edgecolor='black')
    plt.xlabel('Frequency (number of orders)')
    plt.ylabel('Count')
    plt.xticks(rotation=45)  # Menambahkan rotasi pada label x
    col2.pyplot(plt)

    # Visualisasi Monetary
    col3.subheader('Distribution of Monetary')
    plt.hist(rfm_data['Monetary'], bins=30, color='lightgreen', edgecolor='black')
    plt.xlabel('Monetary (total payment value)')
    plt.ylabel('Count')
    plt.xticks(rotation=45)  # Menambahkan rotasi pada label x
    col3.pyplot(plt)

# menjalankan fungsi visualisasi
visualisasi_review()
visualisasi_perilaku()