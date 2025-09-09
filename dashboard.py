from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from constants import ALL_ROLES_OPTION, CSV_FILE, EMPTY_ROLE_OPTION
from interfaces.form_response import DISPLAY_NAMES, DOMAIN_HEADERS
from typeform_api import fetch_typeform_responses

# dataset_url = "https://raw.githubusercontent.com/Lexie88rus/bank-marketing-analysis/master/bank.csv"

st.set_page_config(
    page_title="CMRA Group Dashboard",
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

# == IMPORT SECTION ==
st.markdown("### Import Cohort Data (CSV)")
uploaded_file = st.file_uploader(
    "Upload a CSV file to use as the current cohort (optional):",
    type=["csv"],
    key="import_csv",
)
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("CSV file successfully imported and loaded as current cohort!")

# == FILTERS SECTION ==
all_filters_disabled = uploaded_file is not None
role_options = [ALL_ROLES_OPTION, EMPTY_ROLE_OPTION] + list(
    pd.unique(df["role"].dropna())
)
role_filter = st.selectbox("Role", role_options, disabled=all_filters_disabled)

realtime_data_col, combine_live_with_historical_col = st.columns(2)
with realtime_data_col:
    enable_realtime_data = st.toggle(
        "Enable Real-time Data", value=False, disabled=all_filters_disabled
    )
with combine_live_with_historical_col:
    combine_live = st.toggle(
        "Combine with historical data",
        value=False,
        disabled=all_filters_disabled or not enable_realtime_data,
    )

end_range_disabled = all_filters_disabled or enable_realtime_data
start_range_disabled = all_filters_disabled or (
    enable_realtime_data and not combine_live
)
start_date_col, end_date_col = st.columns(2)
with start_date_col:
    start_date_range = st.date_input("Start Date", disabled=start_range_disabled)
with end_date_col:
    end_date_range = st.date_input("End Date", disabled=end_range_disabled)

start_time_col, end_time_col = st.columns(2)
with start_time_col:
    start_time_range = st.time_input("Start Time", disabled=start_range_disabled)
with end_time_col:
    end_time_range = st.time_input("End Time", disabled=end_range_disabled)

# Combine date and time into datetime objects
start_datetime = datetime.combine(start_date_range, start_time_range)
end_datetime = datetime.combine(end_date_range, end_time_range)

if "last_fetched_range" not in st.session_state:
    st.session_state["last_fetched_range"] = (None, None)

last_start, last_end = st.session_state["last_fetched_range"]

if (start_datetime != last_start) or (end_datetime != last_end):
    with st.spinner("Fetching data from Typeform..."):
        fetch_typeform_responses(start_datetime, end_datetime)
        df = get_data()
    st.session_state["last_fetched_range"] = (start_datetime, end_datetime)


df["submitted_at"] = pd.to_datetime(df["submitted_at"])
# Convert timezone-aware datetime to timezone-naive for comparison
df["submitted_at"] = df["submitted_at"].dt.tz_localize(None)

# creating a single-element container
placeholder = st.empty()

# Apply dataframe filters
if role_filter == EMPTY_ROLE_OPTION:
    df = df[df["role"].isna() | (df["role"] == "")]
elif role_filter != ALL_ROLES_OPTION:
    df = df[df["role"] == role_filter]

# Apply datetime range
df = df[(df["submitted_at"] >= start_datetime) & (df["submitted_at"] <= end_datetime)]
st.info(str(df.shape[0]) + " responses from Typeform for the selected date/time range.")


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

# Define subdomain mappings for each domain
subdomain_mapping = {
    "discipleship": ["education", "training"],
    "sending": ["sending1", "membercare"],
    "support": ["praying", "giving", "community"],
    "structure": ["organisation", "policies", "partnerships"],
}

# Calculate top and lowest subdomains for each domain
top_subdomains = []
lowest_subdomains = []

for domain in domain_summary_stats.index:
    subdomains = subdomain_mapping[domain]

    # Calculate mean scores for each subdomain in this domain
    subdomain_means = df[subdomains].mean()

    # Find top and lowest subdomain
    top_subdomain = subdomain_means.idxmax()
    lowest_subdomain = subdomain_means.idxmin()

    top_subdomains.append(DISPLAY_NAMES[top_subdomain])
    lowest_subdomains.append(DISPLAY_NAMES[lowest_subdomain])

# Create the final dataframe
domain_summary = pd.DataFrame(
    {
        "Domain": [DISPLAY_NAMES[domain] for domain in domain_summary_stats.index],
        "Average Score": domain_summary_stats["avg_score"],
        "Median Score": domain_summary_stats["median_score"],
        "Top Subdomain": top_subdomains,
        "Lowest Subdomain": lowest_subdomains,
    }
).reset_index(drop=True)

st.markdown("### Domain Summary")
st.dataframe(domain_summary, use_container_width=True, hide_index=True)


st.markdown("### Visualization Panel")
# == RADAR CHART SECTION ==
# Create radar chart data
radar_data = domain_summary_stats.reset_index()
radar_data["domain_display"] = [
    DISPLAY_NAMES[domain] for domain in radar_data["domain"]
]

domain_radar = go.Figure()

domain_radar.add_trace(
    go.Scatterpolar(
        r=radar_data["avg_score"],
        theta=radar_data["domain_display"],
        fill="toself",
        name="Average Score",
        line_color="rgb(32, 201, 151)",
        fillcolor="rgba(32, 201, 151, 0.2)",
    )
)

domain_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100],  # Assuming scores are 0-100
        ),
        angularaxis=dict(
            tickfont=dict(size=24),  # <-- Angular axis tick font size
        ),
    ),
    showlegend=True,
    title="Domain Average Scores",
    height=500,
    font=dict(size=18),
    hoverlabel=dict(font_size=18),
)


# == SUBDOMAIN BAR CHART SECTION ==
# Create subdomain data with domain prefixes for clearer grouping
subdomain_data = []

for domain, subdomains in subdomain_mapping.items():
    for subdomain in subdomains:
        avg_score = df[subdomain].mean()
        subdomain_data.append(
            {
                "domain": DISPLAY_NAMES[domain],
                "subdomain": DISPLAY_NAMES[subdomain],
                "subdomain_full": f"{DISPLAY_NAMES[domain]}: {DISPLAY_NAMES[subdomain]}",
                "avg_score": round(avg_score, 2),
            }
        )

subdomain_df = pd.DataFrame(subdomain_data)

# Create single bar chart with color coding by domain
subdomain_bar = go.Figure()

domains = subdomain_df["domain"].unique()
colors = [
    "rgb(32, 201, 151)",
    "rgb(255, 99, 71)",
    "rgb(54, 162, 235)",
    "rgb(255, 206, 86)",
]
color_map = {domain: colors[i % len(colors)] for i, domain in enumerate(domains)}

subdomain_bar.add_trace(
    go.Bar(
        x=subdomain_df["subdomain_full"],
        y=subdomain_df["avg_score"],
        marker_color=[color_map[domain] for domain in subdomain_df["domain"]],
        text=subdomain_df["avg_score"],
        textposition="auto",
        showlegend=False,
    )
)

subdomain_bar.update_layout(
    title="Average Scores by Subdomain",
    xaxis_title="Subdomains",
    yaxis_title="Average Score",
    height=500,
    xaxis={"tickangle": 45, "title_font": {"size": 20}, "tickfont": {"size": 14}},
    yaxis={
        "title_font": {"size": 20},
        "tickfont": {"size": 18},
    },
    font=dict(size=18),
    hoverlabel=dict(font_size=18),
)

domain_radar_col, subdomain_bar_col = st.columns(2)
with domain_radar_col:
    st.plotly_chart(domain_radar, use_container_width=True)
with subdomain_bar_col:
    st.plotly_chart(subdomain_bar, use_container_width=True)

# == SUBDOMAIN HEATMAP SECTION ==
# Prepare data for heatmap
heatmap_data = []
domain_labels = []
subdomain_labels = []

for domain, subdomains in subdomain_mapping.items():
    for subdomain in subdomains:
        avg_score = df[subdomain].mean()
        heatmap_data.append([round(avg_score, 2)])
        domain_labels.append(DISPLAY_NAMES[domain])
        subdomain_labels.append(DISPLAY_NAMES[subdomain])

# Create heatmap
heatmap_fig = go.Figure(
    data=go.Heatmap(
        z=heatmap_data,
        x=["Average Score"],
        y=[
            f"{domain}: {subdomain}"
            for domain, subdomain in zip(domain_labels, subdomain_labels)
        ],
        # colorscale="RdYlGn",
        autocolorscale=True,
        text=heatmap_data,
        texttemplate="%{text}",
        textfont={"size": 18},
        colorbar=dict(title="Score"),
        hoverongaps=False,
    )
)

heatmap_fig.update_layout(
    title="Subdomain Average Scores Heatmap",
    height=600,
    yaxis={
        "autorange": "reversed",
        "tickfont": {"size": 18},
    },
    xaxis={"side": "top"},
    font=dict(size=18),
    hoverlabel=dict(font_size=18),
)

st.plotly_chart(heatmap_fig, use_container_width=True)

# == INSIGHTS SECTION ==
st.markdown("### Summary Insights")
if df.empty:
    st.warning("No data available for the selected filters and date range.")
else:
    # Find strongest domain
    strongest_domain_idx = domain_summary_stats["avg_score"].idxmax()
    strongest_domain = DISPLAY_NAMES[strongest_domain_idx]

    # Find lowest 4 subdomains across all domains
    all_subdomain_scores = []
    for domain, subdomains in subdomain_mapping.items():
        for subdomain in subdomains:
            avg_score = df[subdomain].mean()
            all_subdomain_scores.append(
                {
                    "subdomain": DISPLAY_NAMES[subdomain],
                    "avg_score": round(avg_score, 2),
                }
            )

    # Sort by score and get the lowest 4
    subdomain_scores_df = pd.DataFrame(all_subdomain_scores)
    lowest_subdomains = subdomain_scores_df.nsmallest(4, "avg_score")[
        "subdomain"
    ].tolist()

    # Display strongest domain in green box
    st.markdown("**This cohort's strongest domain is:**")
    st.success(f"**{strongest_domain}**")

    # Display lowest subdomains in yellow boxes
    st.markdown("**Areas for greatest improvement:**")
    improvement_cols = st.columns(4)

    for i, subdomain in enumerate(lowest_subdomains):
        with improvement_cols[i]:
            st.warning(f"**{subdomain}**")

    # == COMPARISON COHORT SECTION ==
    st.markdown("#### Comparison Cohort Selection")

    # Comparison cohort date/time selectors
    comp_start_date_col, comp_end_date_col = st.columns(2)
    with comp_start_date_col:
        comp_start_date = st.date_input(
            "Previous Cohort Start Date", key="comp_start_date"
        )
    with comp_end_date_col:
        comp_end_date = st.date_input("Previous Cohort End Date", key="comp_end_date")

    comp_start_time_col, comp_end_time_col = st.columns(2)
    with comp_start_time_col:
        comp_start_time = st.time_input(
            "Previous Cohort Start Time", key="comp_start_time"
        )
    with comp_end_time_col:
        comp_end_time = st.time_input("Previous Cohort End Time", key="comp_end_time")

    # Combine comparison date and time into datetime objects
    comp_start_datetime = datetime.combine(comp_start_date, comp_start_time)
    comp_end_datetime = datetime.combine(comp_end_date, comp_end_time)

    # Filter for comparison cohort (using the same role filter as current cohort)
    df_comp = get_data()
    df_comp["submitted_at"] = pd.to_datetime(df_comp["submitted_at"])
    df_comp["submitted_at"] = df_comp["submitted_at"].dt.tz_localize(None)

    if role_filter == EMPTY_ROLE_OPTION:
        df_comp = df_comp[df_comp["role"].isna() | (df_comp["role"] == "")]
    elif role_filter != ALL_ROLES_OPTION:
        df_comp = df_comp[df_comp["role"] == role_filter]

    df_comp = df_comp[
        (df_comp["submitted_at"] >= comp_start_datetime)
        & (df_comp["submitted_at"] <= comp_end_datetime)
    ]

    # Calculate average scores for each subdomain in both cohorts
    subdomain_compare_data = []
    for domain, subdomains in subdomain_mapping.items():
        for subdomain in subdomains:
            current_avg = df[subdomain].mean() if not df.empty else 0
            comp_avg = df_comp[subdomain].mean() if not df_comp.empty else 0
            subdomain_compare_data.append(
                {
                    "domain": DISPLAY_NAMES[domain],
                    "subdomain": DISPLAY_NAMES[subdomain],
                    "Current Cohort": round(current_avg, 2),
                    "Previous Cohort": round(comp_avg, 2),
                }
            )

    subdomain_compare_df = pd.DataFrame(subdomain_compare_data)

    # Bar chart comparing subdomains
    compare_bar = go.Figure()

    compare_bar.add_trace(
        go.Bar(
            x=subdomain_compare_df["subdomain"],
            y=subdomain_compare_df["Previous Cohort"],
            name="Previous",
            marker_color="rgb(255, 99, 71)",
        )
    )
    compare_bar.add_trace(
        go.Bar(
            x=subdomain_compare_df["subdomain"],
            y=subdomain_compare_df["Current Cohort"],
            name="Current",
            marker_color="rgb(32, 201, 151)",
        )
    )

    compare_bar.update_layout(
        barmode="group",
        title="Subdomain Average Scores: Current vs. Previous Cohort",
        xaxis_title="Subdomain",
        yaxis_title="Average Score",
        height=500,
        xaxis={"tickangle": 45, "tickfont": {"size": 18}, "title_font": {"size": 20}},
        yaxis={"tickfont": {"size": 18}, "title_font": {"size": 20}},
        hoverlabel=dict(font_size=18),
    )

    st.plotly_chart(compare_bar, use_container_width=True)

# == EXPORT SECTION ==
st.markdown("### Export Current Cohort Data")
csv_export = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Current Cohort as CSV",
    data=csv_export,
    file_name="current_cohort.csv",
    mime="text/csv",
)


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
