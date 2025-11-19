# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page config (single call)
st.set_page_config(page_title="Paragon Dashboard", layout="wide", page_icon="📊", initial_sidebar_state="expanded")

# --------------------------
# Dark theme CSS + plot container styles
st.markdown("""
<style>
/* Page colors */
body {
    background-color: #0f111a;
    color: #ffffff;
}
.stSidebar {
    background-color: #1f2233;
    color: #ffffff;
}
h1, h2, h3, h4, h5, h6 {
    color: #e6eef6;
}

/* Card & kpi */
.card {
    background: linear-gradient(180deg, rgba(30,33,43,1) 0%, rgba(22,24,32,1) 100%);
    padding: 14px; border-radius: 10px;
    box-shadow: 0 6px 18px rgba(2,6,23,0.6);
    margin-bottom: 12px; color: #e6eef6;
}
.card-title{ font-size:14px; color:#9fc5ff; margin:0 0 8px 0; font-weight:600; }
.kpi { background-color:#171923; padding:8px; border-radius:8px; box-shadow:0 6px 14px rgba(2,6,23,0.5); text-align:center; }
.kpi .label{ color:#9fc5ff; font-size:12px; margin:0; } .kpi .value{ color:#ffffff; font-size:16px; margin:0; font-weight:700; }

/* Pilar card */
.pilar-card{ background-color:#13141a; padding:12px; border-radius:8px; box-shadow:0 6px 16px rgba(2,6,23,0.5); color:#e6eef6; margin-bottom:12px; }
.pilar-title{ color:#8ecae6; margin:0 0 8px 0; font-weight:700; font-size:14px; }
ul.pilar-list{ margin:0; padding-left:18px; } ul.pilar-list li{ margin-bottom:6px; color:#cfe8ff; font-size:13px; }

/* Plot containers: border + shadow + rounded */
.plot-container {
    background: linear-gradient(180deg, rgba(19,20,28,0.6), rgba(16,17,24,0.3));
    border: 1px solid rgba(159,197,255,0.12);
    padding: 12px;
    border-radius: 10px;
    box-shadow: 0 8px 24px rgba(3,6,23,0.6);
    margin-bottom: 16px;
}

/* Make sure Plotly background stays transparent */
.plotly-graph-div {
    background: transparent !important;
}

/* Make text inside cards readable on dark */
.card p, .card h3, .pilar-card h3 { color: #e6eef6; }

/* Small tweaks for responsiveness */
@media (max-width: 800px) {
  .plot-container { padding: 8px; }
}
</style>
""", unsafe_allow_html=True)

# --------------------------
# Dummy data
np.random.seed(42)
divisions = ['Corporate Affairs', 'People & Culture', 'PPC', 'Marketing', 'Operations']
pilars = ['Capability & Leadership', 'Public Affairs', 'Communication', 'Partnerships',
          'Impact Governance', 'Data & Digitalization', 'Performance & Reward', 'Innovation']
priorities = [
    'Priority 1 (Urgent - Important)',
    'Priority 2 (Not Urgent - Important)',
    'Priority 3 (Urgent - Not Important)',
    'HR Priority 1',
    'HR Priority 2',
    'HR Priority 3'
]

dummy_data = []
for i in range(50):
    dummy_data.append({
        'Division': np.random.choice(divisions),
        'Initiative': f'Initiative {i+1}',
        'Pilar': np.random.choice(pilars),
        'PIA': f'PIA {np.random.randint(1,12)}',
        'Priority': np.random.choice(priorities)
    })
df = pd.DataFrame(dummy_data)

# --------------------------
# --------------------------
# Sidebar Filters (expandable + select all per filter, tetap bisa uncheck satu2)
st.sidebar.header("Filters")

# Fungsi bantu Select All untuk session_state
def select_all_toggle(key, options):
    if key not in st.session_state:
        st.session_state[key] = options.copy()
    select_all = st.checkbox(f"Select All {key.replace('_',' ').title()}", value=len(st.session_state[key])==len(options))
    if select_all:
        st.session_state[key] = options.copy()
    # Multiselect dengan value dari session_state
    selected = st.multiselect(key.replace('_',' ').title(), options, default=st.session_state[key])
    st.session_state[key] = selected
    return selected

# --------------------------
# Hierarchical Tree Filters
with st.sidebar.expander("Hierarchical Tree Filters", expanded=True):
    top_node_type = st.radio("Top node type for hierarchy:", ["PIA", "Division", "Priority"])
    
    if top_node_type == "PIA":
        sel_tree_pia = select_all_toggle("PIA (Tree)", sorted(df['PIA'].unique()))
        sel_tree_div = select_all_toggle("Division (Tree)", sorted(df['Division'].unique()))
        tree_df = df[df['PIA'].isin(sel_tree_pia) & df['Division'].isin(sel_tree_div)]
        
    elif top_node_type == "Division":
        sel_tree_div = select_all_toggle("Division (Tree)", sorted(df['Division'].unique()))
        sel_tree_pia = select_all_toggle("PIA (Tree)", sorted(df['PIA'].unique()))
        tree_df = df[df['Division'].isin(sel_tree_div) & df['PIA'].isin(sel_tree_pia)]
        
    else:
        sel_tree_prio = select_all_toggle("Priority (Tree)", sorted(df['Priority'].unique()))
        tree_df = df[df['Priority'].isin(sel_tree_prio)]

# --------------------------
# Other Plots Filters
with st.sidebar.expander("Other Plots Filters", expanded=True):
    sel_plot_div = select_all_toggle("Division (Plots)", sorted(df['Division'].unique()))
    sel_plot_pia = select_all_toggle("PIA (Plots)", sorted(df['PIA'].unique()))
    sel_plot_pilar = select_all_toggle("Pilar (Plots)", sorted(df['Pilar'].unique()))
    sel_plot_prio = select_all_toggle("Priority (Plots)", sorted(df['Priority'].unique()))
    
    plot_df = df[df['Division'].isin(sel_plot_div) &
                 df['PIA'].isin(sel_plot_pia) &
                 df['Pilar'].isin(sel_plot_pilar) &
                 df['Priority'].isin(sel_plot_prio)]

# --------------------------
# Header
st.markdown(
    "<h1 style='color:#9fc5ff;margin-bottom:2px'>Paragon Strategy Visualizer</h1>"
    "<div style='color:#cfe8ff;margin-top:0;margin-bottom:8px'>Interactive hierarchical canvas • KPI • Summary • Pilar cards</div>",
    unsafe_allow_html=True,
)

# --------------------------
# KPI row (compact)
kpi_total_div = df["Division"].nunique()
kpi_total_pia = df["PIA"].nunique()
kpi_total_pilar = df["Pilar"].nunique()
kpi_total_init = df["Initiative"].nunique()

k1, k2, k3, k4 = st.columns(4)
kpi_htmls = [
    ("Total Divisions", kpi_total_div),
    ("Total PIAs", kpi_total_pia),
    ("Unique Pilars", kpi_total_pilar),
    ("Initiatives", kpi_total_init),
]
for col, (label, val) in zip((k1, k2, k3, k4), kpi_htmls):
    html_kpi = f"<div class='kpi'><p class='label'>{label}</p><p class='value'>{val}</p></div>"
    col.markdown(html_kpi, unsafe_allow_html=True)
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# --------------------------
# Hierarchical Tree (Plotly Sunburst) -- DO NOT CHANGE SUNBURST COLORS (per request)
st.subheader("Hierarchical Tree (Interactive)")

if top_node_type == "PIA":
    path = ['PIA','Division','Pilar','Initiative']
    values = None
elif top_node_type == "Division":
    path = ['Division','PIA','Pilar','Initiative']
    values = None
else:
    path = ['Priority','Division','Pilar','Initiative']
    values = None

fig_tree = px.sunburst(
    tree_df,
    path=path,
    values=values,
    color=path[-2] if len(path)>1 else path[0],
    color_continuous_scale='Viridis',  # KEEP default-ish; user asked not to touch sunburst
    hover_data=['Priority','PIA','Division']
)
fig_tree.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='#0f111a', font_color='white')
st.plotly_chart(fig_tree, use_container_width=True)

# --------------------------
# Summary visualizations
st.subheader("Summary Plots")

col1, col2 = st.columns(2)

# We'll use a single-tone blue gradient (dark -> light) for bars and heatmap
single_tone_scale = ['#A8D8FF', '#6EB3FF', '#3D8BFF', '#1860D4', '#0B3270']  # dark-to-light blue

with col1:
    st.markdown("**Count of Pilar per Division**")
    p1 = plot_df.groupby('Division')['Pilar'].nunique().reset_index(name='Count Pilar')

    # Map color to numeric value so bar shows single-tone gradient (dark -> light)
    fig1 = px.bar(
        p1.sort_values('Count Pilar', ascending=True),
        x='Division',
        y='Count Pilar',
        text='Count Pilar',
        color='Count Pilar',
        color_continuous_scale=single_tone_scale,
        template='plotly_dark',
        labels={'Count Pilar': 'Count Pilar'}
    )
    fig1.update_traces(marker_line_width=0)  # cleaner look
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False,
                       margin=dict(t=8, l=8, r=8, b=8))
    # Wrap plot with container that has border + shadow
    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("**Count of PIA per Division**")
    p2 = plot_df.groupby('Division')['PIA'].nunique().reset_index(name='Count PIA')

    fig2 = px.bar(
        p2.sort_values('Count PIA', ascending=True),
        x='Division',
        y='Count PIA',
        text='Count PIA',
        color='Count PIA',
        color_continuous_scale=single_tone_scale,
        template='plotly_dark',
        labels={'Count PIA': 'Count PIA'}
    )
    fig2.update_traces(marker_line_width=0)
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False,
                       margin=dict(t=8, l=8, r=8, b=8))

    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.subheader("Division vs Priority Heatmap")

heat = plot_df.groupby(['Division','Priority']).size().reset_index(name='Count')

# Use a single-tone blue gradient for heatmap too (dark->light)
heat_fig = px.density_heatmap(
    heat,
    x='Division',
    y='Priority',
    z='Count',
    text_auto=True,
    color_continuous_scale=single_tone_scale,
    template='plotly_dark',
    labels={'Count': 'Count'}
)
heat_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       margin=dict(t=6, l=6, r=6, b=6))
# Add container
st.markdown('<div class="plot-container">', unsafe_allow_html=True)
st.plotly_chart(heat_fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --------------------------
# Pilar Card View
# Pilar Card View (update: tampilkan Division tiap Initiative)
st.subheader("Pilar Card View (Initiatives per Pilar)")
pilar_group = plot_df.groupby('Pilar')[['Initiative','Division']].apply(lambda x: x.values.tolist()).reset_index(name='Initiatives')

# Card style lebih elegan dark theme
card_style = """
<div style="
    background: linear-gradient(180deg, #161826, #1f2233);
    padding:18px;
    margin-bottom:18px;
    border-radius:12px;
    box-shadow:0 8px 20px rgba(0,0,0,0.5);
    border:1px solid rgba(100,120,150,0.25);
    transition: transform 0.2s;
">
    <h3 style="color:#4fc3f7;margin-bottom:8px;font-weight:700;font-size:16px">{title}</h3>
    {content}
</div>
"""

# List item style lebih modern
list_style_start = "<ul style='padding-left:20px;margin:0;'>"
list_style_end = "</ul>"
cols = st.columns(2)

for i, (_, row) in enumerate(pilar_group.iterrows()):
    content_html = list_style_start
    # row['Initiatives'] adalah list of [Initiative, Division]
    for init, div in row['Initiatives']:
        content_html += f"<li style='margin-bottom:6px;color:#cfe8ff;font-size:14px;line-height:1.5;'>{init} ({div})</li>"
    content_html += list_style_end
    with cols[i % 2]:
        st.markdown(card_style.format(title=row['Pilar'], content=content_html), unsafe_allow_html=True)

st.subheader("Division Prioritization Overview")

# Pilih kolom untuk ditampilkan
prioritization_df = plot_df[['Division','Pilar','Initiative','Priority']].copy()

# Optional: sorting berdasarkan Priority (Urgent → Less)
priority_order = [
    'Priority 1 (Urgent - Important)',
    'Priority 2 (Not Urgent - Important)',
    'Priority 3 (Urgent - Not Important)',
    'HR Priority 1',
    'HR Priority 2',
    'HR Priority 3'
]
prioritization_df['Priority'] = pd.Categorical(prioritization_df['Priority'], categories=priority_order, ordered=True)
prioritization_df = prioritization_df.sort_values(['Division','Priority'])

# Buat tabel Plotly interaktif
import plotly.graph_objects as go

header_color = '#0f111a'
cell_color = '#1f2233'
font_color = '#e6eef6'

fig_table = go.Figure(data=[go.Table(
    header=dict(
        values=list(prioritization_df.columns),
        fill_color=header_color,
        font=dict(color=font_color, size=14),
        align='center',
        line_color='rgba(255,255,255,0.2)',
        height=32
    ),
    cells=dict(
        values=[prioritization_df[col] for col in prioritization_df.columns],
        fill_color=cell_color,
        font=dict(color=font_color, size=13),
        align='left',
        line_color='rgba(255,255,255,0.1)',
        height=28
    )
)])

# Layout tambahan (border + shadow efek)
fig_table.update_layout(
    margin=dict(l=0, r=0, t=10, b=10),
    paper_bgcolor='#0f111a',
    plot_bgcolor='#0f111a',
    height=400
)

# Tampilkan di Streamlit dengan container elegan
st.markdown('<div style="padding:10px; border-radius:12px; background:#13141a; box-shadow:0 6px 18px rgba(0,0,0,0.5); border:1px solid rgba(159,197,255,0.12)">', unsafe_allow_html=True)
st.plotly_chart(fig_table, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
