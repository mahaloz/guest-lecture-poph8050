from datetime import datetime
import html
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from core import APHIS_URL, CSV_URL, STATE_CODES, aggregate, map_window, monthly
from data_source import load_data

st.set_page_config(page_title="Avian Influenza Outbreak Explorer", page_icon="🦆", layout="wide")
st.markdown("""<style>
.block-container {padding-top:3.8rem; max-width:1550px}
h1 {font-size:2.7rem!important; letter-spacing:-1.4px; font-weight:750!important}
h2,h3 {letter-spacing:-.5px}
[data-testid="stMetric"] {background:white; border:1px solid #dde7eb; border-radius:12px; padding:16px 20px}
[data-testid="stMetricLabel"] {color:#536d7c}
[data-testid="stMetricValue"] {font-size:2rem}
.eyebrow {color:#008878; font-size:12px; font-weight:750; letter-spacing:2px}
.subhead {color:#5b7180; font-size:17px; max-width:900px; margin-bottom:24px}
.note {background:#e5f2ed; border-left:3px solid #008878; padding:15px 18px; border-radius:5px; margin:10px 0; line-height:1.6}
</style>""", unsafe_allow_html=True)

try:
    data, meta, source_status, download_error = load_data()
except RuntimeError as exc:
    st.error(str(exc))
    st.stop()

first, last = data.Date.min(), data.Date.max()
st.markdown('<div class="eyebrow">HPAI · UNITED STATES · RESEARCH EXPLORER</div>', unsafe_allow_html=True)
st.title("Avian Influenza Outbreak Explorer")
st.markdown('<div class="subhead">Follow the geography and timing of confirmed flock detections. Explore the historical record, one month at a time.</div>', unsafe_allow_html=True)
st.caption(f"SOURCE COVERAGE  {first:%b %d, %Y} – {last:%b %d, %Y}   ·   {len(data):,} source records   ·   Retrieved {datetime.fromisoformat(meta['retrieved_at']):%Y-%m-%d %H:%M UTC}")
if download_error:
    st.warning("The download is unavailable. Showing the verified local snapshot with the retrieval date above.")

with st.sidebar:
    st.markdown("### Explore the record")
    st.caption("All views share these filters.")
    metric_label = st.radio("Measure", ["Flock detections", "Birds in affected flocks"])
    metric = "Detections" if metric_label == "Flock detections" else "Birds"
    states = st.multiselect("States / territories", sorted(data.State.unique()), placeholder="All states and territories")
    dates = st.date_input("Confirmation date range", value=(first.date(), last.date()), min_value=first.date(), max_value=last.date(), format="YYYY-MM-DD")
    categories = st.multiselect("Source category", sorted(data.Category.unique()), placeholder="All source categories")
    st.caption("Commercial means the source label begins with ‘Commercial’. Other labels cannot be reliably classified as backyard.")
    ops = st.multiselect("Exact operation type", sorted(data["Operation Type"].unique()), placeholder="All operation types")
    st.divider()
    st.caption("Bird counts describe birds in affected flocks. They are not counts of confirmed infected or dead birds.")
    if st.button("Refresh source data", width="stretch"):
        from data_source import DATA
        (DATA / "latest.metadata.json").unlink(missing_ok=True)
        load_data.clear()
        st.rerun()
    st.caption(f"{source_status} · Cached for 24 hours")

if len(dates) != 2:
    st.info("Choose an end date to complete the date-range filter.")
    st.stop()
start, end = map(pd.Timestamp, dates)
filtered = data.loc[data.Date.between(start, end)].copy()
if states:
    filtered = filtered.loc[filtered.State.isin(states)]
if categories:
    filtered = filtered.loc[filtered.Category.isin(categories)]
if ops:
    filtered = filtered.loc[filtered["Operation Type"].isin(ops)]
months = pd.date_range(start.to_period("M").start_time, end.to_period("M").start_time, freq="MS")
labels = [d.strftime("%Y-%m") for d in months]
fingerprint = (tuple(states), str(start), str(end), tuple(categories), tuple(ops))
if st.session_state.get("filters") != fingerprint:
    st.session_state.filters = fingerprint
    st.session_state.cursor = labels[-1]
    st.session_state.playing = False
    st.session_state.tick = False

a, b, c, d = st.columns(4)
a.metric("Flock detections · date range", f"{len(filtered):,}")
birds = filtered["Birds Impacted"].sum(min_count=1)
b.metric("Birds in affected flocks · date range", "Unknown" if pd.isna(birds) else f"{birds:,.0f}")
c.metric("States / territories with detections", filtered.State.nunique())
d.metric("Months with detections", filtered.Month.nunique())
missing = filtered["Birds Impacted"].isna().sum()
if missing:
    st.warning(f"{missing:,} selected records lack bird counts. Bird totals sum known counts only; all records count as flock detections.")
if filtered.empty:
    st.info("No detections match these filters. Clear a state or operation filter, or widen the date range.")


def chart_style(fig, height):
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=15, b=0), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Arial", color="#365263"))
    return fig


@st.fragment(run_every=1.2 if st.session_state.get("playing") else None)
def explorer():
    # A fragment keeps playback responsive without re-downloading or redrawing the sidebar.
    if st.session_state.get("playing") and st.session_state.get("tick"):
        i = labels.index(st.session_state.cursor)
        if i < len(labels) - 1:
            st.session_state.cursor = labels[i + 1]
        else:
            st.session_state.playing = False
            st.rerun()
    st.session_state.tick = st.session_state.get("playing", False)
    left, right = st.columns([3, 2])
    with left:
        st.subheader("01 / Outbreak geography")
    with right:
        mode = st.radio("Map accumulation", ["Monthly", "Cumulative"], horizontal=True, label_visibility="collapsed")
    ctrl, slider = st.columns([1, 7], vertical_alignment="center")
    def toggle_play():
        if not st.session_state.playing and st.session_state.cursor == labels[-1]:
            st.session_state.cursor = labels[0]
        st.session_state.playing = not st.session_state.playing
        st.session_state.tick = False
    with ctrl:
        if st.button("⏸ Pause" if st.session_state.playing else "▶ Play", on_click=toggle_play, width="stretch", disabled=len(labels) < 2):
            st.rerun()
    with slider:
        if len(labels) > 1:
            st.select_slider("Map month", options=labels, key="cursor")
        else:
            st.markdown(f"**Map month: {labels[0]}**")
    month = pd.Timestamp(st.session_state.cursor + "-01")
    window = map_window(filtered, month, mode == "Cumulative")
    grouped = aggregate(window, "State")
    geography, ranking = st.columns([3.2, 1])
    with geography:
        if mode == "Cumulative":
            st.caption(f"{start:%b %d, %Y} → {min(end, month + pd.offsets.MonthEnd(0)):%b %d, %Y} · Cumulative within your filtered date range")
        else:
            st.caption(f"{month:%B %Y} · Monthly detections within your filtered date range")
        # Stabilize the color scale across animation frames for meaningful comparisons.
        reference = aggregate(filtered, "State") if mode == "Cumulative" else aggregate(filtered, ["Month", "State"])
        maximum = reference[metric].max() if not reference.empty else 1
        maximum = 1 if pd.isna(maximum) else max(float(maximum), 1)
        mapdata = pd.DataFrame({"State": list(STATE_CODES), "Code": list(STATE_CODES.values())})
        if states:
            mapdata = mapdata.loc[mapdata.State.isin(states)]
        mapdata = mapdata.merge(grouped, on="State", how="left")
        absent = mapdata.Detections.isna()
        mapdata.loc[absent, ["Detections", "Birds", "Missing_birds"]] = 0
        fig = go.Figure(go.Choropleth(locations=mapdata.Code, locationmode="USA-states", z=mapdata[metric],
            text=mapdata.State, customdata=mapdata[["Detections", "Birds", "Missing_birds"]],
            zmin=0, zmax=maximum, colorscale=[[0,"#e6eeed"],[.12,"#b0dbca"],[.4,"#55ac93"],[.7,"#187e74"],[1,"#07544f"]],
            marker_line_color="white", marker_line_width=.8,
            colorbar=dict(title="Flocks" if metric == "Detections" else "Birds", thickness=12, len=.65),
            hovertemplate="<b>%{text}</b><br>Flock detections: %{customdata[0]:,.0f}<br>Birds in affected flocks (known): %{customdata[1]:,.0f}<br>Missing bird counts: %{customdata[2]:,.0f}<extra></extra>"))
        fig.update_geos(scope="usa", projection_type="albers usa", bgcolor="rgba(0,0,0,0)", showlakes=False, resolution=110)
        st.plotly_chart(chart_style(fig, 430), width="stretch", config={"displayModeBar":False,"topojsonURL":"/app/static/"})
        st.caption("Gray-green states have zero matching records; unselected states are uncolored. Puerto Rico is included in totals and the table below, but is outside this map projection. Color scale stays fixed during playback.")
    with ranking:
        st.markdown(f"#### {month:%b %Y}")
        st.caption(f"{mode} map window")
        st.metric("Flock detections", f"{len(window):,}")
        top = grouped.sort_values(metric, ascending=False).head(6)
        st.markdown("**Leading states / territories**")
        if top.empty:
            st.caption("No matching detections this month.")
        for row in top.itertuples():
            value = getattr(row, metric)
            st.markdown(f"{html.escape(row.State)} **{'Unknown' if pd.isna(value) else f'{value:,.0f}'}**")

    st.subheader("02 / The outbreak timeline")
    st.caption("Drag the range handles to zoom; select a bar to set the map month. Date filters above set the analysis period. Playback advances one month every 1.2 seconds.")
    series = monthly(filtered, months)
    timeline = go.Figure(go.Bar(x=series.Month, y=series[metric],
        marker_color=["#ed9958" if m == month else "#168b7c" for m in series.Month],
        customdata=series[["Detections", "Birds", "Missing_birds"]],
        hovertemplate="<b>%{x|%B %Y}</b><br>Flock detections: %{customdata[0]:,.0f}<br>Birds in affected flocks (known): %{customdata[1]:,.0f}<br>Missing bird counts: %{customdata[2]:,.0f}<extra></extra>"))
    timeline.update_layout(dragmode="select", clickmode="event+select", uirevision=str(fingerprint),
        xaxis=dict(rangeslider=dict(visible=True, thickness=.14), type="date",
            rangeselector=dict(buttons=[dict(count=6, label="6 months", step="month", stepmode="backward"),dict(count=1,label="1 year",step="year",stepmode="backward"),dict(step="all",label="All") ])),
        yaxis=dict(title=metric_label, gridcolor="#dce6e9", rangemode="tozero"), showlegend=False)
    def select_month():
        points = st.session_state.timeline.selection.points
        if points:
            selected = pd.Timestamp(points[0]["x"]).strftime("%Y-%m")
            if selected in labels:
                st.session_state.cursor = selected
                st.session_state.playing = False
                st.session_state.tick = False
                st.session_state.selection_changed = True
    st.plotly_chart(chart_style(timeline, 310), key="timeline", on_select=select_month,
                    selection_mode=("points", "box"), config={"displaylogo":False}, width="stretch")
    if st.session_state.pop("selection_changed", False):
        st.rerun()
    if start.day != 1 or end != end + pd.offsets.MonthEnd(0) or end == last:
        st.caption("Boundary months can be partial: only dates inside the selected range and source coverage are counted. Selecting multiple bars uses the first selected month.")


explorer()
st.divider()
st.subheader("03 / What stands out")
st.caption(f"Computed from the entire filtered date range ({start:%Y-%m-%d} to {end:%Y-%m-%d}), using {metric_label.lower()}. These are descriptive counts, not risk estimates.")
if not filtered.empty:
    totals = monthly(filtered, months)
    peaks = totals.loc[totals[metric] == totals[metric].max()]
    state_totals = aggregate(filtered, "State")
    leaders = state_totals.loc[state_totals[metric] == state_totals[metric].max()]
    total = totals[metric].sum(min_count=1)
    cards = st.columns(3)
    unit = "flock detections" if metric == "Detections" else "birds in affected flocks (known counts)"
    if not peaks.empty:
        with cards[0]:
            st.markdown("**Peak month**")
            st.markdown(f"{', '.join(peaks.Month.dt.strftime('%b %Y'))}: **{peaks[metric].iloc[0]:,.0f}** {unit}.")
            st.caption("Monthly sum; all ties shown. Partial boundary months are included.")
    if not leaders.empty:
        with cards[1]:
            st.markdown("**Largest recorded total**")
            st.write(f"{', '.join(leaders.State)}: {leaders[metric].iloc[0]:,.0f} {unit}.")
            st.caption("Sum by state/territory; all ties shown. No population adjustment.")
    with cards[2]:
        st.markdown("**Commercial share**")
        commercial = filtered.loc[filtered.Category == "Commercial (explicit label)"]
        n = len(commercial) if metric == "Detections" else commercial["Birds Impacted"].sum(min_count=1)
        if commercial.empty:
            n = 0
        st.write(f"{n / total:.1%} of {total:,.0f} {unit}." if pd.notna(total) and total > 0 and pd.notna(n) else "Share unavailable: missing or zero denominator.")
        st.caption("Numerator: records explicitly labeled Commercial. Denominator: selected total.")

with st.expander("Verify the summaries · state totals and source records"):
    st.caption("Tables and CSV use the entire filtered date range; the map month affects only the map and its adjacent ranking.")
    st.dataframe(aggregate(filtered, "State").sort_values(metric, ascending=False), hide_index=True, width="stretch")
    st.dataframe(filtered[["Date","State","County","Operation Type","Birds Impacted"]], hide_index=True, width="stretch")
    st.download_button("Download filtered records (CSV)", filtered.to_csv(index=False).encode(), "hpai_filtered.csv", "text/csv")

with st.expander("Source, interpretation & limitations", expanded=True):
    st.markdown(f"**Official context:** [USDA APHIS confirmed poultry flock detections]({APHIS_URL}). **Data used:** [APHIS-derived CSV maintained by a third party]({CSV_URL}). This is not a direct APHIS data feed.")
    st.write(f"Retrieved: {meta['retrieved_at']} · Dataset coverage: {first:%Y-%m-%d} through {last:%Y-%m-%d}. Last detection date does not establish reporting completeness.")
    st.caption(f"SHA-256: {meta['sha256']}")
    duplicates = data.duplicated(subset=["Date","State","County","Operation Type","Birds Impacted"]).sum()
    st.markdown(f"Each CSV row is treated as one flock detection record, not a unique farm or an infected bird. **{duplicates} identical rows beyond the first are retained**: without record IDs, repeated detections and duplicate entries cannot be distinguished. Counts may be revised; recent periods may be incomplete. No missing bird counts are filled in.")
    st.markdown("Operation labels are preserved. ‘WOAH Poultry’ and ‘WOAH Non-Poultry’ do not provide a reliable commercial/backyard distinction. This app does not infer backyard status. Wild-bird and mammal surveillance are outside this dataset. Counts are not adjusted for flock size, regional poultry populations, or surveillance intensity and cannot establish transmission routes or causation.")
