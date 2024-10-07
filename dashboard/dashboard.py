import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from datetime import datetime

dataset_link = "https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/data?select=olist_customers_dataset.csv"
data_path = "./data/cleaned/"

def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

# CSS Matric Style
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: rgba(28, 131, 225, 0.1);
        border: 1px solid rgba(28, 131, 225, 0.1);
        padding: 5% 5% 5% 10%;
        border-radius: 5px;
        color: rgb(30, 103, 119);
        overflow-wrap: break-word;
    }

    /* breakline for metric text */
    div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
        overflow-wrap: break-word;
        white-space: break-spaces;
        color: red;
    }
    </style>
    """, unsafe_allow_html=True)



# Page
st.sidebar.markdown("<h1 style='font-size: 70px; font-weight: 3xl;'>🛒</h1>", unsafe_allow_html=True)

st.sidebar.markdown("<h1 style='font-size: 30px; font-weight: 5xl;'>Brazilian E-Commerce Sales Diversification and Regional Marketing Improvement Analysis</h1>", unsafe_allow_html=True)

st.sidebar.markdown("""
         <p style='font-size: 10px'; align:'bottom'>
         This project is made by utilizing the Brazilian E-Commerce Public Dataset by Olist (+ Marketing Funnel by Olist) <a href='%s'>link</a>.
         <br><br>
         The main purpose of this analysis is to:
         <ul>
            <li style='font-size: 10px;'>Escalate diversification of purchases by knowing what kind of potential product segments need to be boosted.</li>
            <li style='font-size: 10px;'>Increase sales quantity in potential untapped customer regions by identifying the most promising regions for sales.</li>
         </ul>
         </p>
""" % dataset_link, unsafe_allow_html=True)

for i in range(5): st.sidebar.write("")

page = st.sidebar.selectbox("Select a page", ["Product Analysis", "Regional Analysis"])

# Product Analysis page
if page == "Product Analysis":
    # Title
    st.title("📦   Product Analysis")

    tab1, tab2 = st.tabs(["Purchase History", "Categorical Sales Quantity"])

    with tab1:
        col1, spacer, col2 = st.columns([1, 0.2, 4])

        # Data
        sales = pd.read_csv(data_path+"sales_df.csv")
        sales['order_purchase_timestamp'] = pd.to_datetime(sales['order_purchase_timestamp'])

        min_date = sales['order_purchase_timestamp'].min()
        max_date = sales['order_purchase_timestamp'].max()

        # Widget Column
        start_date, end_date = col1.date_input(
            "Date Range", 
            [min_date, max_date], 
            min_value=min_date, 
            max_value=max_date
        )

        filtered_sales = sales[
            (sales['order_purchase_timestamp'] >= pd.to_datetime(start_date)) &
            (sales['order_purchase_timestamp'] <= pd.to_datetime(end_date))
        ]

        for i in range(5): col1.write("")

        # Total Payment Widget
        total_payment_yesterday = filtered_sales['payment_value'].sum() - filtered_sales[filtered_sales['order_purchase_timestamp'] == pd.to_datetime(end_date)]['payment_value'].sum()
        total_payment = filtered_sales['payment_value'].sum()
        col1.metric("Total Payment", f"${format_number(total_payment)}", delta=format_number(total_payment-total_payment_yesterday))

        # Average Payment Widget
        average_payment = filtered_sales['payment_value'].mean()
        average_payment_yesterday = 1
        increase = 0
        if type(filtered_sales[filtered_sales['order_purchase_timestamp'] == pd.to_datetime(end_date)]['payment_value'].mean()) == float:
            average_payment_yesterday = filtered_sales[filtered_sales['order_purchase_timestamp'] == pd.to_datetime(end_date)]['payment_value'].mean()
            increase = (average_payment-average_payment_yesterday)/average_payment_yesterday
        col1.metric("Average Payment", f"${average_payment:,.2f}", delta=f"{increase:.2f}%")

        # Daily Based Payment Chart
        col2.subheader("Daily Payment Average")
        daily_df = pd.read_csv(data_path+"daily_average_payment.csv")
        daily_df['order_purchase_timestamp'] = pd.to_datetime(daily_df['order_purchase_timestamp'])
        col2.line_chart(data=daily_df, x='order_purchase_timestamp', y='payment_value')

    with tab2:
        # Data
        cat_sales = pd.read_csv(data_path+"category_sales.csv")
        cat_sales.columns = ['category name','total sales','unit price','total income']

        average_sales_categorical = cat_sales['total sales'].mean()
        col1, spacer, col2 = st.columns([2, 0.5, 5])

        # Column 1

        # Average sales
        col1.metric("Average Categorical Sales", f"{average_sales_categorical:.2f}")

        # Top 6 Potential Product
        under_average_category = pd.read_csv(data_path+"under_average_category.csv")
        under_average_category['order_purchase_timestamp'] = pd.to_datetime(under_average_category['order_purchase_timestamp'])

        top6_list_raw = under_average_category['product_category_name'].unique()
        top6_list = ['All Categories']
        for i in range(6):
            top6_list.append(top6_list_raw[i])

        col1.markdown("<h1 style='font-size: 20px; font-weight: 3xl;'>Top 6 Potential Category</h1>", unsafe_allow_html=True)
        col1.write("")            
        graph = col1.radio(
            " ",
            top6_list,
            index=0,
        )

        # Column 2
        if graph == top6_list[0]:
            # Create a chart (for example, a bar chart)
            fig = px.bar(
                            cat_sales.sort_values(by='total sales'),
                            x='category name',
                            y='total sales',
                            title=f"Total Purchases Each Categories",
                            labels={'category name': 'Category Name','total sales': 'Total Sales'},
                            template='plotly_white'
                            )
                            
        else:
            default = False
            category_data = under_average_category[under_average_category['product_category_name'] == graph]
            daily_sales = category_data.groupby('order_purchase_timestamp').agg({'order_quantity': 'sum'}).reset_index()

            # Create a chart (for example, a bar chart)
            fig = px.line(
                            daily_sales,
                            x='order_purchase_timestamp',
                            y='order_quantity',
                            title=f"Total Purchases Over Time for {graph}",
                            labels={'order_purchase_timestamp': 'Purchase Date', 'order_quantity': 'Order Quantity'},
                            template='plotly_white'
                            )
        
        col2.plotly_chart(fig)

        


# Regional Analysis Tab
elif page == "Regional Analysis":
    st.title("🗺️   Regional Analysis")

    st.subheader('Total Customers and Expected Customers by Region')

    # Data
    melted_data = pd.read_csv(data_path+"melter_region.csv")

    fig = px.bar(melted_data, 
                x='geolocation_state', 
                y='value', 
                color='customer_type',
                barmode='group', 
                labels={'value': 'Number of Customers'},
                title='Total Customers and Expected Customers by Region',
                )

    fig.update_layout(
        xaxis_title='Geolocation State',
        yaxis_title='Number of Customers',
        legend_title='Customer Type',
        xaxis_tickangle=-45 
    )

    st.plotly_chart(fig, use_container_width=True)