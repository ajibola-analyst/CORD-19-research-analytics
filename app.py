import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CORD-19 Research Trends Explorer", layout="wide")

TEAL = "#1F6F6B"
AMBER = "#E8A33D"
BRICK = "#B85C4A"
OLIVE = "#6B8F58"
SLATE = "#5B7C99"
TAUPE = "#8C7B6B"
BG = "#F8F5EF"
TEXT = "#2B2B2B"

TOPIC_PALETTE = [TEAL, AMBER, BRICK, OLIVE, SLATE, TAUPE]




@st.cache_data
def load_summaries():
    monthly = pd.read_csv("data/summary_monthly_volume.csv", parse_dates=["publish_time"])
    pubtype = pd.read_csv("data/summary_pubtype_quarterly.csv")
    license_yearly = pd.read_csv("data/summary_license_yearly.csv")
    topic_quarterly = pd.read_csv("data/summary_topic_quarterly.csv")
    top_journals = pd.read_csv("data/summary_top_journals.csv")
    browse = pd.read_csv("data/summary_browse_sample.csv", parse_dates=["publish_time"])
    return monthly, pubtype, license_yearly, topic_quarterly, top_journals, browse

monthly, pubtype, license_yearly, topic_quarterly, top_journals, browse = load_summaries()

st.title("CORD-19 Research Trends Explorer")
st.caption(
    "How COVID-19 research responded, shifted, and opened up: "
    "December 2019 through December 2022, drawn from over 820,000 published abstracts."
)


st.markdown(
    f"""
    <div style="display:flex; gap:24px; padding:8px 0 20px 0; flex-wrap:wrap;">
        <div><span style="background:{TEAL}; padding:4px 10px; border-radius:4px; color:white;">Peer-reviewed / Open license</span></div>
        <div><span style="background:{AMBER}; padding:4px 10px; border-radius:4px; color:white;">Preprint / Closed license</span></div>
    </div>
    """,
    unsafe_allow_html=True
)


# Year filter — operates on the tiny monthly table only (37 rows),
# so this is instant no matter how it's touched.

years_available = sorted(monthly["publish_time"].dt.year.unique())
year_range = st.select_slider(
    "Filter years", options=years_available,
    value=(min(years_available), max(years_available))
)

def in_years(dt_series):
    return dt_series.dt.year.between(year_range[0], year_range[1])

monthly_f = monthly[in_years(monthly["publish_time"])]


# 1. Publication volume 

st.subheader(f"Publication Volume, {year_range[0]}–{year_range[1]}")
fig1 = px.line(monthly_f, x="publish_time", y="paper_count", color_discrete_sequence=[TEAL])
fig1.update_layout(plot_bgcolor=BG, paper_bgcolor=BG, showlegend=False,
                    xaxis_title="Month", yaxis_title="Papers published", font_color=TEXT)
st.plotly_chart(fig1, use_container_width=True)
st.caption("One line, one question answered: when did COVID-19 research activity actually happen.")


# 2. Preprint vs. peer-reviewed 

st.subheader("Preprints vs. Peer-Reviewed Publication, by Quarter")
fig2 = px.bar(
    pubtype, x="quarter", y="paper_count", color="pub_type",
    color_discrete_map={"Peer-reviewed": TEAL, "Preprint": AMBER},
    barmode="stack"
)
fig2.update_layout(plot_bgcolor=BG, paper_bgcolor=BG, font_color=TEXT,
                    xaxis_title="Quarter", yaxis_title="Papers", legend_title_text="")
st.plotly_chart(fig2, use_container_width=True)
st.caption(
    "Tracks how much of COVID-19 research bypassed traditional peer review during the "
    "pandemic — one of the most cited shifts in how science operated during the emergency."
)


# 3. Research focus shift 

st.subheader("Research Focus, by Quarter")
topic_quarterly_sorted = topic_quarterly.copy()
totals = topic_quarterly_sorted.groupby("topic_name")["paper_count"].sum().sort_values(ascending=False)
topic_order = totals.index.tolist()

fig3 = px.bar(
    topic_quarterly_sorted, x="quarter", y="paper_count", color="topic_name",
    category_orders={"topic_name": topic_order},
    color_discrete_sequence=TOPIC_PALETTE,
    barmode="stack"
)
fig3.update_layout(plot_bgcolor=BG, paper_bgcolor=BG, font_color=TEXT,
                    xaxis_title="Quarter", yaxis_title="Papers", legend_title_text="Research area")
st.plotly_chart(fig3, use_container_width=True)
st.caption(
    "Shows how scientific attention moved across pandemic phases — for example, from "
    "epidemic modeling early on toward clinical and mental-health research later."
)


# 4. Open-access adoption over time 
st.subheader("Open-Access Adoption, by Year")
lic = license_yearly.copy()
lic["status"] = lic["is_open"].map({True: "Open license", False: "Closed license"})
lic_totals = lic.groupby("year")["paper_count"].sum().rename("total")
lic = lic.merge(lic_totals, on="year")
lic["share"] = lic["paper_count"] / lic["total"]
lic_open = lic[lic["status"] == "Open license"].sort_values("year")

fig4 = px.bar(lic_open, x="year", y="share", color_discrete_sequence=[TEAL])
fig4.update_layout(plot_bgcolor=BG, paper_bgcolor=BG, showlegend=False,
                    xaxis_title="Year", yaxis_title="Share published under an open license",
                    yaxis_tickformat=".0%", font_color=TEXT)
st.plotly_chart(fig4, use_container_width=True)
st.caption("Tracks whether research openness increased or declined as the emergency wore on.")


# Top journals 
with st.expander("Top 15 journals by volume (secondary detail)"):
    tj = top_journals.sort_values("paper_count", ascending=True)
    fig5 = px.bar(tj, x="paper_count", y="journal", orientation="h",
                  color_discrete_sequence=[TAUPE])
    fig5.update_layout(plot_bgcolor=BG, paper_bgcolor=BG, showlegend=False,
                        xaxis_title="Number of papers", yaxis_title="", font_color=TEXT)
    st.plotly_chart(fig5, use_container_width=True)


# Browse 
st.subheader("Explore a Sample of the Data")
st.dataframe(browse[in_years(browse["publish_time"])].head(200))
