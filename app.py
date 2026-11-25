import io
import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import streamlit as st

st.set_page_config(page_title="SCM Excise — India Regional Cluster Map", layout="wide")

# ---------------------------------------------------------
# 1. Pre-defined 6 Regional Clusters & Colors
# ---------------------------------------------------------
CLUSTERS = [
    "North India",
    "Central India",
    "Northeast India",
    "East India",
    "West India",
    "South India",
]

CLUSTER_COLORS = {
    "North India": "#2ca02c",      # Green
    "Central India": "#ff7f0e",    # Orange
    "Northeast India": "#9467bd",  # Purple
    "East India": "#17becf",       # Teal
    "West India": "#1f77b4",       # Blue
    "South India": "#d62728",      # Red
}

INITIAL_DATA = [
    # West India
    ("Goa", "West India", 1772, 0, 87),
    ("Daman", "West India", 1668, 0, 43),
    ("Silvassa", "West India", 1058, 0, 35),
    ("Gujarat", "West India", 724, 0, 32),
    ("Diu Island", "West India", 164, 2, 3),
    ("Maharashtra", "West India", 0, 0, 0),
    # South India
    ("Andhra Pradesh", "South India", 1244, 5, 66),
    ("Karnataka", "South India", 908, 4, 117),
    ("Telangana", "South India", 297, 1, 18),
    ("Kerala", "South India", 203, 1, 13),
    ("Puducherry", "South India", 188, 0, 10),
    ("Tamil Nadu", "South India", 141, 1, 21),
    ("Andaman & Nicobar", "South India", 5, 0, 4),
    # Central India
    ("Chhattisgarh", "Central India", 945, 0, 48),
    ("Madhya Pradesh", "Central India", 640, 3, 15),
    # East India
    ("Odisha", "East India", 974, 0, 64),
    ("Jharkhand", "East India", 378, 1, 50),
    ("West Bengal", "East India", 206, 2, 15),
    ("Bihar", "East India", 0, 0, 0),
    # North India
    ("Rajasthan", "North India", 730, 4, 49),
    ("Uttar Pradesh", "North India", 717, 0, 9),
    ("Punjab", "North India", 297, 0, 25),
    ("Haryana", "North India", 242, 0, 7),
    ("Delhi", "North India", 219, 0, 10),
    ("Uttarakhand", "North India", 56, 0, 5),
    ("Chandigarh", "North India", 40, 0, 2),
    ("Jammu & Kashmir", "North India", 29, 0, 2),
    ("Himachal Pradesh", "North India", 22, 0, 1),
    ("Ladakh", "North India", 1, 0, 1),
    # Northeast India
    ("Arunachal Pradesh", "Northeast India", 159, 0, 52),
    ("Assam", "Northeast India", 109, 0, 13),
    ("Meghalaya", "Northeast India", 46, 0, 10),
    ("Nagaland", "Northeast India", 11, 0, 1),
    ("Sikkim", "Northeast India", 7, 0, 2),
    ("Tripura", "Northeast India", 7, 0, 1),
    ("Manipur", "Northeast India", 1, 0, 0),
    ("Mizoram", "Northeast India", 0, 0, 0),
]

COORDS = {
    "Goa": (74.12, 15.30), "Daman": (72.83, 20.40), "Silvassa": (73.01, 20.28),
    "Gujarat": (71.19, 22.26), "Diu Island": (70.99, 20.71), "Maharashtra": (75.71, 19.75),
    "Andhra Pradesh": (79.74, 15.91), "Karnataka": (75.71, 15.32), "Telangana": (79.02, 18.11),
    "Kerala": (76.27, 10.85), "Puducherry": (79.81, 11.94), "Tamil Nadu": (78.66, 11.13),
    "Andaman & Nicobar": (92.66, 11.74),
    "Chhattisgarh": (81.87, 21.28), "Madhya Pradesh": (78.66, 22.97),
    "Odisha": (85.10, 20.95), "Jharkhand": (85.28, 23.61), "West Bengal": (87.85, 22.99),
    "Bihar": (85.31, 25.09),
    "Rajasthan": (74.22, 27.02), "Uttar Pradesh": (80.95, 26.85), "Punjab": (75.34, 31.15),
    "Haryana": (76.09, 29.06), "Delhi": (77.10, 28.70), "Uttarakhand": (79.02, 30.07),
    "Chandigarh": (76.78, 30.73), "Jammu & Kashmir": (75.34, 33.78),
    "Himachal Pradesh": (77.17, 31.10), "Ladakh": (77.58, 34.15),
    "Arunachal Pradesh": (94.73, 28.22), "Assam": (92.94, 26.20), "Meghalaya": (91.37, 25.47),
    "Nagaland": (94.56, 26.16), "Sikkim": (88.51, 27.53), "Tripura": (91.99, 23.94),
    "Manipur": (93.91, 24.66), "Mizoram": (92.94, 23.16),
}

# ---------------------------------------------------------
# 2. Load Local India States GeoJSON from Repo
# ---------------------------------------------------------
@st.cache_data
def load_india_states_geojson():
    geojson_path = os.path.join(os.path.dirname(__file__), "india_states.geojson")
    gdf = gpd.read_file(geojson_path)
    name_map = {
        "Andaman & Nicobar Island": "Andaman & Nicobar",
        "Arunanchal Pradesh": "Arunachal Pradesh",
        "Dadra and Nagar Haveli and Daman and Diu": "Daman",
        "NCT of Delhi": "Delhi",
        "Jammu & Kashmir": "Jammu & Kashmir",
        "Orissa": "Odisha",
        "Pondicherry": "Puducherry",
        "Uttaranchal": "Uttarakhand",
    }
    gdf["Clean_State"] = gdf["ST_NM"].replace(name_map)
    return gdf

# ---------------------------------------------------------
# 3. Render State-Bordered Cluster Map
# ---------------------------------------------------------
def build_cluster_map(df_edit: pd.DataFrame, states_gdf: gpd.GeoDataFrame, show_labels: bool):
    state_to_cluster = dict(zip(df_edit["State"], df_edit["Cluster"]))
    states_gdf = states_gdf.copy()
    states_gdf["Cluster"] = states_gdf["Clean_State"].map(state_to_cluster)
    states_gdf["Fill_Color"] = states_gdf["Cluster"].map(CLUSTER_COLORS).fillna("#ececec")

    fig, ax = plt.subplots(figsize=(13.5, 11.5), dpi=180)
    fig.patch.set_facecolor("#f7f9fc")
    ax.set_facecolor("#dcebf7")

    # Fill each state with its cluster color and internal state border
    states_gdf.plot(
        ax=ax,
        color=states_gdf["Fill_Color"],
        edgecolor="#444444",
        linewidth=0.75,
        alpha=0.38,
        zorder=2,
    )

    # Dissolve by Cluster to draw thick outer borders around each regional cluster
    clustered_gdf = states_gdf[states_gdf["Cluster"].notna()]
    if not clustered_gdf.empty:
        dissolved = clustered_gdf.dissolve(by="Cluster").reset_index()
        for _, row in dissolved.iterrows():
            col = CLUSTER_COLORS[row["Cluster"]]
            gpd.GeoSeries([row.geometry]).boundary.plot(
                ax=ax, color=col, linewidth=2.3, zorder=3
            )

    active = df_edit[df_edit["Grand_Total"] > 0].copy()
    max_total = max(active["Grand_Total"].max(), 1)

    for cl in CLUSTERS:
        sub = active[active["Cluster"] == cl]
        if sub.empty:
            continue
        lons = [COORDS[s][0] for s in sub["State"] if s in COORDS]
        lats = [COORDS[s][1] for s in sub["State"] if s in COORDS]
        vals = [r["Grand_Total"] for _, r in sub.iterrows() if r["State"] in COORDS]
        sizes = [65 + (v / max_total) * 520 for v in vals]

        ax.scatter(
            lons, lats, s=sizes, color=CLUSTER_COLORS[cl],
            edgecolors="#111111", linewidth=0.9, alpha=0.92, zorder=4
        )

    if show_labels:
        for _, r in active.iterrows():
            st_name = r["State"]
            if st_name not in COORDS:
                continue
            lon, lat = COORDS[st_name]
            lost_str = f" [Lost:{int(r['Device_Lost'])}]" if r["Device_Lost"] > 0 else ""
            label_txt = f"{st_name} ({int(r['Grand_Total']):,}){lost_str}"
            ax.annotate(
                label_txt,
                (lon, lat),
                xytext=(5, 4),
                textcoords="offset points",
                fontsize=7.3,
                fontweight="bold" if r["Grand_Total"] >= 700 or r["Device_Lost"] >= 3 else "normal",
                color="#111111",
                bbox=dict(boxstyle="round,pad=0.14", fc="white", ec="none", alpha=0.78),
                zorder=5,
            )

    legend_handles = []
    for cl in CLUSTERS:
        sub = df_edit[df_edit["Cluster"] == cl]
        tot = int(sub["Grand_Total"].sum())
        lost = int(sub["Device_Lost"].sum())
        nrecv = int(sub["Not_Received"].sum())
        pct = (nrecv / tot * 100) if tot > 0 else 0.0
        lbl = f"{cl}: {tot:,} | Lost: {lost} | Not Recv: {nrecv} ({pct:.1f}%)"
        legend_handles.append(mpatches.Patch(color=CLUSTER_COLORS[cl], label=lbl))

    ax.legend(
        handles=legend_handles,
        loc="lower left",
        title="Regional Clusters (Bordered by State)",
        title_fontsize=9.2,
        fontsize=8.2,
        frameon=True,
        facecolor="white",
        edgecolor="#888888",
        framealpha=0.95,
    ).set_zorder(6)

    net_tot = int(df_edit["Grand_Total"].sum())
    net_lost = int(df_edit["Device_Lost"].sum())
    net_nrecv = int(df_edit["Not_Received"].sum())
    ax.text(
        97.8, 6.8,
        f"Network Total: {net_tot:,} | Device Lost: {net_lost} | Not Received: {net_nrecv:,}",
        ha="right", va="bottom", fontsize=8.3, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.35", fc="#fffdf0", ec="#bbbbbb", alpha=0.95),
        zorder=6,
    )

    ax.set_xlim(67.5, 98.2)
    ax.set_ylim(6.2, 37.2)
    ax.set_xlabel("Longitude (°E)", fontsize=9.5, fontweight="bold")
    ax.set_ylabel("Latitude (°N)", fontsize=9.5, fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.set_title(
        "SCM Excise — State-Bordered Regional Cluster Map Across India",
        fontsize=13.5, fontweight="bold", pad=12,
    )
    plt.tight_layout()
    return fig

# ---------------------------------------------------------
# 4. Streamlit UI Layout
# ---------------------------------------------------------
st.title("SCM Excise — Live Regional Cluster Map (State-Bordered)")
st.markdown(
    "Edit any value or reassign a state's **Cluster** below—the India map and regional totals update immediately."
)

if "cluster_df" not in st.session_state:
    st.session_state.cluster_df = pd.DataFrame(
        INITIAL_DATA, columns=["State", "Cluster", "Grand_Total", "Device_Lost", "Not_Received"]
    )

with st.sidebar:
    st.header("Map Settings & Excel Upload")
    show_labels = st.checkbox("Show State Labels on Map", value=True)
    uploaded = st.file_uploader("Upload Updated Excel (.xlsx) (Optional)", type=["xlsx"])
    if uploaded is not None:
        up_df = pd.read_excel(uploaded)
        required_cols = {"State", "Grand_Total", "Device_Lost", "Not_Received"}
        if required_cols.issubset(set(up_df.columns)):
            if "Cluster" not in up_df.columns:
                default_map = dict(zip(st.session_state.cluster_df["State"], st.session_state.cluster_df["Cluster"]))
                up_df["Cluster"] = up_df["State"].map(default_map).fillna("North India")
            st.session_state.cluster_df = up_df[["State", "Cluster", "Grand_Total", "Device_Lost", "Not_Received"]]
            st.success("Excel loaded successfully!")
        else:
            st.error(f"Excel must include columns: {required_cols}")

    if st.button("Reset to Default Values"):
        st.session_state.cluster_df = pd.DataFrame(
            INITIAL_DATA, columns=["State", "Cluster", "Grand_Total", "Device_Lost", "Not_Received"]
        )
        st.rerun()

col_table, col_map = st.columns([1.05, 1.35], gap="large")

with col_table:
    st.subheader("1. Edit Values or Cluster Assignment")
    edited_df = st.data_editor(
        st.session_state.cluster_df,
        use_container_width=True,
        height=600,
        hide_index=True,
        column_config={
            "State": st.column_config.TextColumn("State / UT", disabled=True),
            "Cluster": st.column_config.SelectboxColumn("Cluster", options=CLUSTERS, required=True),
            "Grand_Total": st.column_config.NumberColumn("Grand Total", min_value=0, step=1),
            "Device_Lost": st.column_config.NumberColumn("Device Lost", min_value=0, step=1),
            "Not_Received": st.column_config.NumberColumn("Not Received", min_value=0, step=1),
        },
    )

    st.subheader("2. Live Cluster Summary")
    summary_df = (
        edited_df.groupby("Cluster", as_index=False)[["Grand_Total", "Device_Lost", "Not_Received"]]
        .sum()
        .sort_values("Grand_Total", ascending=False)
    )
    summary_df["Not_Recv_%"] = (
        (summary_df["Not_Received"] / summary_df["Grand_Total"].replace(0, pd.NA)) * 100
    ).fillna(0).round(2)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

with col_map:
    st.subheader("3. Live State-Bordered India Map")
    states_gdf = load_india_states_geojson()
    fig = build_cluster_map(edited_df, states_gdf, show_labels)
    st.pyplot(fig, use_container_width=True)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=220, bbox_inches="tight")
    st.download_button(
        label="Download Updated Map (PNG)",
        data=buf.getvalue(),
        file_name="india_regional_cluster_map.png",
        mime="image/png",
    )
