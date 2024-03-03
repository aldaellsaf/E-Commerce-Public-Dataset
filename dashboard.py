import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime as dt
from babel.numbers import format_currency

sns.set(style='dark')

# Load data
pelanggan = pd.read_csv("dataset/olist_customers_dataset.csv")
items = pd.read_csv("dataset/olist_order_items_dataset.csv")
pesanan = pd.read_csv("dataset/olist_orders_dataset.csv")
pembayaran = pd.read_csv("dataset/olist_order_payments_dataset.csv")
produk = pd.read_csv("dataset/olist_products_dataset.csv")
sellers = pd.read_csv("dataset/olist_sellers_dataset.csv")
kategori_produk = pd.read_csv("dataset/product_category_name_translation.csv")
geolocation = pd.read_csv("dataset/olist_geolocation_dataset.csv")
order_items = pd.read_csv("dataset/order_items.csv")
orders = pd.read_csv("dashboard/orders.csv")
customer_seller = pd.read_csv("dataset/customer_seller.csv")

all_data = pd.read_csv("dashboard/orders.csv")
datetime_columns = ["order_delivered_customer_date", "order_delivered_carrier_date"]
all_data.sort_values(by="order_delivered_customer_date", inplace=True)
all_data.reset_index(inplace=True)
 
for column in datetime_columns:
    all_data[column] = pd.to_datetime(all_data[column])

# Create sidebar
with st.sidebar:
    # Add image
    st.image("https://brazilian.report/wp-content/uploads/2023/10/TBR-PHOTOS-79.png")

st.sidebar.title("E-Commerce Dashboard")
st.sidebar.markdown("Dashboard ini menampilkan beberapa insight dari Brazilian E-Commerce dataset.")
st.sidebar.write("Proyek Analisis Data by Alda Ellsa Faradilla")

# Display the title and description
st.title(":sparkles: E-Commerce Data Analysis Dashboard :sparkles:")

st.header('Pertanyaan Bisnis')
tab1, tab2, tab3, tab4 = st.tabs(["Pertanyaan 1", "Pertanyaan 2", "Pertanyaan 3", "Pertanyaan 4"])
 
with tab1:
    st.subheader("Kemana tujuan pengiriman paket yang memiliki waktu pengiriman terlama?")
    
    st.write("Visualisasi")
    # Data Wrangling
    geolocation = geolocation.drop(columns=["geolocation_city", "geolocation_state"])
    geolocation = geolocation.drop_duplicates(subset=["geolocation_zip_code_prefix"])

    # Menggabungkan Data Produk dengan Data Kategori Produk Translation
    product = produk.merge(kategori_produk, left_on="product_category_name", right_on="product_category_name",how="left")
    df_produk = product[["product_id","product_category_name_english","product_category_name"]]

    # Menggabungkan Data Items dengan Data Produk menjadi Data Order Items
    order_items = items.drop(columns = ["shipping_limit_date"])
    order_items = items.merge(df_produk, left_on="product_id", right_on="product_id",how="left")

    # Menggabungkan Data Items dengan Seller
    order_items = order_items.merge(sellers, left_on="seller_id", right_on="seller_id",how="left")

    # Menggabungkan Order Items dengan Geolocation
    order_items = order_items.merge(geolocation, left_on="seller_zip_code_prefix", right_on="geolocation_zip_code_prefix",how="left", validate = "m:1")

    # Menggabungkan Pesanan dengan Pembayaran
    payments = pembayaran.drop(columns = ["payment_sequential","payment_installments"])
    orders = pesanan.merge(payments, left_on="order_id", right_on="order_id",how="left")

    # Menggabungkan Pesanan dengan Pelanggan
    customer = pelanggan.drop(columns = [])
    orders = orders.merge(customer, left_on="customer_id", right_on="customer_id",how="left")

    # Menggabungkan Pelanggan dengan Geolocation
    orders = orders.merge(geolocation, left_on="customer_zip_code_prefix", right_on="geolocation_zip_code_prefix",how="left")

    # Mengonversi kolom tanggal menjadi datetime
    orders["order_delivered_customer_date"] = pd.to_datetime(orders["order_delivered_customer_date"])
    orders["order_delivered_carrier_date"] = pd.to_datetime(orders["order_delivered_carrier_date"])
    orders["hari_pengiriman"] = (orders["order_delivered_customer_date"] - orders["order_delivered_carrier_date"]).dt.days

    # Visualization
    # Menggabungkan Pelanggan dengan Seller
    customer = orders[["customer_city","customer_state","hari_pengiriman","order_id","customer_id","customer_zip_code_prefix","geolocation_lat","geolocation_lng"]]
    seller = order_items[["order_id","seller_id","seller_city","seller_state","seller_zip_code_prefix","freight_value","geolocation_lat","geolocation_lng"]]
    customer_seller = customer.merge(seller, left_on="order_id", right_on="order_id",how="left")
    customer_seller.rename(columns = {"geolocation_lat_x":"geolocation_lat_cust", "geolocation_lat_y":"geolocation_lat_seller", "geolocation_lng_x":"geolocation_lng_cust","geolocation_lng_y":"geolocation_lng_seller"}, inplace = True)

    pengiriman = customer_seller.groupby(["seller_city", "customer_city"])["hari_pengiriman"].max()
    pengiriman = pengiriman.sort_values(ascending=False).head(5).reset_index()
    pengiriman

    st.subheader("Conclution")
    st.write("Dengan ditampilkannya tabel yang berisi dengan tiga kolom yaitu kolom kota penjual, kolom kota pelanggan, dan kolom hari pengiriman. Ditampilkan lima data dengan waktu pengiriman yang bervariasi antara 188 hari hingga 205 hari. Sehingga kota tujuan dalam pengiriman paket yang memiliki waktu pengiriman terlama adalah Kota Rio de Janeiro dengan lama pengiriman yaitu 205 hari.")
 
with tab2:
    st.header("Pertanyaan 2 : Kategori produk apa yang menghasilkan pendapatan tertinggi?")
    
    st.write("Visualisasi Grafik Batang")
    pendapatan = order_items.groupby("product_category_name_english")["price"].sum().sort_values(ascending=False).reset_index()
    pendapatan = pendapatan.rename(columns={"product_category_name_english": "category", "price": "price"})


    plt.figure(figsize=(24, 6))
    colors = ["#164863", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(x="price", y="category", data = pendapatan.sort_values(by="price", ascending=False).head(5), palette=colors)
    plt.ylabel("Kategori Produk", fontsize = 14)
    plt.xlabel("Total Pendapatan (USD)", fontsize = 14)
    plt.title("Kategori Produk dengan Pendapatan Tertinggi", loc="center", fontsize=18)
    st.pyplot(plt)

    max_price = pendapatan["price"].max()
    st.write("Total pendapatan tertinggi sebesar:", max_price)

    st.subheader("Conclution")
    st.write("Grafik batang yang ditampilkan berisi tentang membandingkan pendapatan total dalam USD dari lima kategori produk yang berbeda yaitu kategori health_beauty, watches_gifts, bed_bath_table, sports_leisure, dan computers_accessories. Dari grafik batang tersebut didapatkan bahwa kategori produk health_beauty memiliki pendapatan tertinggi dari semua kategori yang ditampilkan dengan total pendapatan sebesar 1.258.681,34 USD.")
 
with tab3:
    st.header("Pertanyaan 3 : Kota manakah yang menghasilkan pendapatan paling tinggi?")
    
    st.write("Visualisasi Grafik Batang")
    pendapatan_kota = orders.groupby("customer_city")["payment_value"].sum().reset_index().sort_values("payment_value", ascending = False).head(5)

    plt.figure(figsize=(24, 6))
    colors = ["#164863", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(x = "payment_value", y = "customer_city", data = pendapatan_kota, palette = colors)

    plt.xlabel("Total Pendapatan (USD)")
    plt.ylabel("Kota")
    plt.title("Kota yang Menghasilkan Pendapatan Tertinggi")
    st.pyplot(plt)

    st.subheader("Conclution")
    st.write("Grafik batang yang ditampilkan berisi tentang perbandingan pendapatan antara beberapa kota yang ada di Brasil. Terdapat lima kota yang ditampilkan dalam grafik tersebut yaitu Kota Sao Paulo, Kota Rio de Janeiro, Kota Belo Horizonte, Kota Brasilia, dan Kota Curitiba. Dari visualisasi grafik batang tersebut diperoleh bahwa Kota Sao Paulo menjadi kota yang menghasilkan pendapatan tertinggi.")

with tab4:
    st.header("Pertanyaan 4 : Bagaimana pengelompokkan pelanggan berdasarkan keterkinian pembelian terakhir, frekuensi pembelian, dan jumlah total yang dibelanjakan?")
    
    st.write("Visualisasi")
    # Menggabungkan Items denggan Harga
    harga = items.drop(columns = ["order_item_id","product_id",	"seller_id", "shipping_limit_date"])
    orders = orders.merge(harga, left_on ="order_id", right_on= "order_id",how="left")

    # Recency = pembelian terakhir
    orders["order_approved_at"] = pd.to_datetime(orders["order_approved_at"])
    now = orders["order_approved_at"].max() + pd.Timedelta(days=1)
    recency = orders.groupby("customer_id")["order_approved_at"].max().reset_index()
    recency.columns = ["customer_id", "LastPurchaseDate"]
    recency["Recency"] = (now - recency["LastPurchaseDate"]).dt.days

    # Frequency = jumlah pembelian
    frequency = orders.groupby("customer_id")["order_id"].count().reset_index()
    frequency.columns = ["customer_id", "Frequency"]
    frequency["customer_id"] = frequency["customer_id"].astype(object)

    # Monetary = total uang yang dikeluarkan
    monetary = orders.groupby("customer_id")["price"].sum().reset_index()
    monetary.columns = ["customer_id", "Monetary"]

    # Gabungan dataframe RFM
    rfm = pd.merge(recency, frequency, on="customer_id")
    rfm = pd.merge(rfm, monetary, on="customer_id")
    st.write(rfm.head())
    st.write(rfm.describe())

    st.write("Visualisasi Histogram")
    # Membuat Visualisasi
    st.text("Pengelompokkan Pelanggan dengan RFM Parameters (customer_id)")

    # Membuat histogram kolom Recency
    plt.figure()
    plt.hist(rfm["Recency"], bins=10, edgecolor="black", linewidth=1)
    plt.xlabel("Recency (lama belanja)")
    plt.ylabel("Jumlah")
    plt.title("Histogram dari Recency")
    st.pyplot(plt)

    # Membuat histogram kolom Frequency
    plt.figure()
    plt.hist(rfm["Frequency"], bins=10, edgecolor="black", linewidth=1)
    plt.xlabel("Frequency (orders)")
    plt.ylabel("Jumlah")
    plt.title("Histogram dari Frequency")
    st.pyplot(plt)

    # Membuat histogram kolom Monetary
    plt.figure()
    plt.hist(rfm["Monetary"], bins=10, edgecolor="black", linewidth=1)
    plt.xlabel("Monetary (pengeluaran)")
    plt.ylabel("Jumlah")
    plt.title("Histogram dari Monetary")
    st.pyplot(plt)

    st.subheader("Conclution")
    st.write("Berdasarkan visualisasi grafik batang yang ditampilkan, pengelompokkan pelanggan berdasarkan parameter RFM(Recency, Frequency, Monetary) didapatkan bahwa:")
    list = ["Histogram recency menunjukkan bahwa sebagian besar pelanggan memiliki nilai recency yang rendah, artinya pelanggan sudah lama tidak berbelanja.", 
            "Histogram frequency menunjukkan bahwa hampir semua pelanggan memiliki frekuensi pembelian yang sangat rendah, artinya pelanggan jarang berbelanja.",
            "Histogram monetary menunjukkan bahwa sebagian besar pelanggan memiliki nilai monetary yang rendah, artinya pelanggan menghabiskan sedikit uang untuk berbelanja."]

    md = "\n".join([f"{i+1}. {x}" for i, x in enumerate(list)])
    st.markdown(md)
