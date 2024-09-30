import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import plotly.graph_objects as go
import plotly.express as px
sns.set(style="dark")



def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "total_price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "total_price": "revenue"
    }, inplace=True)
    
    return daily_orders_df


def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_id").total_price.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df


def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bystate_df


def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "total_price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

# Load data
all_df = pd.read_csv("main_data.csv")

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by='order_purchase_timestamp', inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])
    
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Add company logo with some spacing
    st.image("ecommerce.png", use_column_width=True)
    st.markdown("## E-Commerce Dashboard")
    
    # Add horizontal divider
    st.markdown("---")
    
    # Date Range Selector with appropriate labels and style
    st.markdown("### Filter by Date Range")
    start_date, end_date = st.date_input(
        label='Select Date Range:',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    st.markdown("---")
    
    # Add some additional filter options (example: product categories, payment methods)
    st.markdown("### Additional Filters")
    
    # Dropdown for payment types
    payment_type = st.selectbox(
        'Select Payment Type',
        ['All'] + all_df['payment_type'].unique().tolist()
    )

    # Multiselect for product categories
    product_categories = st.multiselect(
        'Select Product Categories',
        all_df['product_category_name'].unique().tolist(),
        default=None
    )
    
    st.markdown("---")
    
    # A button for resetting filters (optional)
    if st.button("Reset Filters"):
        start_date, end_date = min_date, max_date
        payment_type = 'All'
        product_categories = []

    # Option to download data (optional)
    st.markdown("### Download Filtered Data")
    if st.button('Download Data as CSV'):
        st.write("Here you can add logic to download the filtered data.")

# Filter data based on selected date range
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                  (all_df["order_purchase_timestamp"] <= str(end_date))]

# Apply payment type filter if a specific type is selected
if payment_type != 'All':
    main_df = main_df[main_df['payment_type'] == payment_type]

# Apply product category filter if selected
if product_categories:
    main_df = main_df[main_df['product_category_name'].isin(product_categories)]

# Create dataframes
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

# Set colors for the plots
violet = "#8A2BE2"  # Violet
orange = "#FFA500"  # Orange
colors = [violet]  # Using violet for line plots

# Streamlit layout
st.header('Dashboard E-Commerce Public:sparkles:')

st.caption('Copyright (c) Your Company 2023')


from streamlit_option_menu import option_menu

# Sidebar or Navbar Option Menu
selected = option_menu(
    menu_title=None,  # Required
    options=["Overview", "Sales Analysis", "Customers", "Product Performance"],  # Pages
    icons=["house", "bar-chart", "people", "box-seam"],  # Icons
    menu_icon="cast",  # Menu icon
    default_index=0,  # First page selected
    orientation="horizontal"  # Navbar orientation (can also be vertical)
)

# Page Content Logic
if selected == "Overview":
    st.title("Overview")

    # Calculate the average review score
    average_review_score = all_df['review_score'].mean().round(2)

    st.subheader("Average Review Score")

    # Create a gauge chart (speedometer-like)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=average_review_score,
        title={'text': ""},
        gauge={
            'axis': {'range': [0, 5]},  # Assuming review score is between 0 and 5
            'bar': {'color': "orange"},
            'steps': [
                {'range': [0, 2], 'color': "red"},
                {'range': [2, 4], 'color': "yellow"},
                {'range': [4, 5], 'color': "green"}
            ],
        }
    ))

    # Display the plot in Streamlit
    st.plotly_chart(fig)

    # Add descriptive text based on average review score
    if average_review_score >= 4.0:
        st.markdown("**Performance Level:** Great! ⭐️")
    elif average_review_score >= 3.0:
        st.markdown("**Performance Level:** Good! 😊")
    elif average_review_score >= 2.0:
        st.markdown("**Performance Level:** Average! 😐")
    else:
        st.markdown("**Performance Level:** Bad! 😞")
        
elif selected == "Sales Analysis":
    st.title("Sales Analysis")
    
    st.subheader('Daily Orders')

    col1, col2 = st.columns(2)

    with col1:
        total_orders = daily_orders_df.order_count.sum()
        st.metric("Total orders", value=total_orders)

    with col2:
        total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
        st.metric("Total Revenue", value=total_revenue)

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        daily_orders_df["order_purchase_timestamp"],
        daily_orders_df["order_count"],
        marker='o', 
        linewidth=2,
        color=violet
    )
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)

    st.pyplot(fig)
    st.subheader("Average drelivery of goods")

    # Menghitung rata-rata waktu pengiriman per provinsi (state)
    rata_waktu_pengiriman_state = all_df.groupby('customer_state')['waktu_pengiriman'].mean().reset_index()
    rata_waktu_pengiriman_state.columns = ['customer_state', 'rata_waktu_pengiriman']

    rata_waktu_pengiriman_state['rata_waktu_pengiriman'] = rata_waktu_pengiriman_state['rata_waktu_pengiriman'].round(2)

    # Define colors for bars (orange and purple)
    colors = ['orange' if i % 2 == 0 else 'purple' for i in range(len(rata_waktu_pengiriman_state))]

    # Plot untuk rata-rata waktu pengiriman per provinsi
    plt.figure(figsize=(12, 6))
    plt.barh(rata_waktu_pengiriman_state['customer_state'], rata_waktu_pengiriman_state['rata_waktu_pengiriman'], color=colors)
    plt.xlabel('Rata-Rata Waktu Pengiriman (Hari)')
    plt.ylabel('Provinsi')
    plt.title('Rata-Rata Waktu Pengiriman per Provinsi')
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    # Display the plot in Streamlit
    st.pyplot(plt)
    
        
elif selected == "Customers":
    st.title("Customers Insights")
    st.subheader("Customer Demographics by State")

    colors = [violet if i % 2 == 0 else orange for i in range(len(bystate_df))]

    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(
        x="customer_count", 
        y="customer_state",
        data=bystate_df.sort_values(by="customer_count", ascending=False),
        palette=colors,  # Use alternating violet and orange for bars
        ax=ax
    )
    ax.set_title("Number of Customers by State", loc="center", fontsize=30)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)


    st.subheader("Best Customer Based on RFM Parameters")

    col1, col2, col3 = st.columns(3)

    with col1:
        avg_recency = round(rfm_df.recency.mean(), 1)
        st.metric("Average Recency (days)", value=avg_recency)

    with col2:
        avg_frequency = round(rfm_df.frequency.mean(), 2)
        st.metric("Average Frequency", value=avg_frequency)

    with col3:
        avg_monetary = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
        st.metric("Average Monetary", value=avg_monetary)

    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
    colors = [violet] * 5

    sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("customer_id", fontsize=30)
    ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
    ax[0].tick_params(axis='y', labelsize=30)
    ax[0].tick_params(axis='x', labelsize=35)

    sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("customer_id", fontsize=30)
    ax[1].set_title("By Frequency", loc="center", fontsize=50)
    ax[1].tick_params(axis='y', labelsize=30)
    ax[1].tick_params(axis='x', labelsize=35)

    sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel("customer_id", fontsize=30)
    ax[2].set_title("By Monetary", loc="center", fontsize=50)
    ax[2].tick_params(axis='y', labelsize=30)
    ax[2].tick_params(axis='x', labelsize=35)

    st.pyplot(fig)
    
    jumlah_pembayaran = all_df['payment_type'].value_counts().reset_index()
    jumlah_pembayaran.columns = ['payment_type', 'jumlah']

    # Mengurutkan berdasarkan jumlah pembayaran
    jumlah_pembayaran = jumlah_pembayaran.sort_values(by='jumlah', ascending=False)

    # Menambahkan kolom persentase
    jumlah_pembayaran['persentase'] = (jumlah_pembayaran['jumlah'] / jumlah_pembayaran['jumlah'].sum()) * 100

    # Menampilkan hasil di konsol (opsional)
    print("Metode Pembayaran Paling Banyak:")
    print(jumlah_pembayaran)

    # Definisikan palet warna dari violet ke orange
    color_palette = ['#180161', '#4F1787', '#EB3678', '#FB773C']

    # Membuat pie chart menggunakan plotly
    fig = px.pie(jumlah_pembayaran, 
                values='jumlah', 
                names='payment_type', 
                title='Persentase Metode Pembayaran',
                hover_data=['persentase'], 
                labels={'persentase': 'Persentase'},
                hole=0.3,  # Ini akan membuat pie chart menjadi doughnut chart
                color_discrete_sequence=color_palette  # Menetapkan palet warna
                )

    # Tampilkan plot di Streamlit
    st.plotly_chart(fig)
    
elif selected == "Product Performance":
    st.title("Product Performance")
    
    st.subheader("Best & Worst Performing Products")

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

    # Use violet and a lighter color for the bars
    colors = [violet, orange]

    # Best Performing Product
    sns.barplot(x="total_price", y="product_id", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Total Sales", fontsize=30)
    ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
    ax[0].tick_params(axis='y', labelsize=35)
    ax[0].tick_params(axis='x', labelsize=30)

    # Worst Performing Product
    sns.barplot(x="total_price", y="product_id", data=sum_order_items_df.sort_values(by="total_price", ascending=True).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Total Sales", fontsize=30)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
    ax[1].tick_params(axis='y', labelsize=35)
    ax[1].tick_params(axis='x', labelsize=30)

    st.pyplot(fig)
    product_sales = all_df.groupby('product_category_name_english')['order_item_id'].count().reset_index()
    product_sales.columns = ['product_category', 'sales_count']

    # Sort by the number of products sold (descending order)
    product_sales = product_sales.sort_values(by='sales_count', ascending=False)

    # Plot the bar chart using Plotly Express
    fig = px.bar(
        product_sales.head(10),  # Display only the top 10 best-selling categories
        x='product_category',
        y='sales_count',
        color='sales_count',
        color_continuous_scale='Viridis',  # Color scale from violet to orange (you can adjust)
        title='Top 10 Best-Selling Product Categories',
        labels={'product_category': 'Product Category', 'sales_count': 'Number of Sales'},
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig)
            

    
