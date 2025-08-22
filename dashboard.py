from datetime import datetime

import pandas as pd
import streamlit as st

from constants import CSV_FILE
from interfaces.form_response import DOMAIN_HEADERS

# dataset_url = "https://raw.githubusercontent.com/Lexie88rus/bank-marketing-analysis/master/bank.csv"

st.set_page_config(
    page_title="Real-Time Data Science Dashboard",
    page_icon="✅",
    layout="wide",
)


# read csv from a URL
@st.cache_data
def get_data() -> pd.DataFrame:
    # return pd.read_csv(dataset_url)
    return pd.read_csv(CSV_FILE)


# All collated data
df = get_data()


# dashboard title
st.title("CMRA Group Dashboard")

# top-level filters
role_filter = st.selectbox("Role", pd.unique(df["role"]))

start_date_col, end_date_col = st.columns(2)
with start_date_col:
    start_date_range = st.date_input("Start Date")
with end_date_col:
    end_date_range = st.date_input("End Date")

start_time_col, end_time_col = st.columns(2)
with start_time_col:
    start_time_range = st.time_input("Start Time")
with end_time_col:
    end_time_range = st.time_input("End Time")

# Combine date and time into datetime objects
start_datetime = datetime.combine(start_date_range, start_time_range)
end_datetime = datetime.combine(end_date_range, end_time_range)

# creating a single-element container
placeholder = st.empty()

# dataframe filter
# df = df[df["role"] == role_filter]

# print(df)

# == DOMAIN SUMMARY SECTION (Table) ==
df_domain_scores = df.melt(
    id_vars=[col for col in df.columns if col not in DOMAIN_HEADERS],
    value_vars=DOMAIN_HEADERS,
    var_name="domain",
    value_name="domain_score",
)

# Remove any rows with missing scores
df_domain_scores = df_domain_scores.dropna(subset=["domain_score"])

# Now create the domain summary
domain_summary_stats = (
    df_domain_scores.groupby("domain")
    .agg({"domain_score": ["mean", "median"]})
    .round(2)
)

# Flatten column names
domain_summary_stats.columns = ["avg_score", "median_score"]

# # Find top and lowest sub-domains for each domain
# # If you don't have subdomains, you might want to use a different identifier
# # For now, I'll assume you have a 'subdomain' column or use 'role' instead
# if "subdomain" in df_domain_scores.columns:
#     top_subdomains = df_domain_scores.loc[df_domain_scores.groupby("domain")["domain_score"].idxmax()][
#         "subdomain"
#     ]
#     lowest_subdomains = df_domain_scores.loc[df_domain_scores.groupby("domain")["domain_score"].idxmin()][
#         "subdomain"
#     ]
# else:
#     # Use role or another identifier if subdomain doesn't exist
#     top_subdomains = df_melted.loc[df_melted.groupby("domain")["score"].idxmax()][
#         "role"
#     ]
#     lowest_subdomains = df_melted.loc[df_melted.groupby("domain")["score"].idxmin()][
#         "role"
#     ]

# Create the final dataframe
domain_summary = pd.DataFrame(
    {
        "domain": domain_summary_stats.index,
        "average_score": domain_summary_stats["avg_score"],
        "median_score": domain_summary_stats["median_score"],
        # "top_subdomain": top_subdomains.values,
        # "lowest_subdomain": lowest_subdomains.values,
    }
).reset_index(drop=True)

st.markdown("### Domain Summary")
st.dataframe(domain_summary)


# near real-time / live feed simulation
# for seconds in range(200):
#     df["age_new"] = df["age"] * np.random.choice(range(1, 5))
#     df["balance_new"] = df["balance"] * np.random.choice(range(1, 5))

#     # creating KPIs
#     avg_age = np.mean(df["age_new"])

#     count_married = int(
#         df[(df["marital"] == "married")]["marital"].count()
#         + np.random.choice(range(1, 30))
#     )

#     balance = np.mean(df["balance_new"])

#     with placeholder.container():
#         # create three columns
#         kpi1, kpi2, kpi3 = st.columns(3)

#         # fill in those three columns with respective metrics or KPIs
#         kpi1.metric(
#             label="Age ⏳",
#             value=round(avg_age),
#             delta=round(avg_age) - 10,
#         )

#         kpi2.metric(
#             label="Married Count 💍",
#             value=int(count_married),
#             delta=-10 + count_married,
#         )

#         kpi3.metric(
#             label="A/C Balance ＄",
#             value=f"$ {round(balance, 2)} ",
#             delta=-round(balance / count_married) * 100,
#         )

#         # create two columns for charts
#         fig_col1, fig_col2 = st.columns(2)
#         with fig_col1:
#             st.markdown("### First Chart")
#             fig = px.density_heatmap(data_frame=df, y="age_new", x="marital")
#             st.write(fig)

#         with fig_col2:
#             st.markdown("### Second Chart")
#             fig2 = px.histogram(data_frame=df, x="age_new")
#             st.write(fig2)

#         st.markdown("### Detailed Data View")
#         st.dataframe(df)
#         time.sleep(1)
#         st.rerun()
