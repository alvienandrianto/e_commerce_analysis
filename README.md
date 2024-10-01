# Ecommerce Dashboard

This project is an ecommerce dashboard built with **Streamlit**, **Pandas**, and **Seaborn** for data visualization. It allows users to explore ecommerce data, visualize daily orders, customer demographics, best and worst performing products, and analyze customer behavior using RFM (Recency, Frequency, Monetary) metrics.

## Business Question
- Berapa jumlah pesanan pelanggan dalam tahun tertentu?
- Bagaimana pola pembelian pelanggan berdasarkan lokasi atau wilayah?
- Apakah ada pelanggan yang lebih cenderung melakukan pembelian pada kategori produk tertentu?
- Produk apa yang memiliki penjualan tertinggi dan terendah dalam periode waktu tertentu?
- Kategori produk mana yang menyumbang pendapatan terbesar?
- Apakah ada perbedaan waktu pengiriman berdasarkan wilayah geografis?
- Siapa penjual dengan performa terbaik dan terburuk berdasarkan penjualan dan ulasan?
- Pembayaran dengan metode apa yang paling banyak?

## Features
- Daily Orders Visualization
- Revenue and Order Count Summary
- Best and Worst Performing Products
- Customer Demographics (by gender, age, state)
- RFM Analysis (Recency, Frequency, and Monetary metrics)

## Prerequisites

Before you begin, ensure you have the following installed:
- **Python** (version 3.7 or later)
- **pip** (Python package installer)

You will also need to install the following Python libraries:
```bash

git clone https://github.com/alvienandrianto/e_commerce_analysis.git

cd e_commerce_analysis

pip install -r requirements.txt 

cd dashboard

streamlit run dashboard.py