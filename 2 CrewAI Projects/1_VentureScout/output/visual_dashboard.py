# visual_dashboard.py

import pandas as pd
import plotly.express as px
import gradio as gr

# =======================
# --- DATA MANAGEMENT ---
# =======================

STARTUP_DATA = [
    # name, sector, ARR (M USD), growth_rate %, valuation (M USD), stage, financial_health
    ['Scale AI', 'Artificial Intelligence', 680, 97, 14000, 'Growth', 'Excellent'],
    ['Ora AI', 'Artificial Intelligence', 1.2, 130, 16, 'Seed', 'Promising'],
    ['Skild AI', 'Artificial Intelligence', 32, 90, 4500, 'Growth', 'Very Good'],
    ['Astro', 'Clean Energy', 10.5, 85, 270, 'Development', 'Good'],
    ['Cloover', 'Clean Energy', 7.2, 75, 180, 'Development', 'Promising'],
    ['Pogo', 'Clean Energy', 4.8, 70, 85, 'Seed', 'Growing'],
    ['Blockaid', 'Blockchain', 12.1, 77, 310, 'Development', 'Solid'],
    ['Govly', 'Blockchain', 1.7, 120, 20, 'Seed', 'To Monitor'],
]

df = pd.DataFrame(STARTUP_DATA, columns=[
    "Name", "Sector", "ARR (M USD)", "Growth (%)", "Valuation (M USD)", "Stage", "Financial Health"
])

sector_palette = {
    "Artificial Intelligence": "#1f77b4",
    "Clean Energy": "#2ca02c",
    "Blockchain": "#d62728"
}

# Health order for sorting
health_order = ["Excellent", "Very Good", "Solid", "Good", "Promising", "Growing", "To Monitor"]

# =======================
# --- GRAPH FUNCTIONS ---
# =======================

def plot_roi_vs_growth(data):
    fig = px.scatter(
        data, x="Growth (%)", y="ARR (M USD)", color="Sector",
        size="Valuation (M USD)", hover_name="Name",
        color_discrete_map=sector_palette,
        title="Growth (%) vs ARR (M USD)",
        labels={"Growth (%)":"Growth Rate (%)", "ARR (M USD)":"ARR (M USD)"}
    )
    fig.update_layout(height=450, margin={"t":50,"b":30,"l":20,"r":10})
    return fig

def plot_sector_distribution(data):
    count_by_sector = data.groupby("Sector").size().reset_index(name="Count")
    fig = px.pie(
        count_by_sector, names="Sector", values="Count",
        color="Sector", color_discrete_map=sector_palette,
        title="Startup Distribution by Sector"
    )
    fig.update_traces(textinfo='label+percent')
    return fig

def plot_top_growth_bar(data):
    fig = px.bar(
        data.sort_values("Growth (%)", ascending=False),
        x="Name", y="Growth (%)", color="Sector",
        color_discrete_map=sector_palette,
        title="Ranking: Startups by Growth Rate (%)"
    )
    fig.update_layout(xaxis_title="", yaxis_title="Growth (%)", height=400, margin=dict(b=40))
    return fig

def plot_valuation_treemap(data):
    fig = px.treemap(
        data, path=["Sector", "Name"],
        values="Valuation (M USD)", color="Sector",
        color_discrete_map=sector_palette,
        title="Startup Valuation by Sector"
    )
    return fig

def plot_stage_distribution(data, sector):
    fig = px.histogram(
        data, x="Stage", color="Financial Health", barmode='group',
        title=f"Stage Distribution - {sector} Sector",
        category_orders={"Financial Health": health_order}
    )
    fig.update_layout(height=320)
    return fig

def filter_by_sector(sector):
    if sector == "All":
        return df
    else:
        return df[df["Sector"] == sector]

def table_by_health():
    sorted_df = df.copy()
    sorted_df["_HealthOrder_"] = sorted_df["Financial Health"].apply(
        lambda x: health_order.index(x) if x in health_order else 99
    )
    sorted_df = sorted_df.sort_values(["_HealthOrder_", "Growth (%)"], ascending=[True, False]).drop("_HealthOrder_", axis=1)
    display_cols = ["Name", "Sector", "Financial Health", "Stage", "ARR (M USD)", "Growth (%)", "Valuation (M USD)"]
    return sorted_df[display_cols].reset_index(drop=True)

# =======================
# --- INTERACTIVE LOGIC --
# =======================

def update_dashboard(sector):
    # Filter data based on selection
    filtered_data = filter_by_sector(sector)
    
    # Update ROI vs Growth plot
    fig1 = plot_roi_vs_growth(filtered_data)
    
    # Update sector table
    if not filtered_data.empty:
        sector_table = filtered_data[[
            "Name", "Stage", "ARR (M USD)", "Growth (%)", "Valuation (M USD)", "Financial Health"
        ]].reset_index(drop=True)
    else:
        sector_table = pd.DataFrame(columns=[
            "Name", "Stage", "ARR (M USD)", "Growth (%)", "Valuation (M USD)", "Financial Health"
        ])
    
    # Update sector distribution plot
    if sector == "All":
        fig_sector = plot_sector_distribution(filtered_data)
    else:
        fig_sector = plot_stage_distribution(filtered_data, sector)
    
    return fig1, sector_table, fig_sector

# Initialize with all data
initial_fig1 = plot_roi_vs_growth(df)
initial_sector_table = df[[
    "Name", "Stage", "ARR (M USD)", "Growth (%)", "Valuation (M USD)", "Financial Health"
]].reset_index(drop=True)
initial_fig_sector = plot_sector_distribution(df)

# =======================
# ------- GRADIO --------
# =======================

with gr.Blocks(title="Investment Dashboard: Strategic Startups", theme=gr.themes.Base(primary_hue="green")) as demo:
    gr.Markdown("""
    # 📈 Strategic Investment Recommendations Dashboard
    Visualize analysis of innovative startups in Artificial Intelligence, Clean Energy, and Blockchain.
    """)
    
    with gr.Row():
        with gr.Column(scale=3):
            gr.Markdown("## Select a sector for segmented analysis")
            sector_sel = gr.Dropdown(
                choices=["All"] + sorted(df["Sector"].unique().tolist()),
                value="All", label="Filter by Sector"
            )
            gr.Markdown(
                "<small>The table and charts will change based on the selected sector. Use 'All' for complete overview.</small>",
                elem_id="info-text"
            )
        with gr.Column():
            sector_dist_plot = gr.Plot(initial_fig_sector, label="Startup Distribution by Sector")

    with gr.Tab("Interactive Charts"):
        with gr.Row():
            plot_out = gr.Plot(initial_fig1, label="Growth vs ARR")
        with gr.Row():
            sector_plot = gr.Plot(initial_fig_sector, label="Sector Visualization")
        gr.Markdown("### Comparative Startup Table (by sector)")
        data_table = gr.Dataframe(
            value=initial_sector_table,
            label="Startups in Selected Sector",
            headers=["Name", "Stage", "ARR (M USD)", "Growth (%)", "Valuation (M USD)", "Financial Health"], 
            datatype=["str", "str", "number", "number", "number", "str"],
            interactive=False
        )

    with gr.Tab("Growth Ranking"):
        growth_plot = gr.Plot(plot_top_growth_bar(df), label="Growth Ranking")
        gr.Markdown("Top startups ranked by annual growth rate.")

    with gr.Tab("Valuation Map"):
        treemap_plot = gr.Plot(plot_valuation_treemap(df), label="Valuation Treemap")
        gr.Markdown("Visualize the proportionality of each startup's valuation by sector.")

    with gr.Tab("Financial Health Comparison"):
        gr.Markdown("Startups ordered by financial health level and growth.")
        health_table = gr.Dataframe(
            table_by_health(), 
            label="Comparison by Financial Health",
            headers=["Name", "Sector", "Financial Health", "Stage", "ARR (M USD)", "Growth (%)", "Valuation (M USD)"]
        )

    # Main interaction
    sector_sel.change(
        update_dashboard, 
        inputs=[sector_sel], 
        outputs=[plot_out, data_table, sector_plot]
    )
    
    # Also update the sector distribution plot when sector changes
    sector_sel.change(
        lambda sector: plot_sector_distribution(filter_by_sector(sector)),
        inputs=[sector_sel],
        outputs=[sector_dist_plot]
    )
    
    gr.Markdown("""
    ---
    _Data visualization for informed investment decisions ⚡_
    """)

if __name__ == "__main__":
    demo.launch()