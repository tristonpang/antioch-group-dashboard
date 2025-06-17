import time

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

dataset_url = "https://raw.githubusercontent.com/Lexie88rus/bank-marketing-analysis/master/bank.csv"

st.set_page_config(
    page_title="Real-Time Data Science Dashboard",
    page_icon="✅",
    layout="wide",
)

# read csv from a URL
@st.cache_data
def get_data() -> pd.DataFrame:
    return pd.read_csv(dataset_url)

df = get_data()


# dashboard title
st.title("Real-Time / Live Data Science Dashboard")

# top-level filters
job_filter = st.selectbox("Select the Job", pd.unique(df["job"]))

# dataframe filter
df = df[df["job"] == job_filter]

# create three columns
kpi1, kpi2, kpi3 = st.columns(3)

# creating KPIs 
avg_age = np.mean(df['age']) 

count_married = int(df[(df["marital"]=='married')]['marital'].count() + np.random.choice(range(1,30)))
  
balance = np.mean(df['balance'])

# fill in those three columns with respective metrics or KPIs
kpi1.metric(
    label="Age ⏳",
    value=round(avg_age),
    delta=round(avg_age) - 10,
)

kpi2.metric(
    label="Married Count 💍",
    value=int(count_married),
    delta=-10 + count_married,
)

kpi3.metric(
    label="A/C Balance ＄",
    value=f"$ {round(balance,2)} ",
    delta=-round(balance / count_married) * 100,
)

# create two columns for charts
fig_col1, fig_col2 = st.columns(2)

with fig_col1:
    st.markdown("### First Chart")
    fig = px.density_heatmap(
        data_frame=df, y="age", x="marital"
    )
    st.write(fig)
   
with fig_col2:
    st.markdown("### Second Chart")
    fig2 = px.histogram(data_frame=df, x="age")
    st.write(fig2)

st.markdown("### Detailed Data View")
st.dataframe(df)