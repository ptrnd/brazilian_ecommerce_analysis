import streamlit as st
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from pathlib import Path

# Baca data pelanggan, pesanan, dan pembayaran
customer_data = pd.read_csv('./../Datasets/olist_customers_dataset.csv')
geo_data = pd.read_csv('./../Datasets/olist_geolocation_dataset.csv')
order_items_data = pd.read_csv('./../Datasets/olist_order_items_dataset.csv')
order_payments_data = pd.read_csv('../Datasets/olist_order_payments_dataset.csv')
order_reviews_data = pd.read_csv('../Datasets/olist_order_reviews_dataset.csv')
orders_data = pd.read_csv('../Datasets/olist_orders_dataset.csv')
products_data = pd.read_csv('../Datasets/olist_products_dataset.csv')
sellers_data = pd.read_csv('../Datasets/olist_sellers_dataset.csv')
product_category_data = pd.read_csv('../Datasets/product_category_name_translation.csv')

# Konversi kolom order_purchase_timestamp ke format datetime
orders_data['order_purchase_timestamp'] = pd.to_datetime(orders_data['order_purchase_timestamp'])

# Gabungkan data pesanan dan pembayaran
order_payment_data = order_payments_data.groupby('order_id')['payment_value'].sum().reset_index()
orders_data = orders_data.merge(order_payment_data, on='order_id', how='left')

# Hitung Recency, Frequency, dan Monetary
snapshot_date = orders_data['order_purchase_timestamp'].max() + pd.DateOffset(days=1)
rfm_data = orders_data.groupby('customer_id').agg({
    'order_purchase_timestamp': lambda x: (snapshot_date - x.max()).days,
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

# Tampilkan histogram untuk Recency
st.subheader('Distribution of Recency')
plt.hist(rfm_data['Recency'], bins=30, color='skyblue', edgecolor='black')
plt.xlabel('Recency (days)')
plt.ylabel('Count')
st.pyplot(plt)

# Tampilkan histogram untuk Frequency
st.subheader('Distribution of Frequency')
plt.hist(rfm_data['Frequency'], bins=30, color='lightcoral', edgecolor='black')
plt.xlabel('Frequency (number of orders)')
plt.ylabel('Count')
st.pyplot(plt)

# Tampilkan histogram untuk Monetary
st.subheader('Distribution of Monetary')
plt.hist(rfm_data['Monetary'], bins=30, color='lightgreen', edgecolor='black')
plt.xlabel('Monetary (total payment value)')
plt.ylabel('Count')
st.pyplot(plt)