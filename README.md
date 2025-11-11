Microsoft Teams Need help? 
Join the meeting now 
Meeting ID: 256 090 917 241 4 
Passcode: ts2gG2P7 
________________________________________
Dial in by phone 
+1 860-785-9736,,888760307# United States, Hartford 
Find a local number 
Phone conference ID: 888 760 307# 
Join on a video conferencing device 
Tenant key: 330319201@t.plcm.vc 
Video ID: 114 528 109 8 
More info 


import pandas as pd
import plotly.graph_objects as go
import glob
import os
from datetime import datetime, timedelta
from dash import Dash, dcc, html, Input, Output, State, callback_context
import base64

# === CONFIGURATION ===
folder_path = "path_to_folder"  # Replace with your folder path containing YYYYMMDD.xlsx files
promising_file = "promising-companies.xlsx"  # Replace with actual path if available

# === STEP 1: Load promising companies if file exists ===
promising_companies = []
if os.path.exists(promising_file):
    try:
        prom_df = pd.read_excel(promising_file, engine="openpyxl")
        if 'Company' in prom_df.columns:
            promising_companies = prom_df['Company'].dropna().unique().tolist()
    except Exception as e:
        print(f"Error reading promising companies file: {e}")

# === STEP 2: Load all Excel files and build index of companies ===
all_files = glob.glob(os.path.join(folder_path, "*.xlsx"))
dfs = []
for file in all_files:
    base_name = os.path.basename(file)
    date_str = os.path.splitext(base_name)[0]
    try:
        file_date = datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        continue
    temp_df = pd.read_excel(file, engine="openpyxl")
    temp_df['Date'] = file_date
    dfs.append(temp_df)

df = pd.concat(dfs).sort_values('Date') if dfs else pd.DataFrame()
companies = sorted(df['Company'].unique()) if not df.empty else []

# === DASH APP ===
app = Dash(__name__)
app.title = "Interactive OHLC Chart"

app.layout = html.Div([
    html.H2("Interactive OHLC with Volume & Delivery"),
    html.Div([
        html.Label("Select Company:"),
        dcc.Dropdown(
            id='company-dropdown',
            options=[{'label': c, 'value': c} for c in companies],
            placeholder='Type or select a company...',
            searchable=True,
            clearable=True
        )
    ], style={'margin-bottom': '20px', 'width': '50%'}),
    html.Div([
        html.Button("Back", id='back-btn', n_clicks=0),
        html.Button("Next", id='next-btn', n_clicks=0, style={'margin-left': '10px'}),
        html.Button("Toggle Range Slider", id='toggle-slider', n_clicks=0, style={'margin-left': '10px'}),
        html.Button("Toggle Dark Mode", id='toggle-dark', n_clicks=0, style={'margin-left': '10px'}),
        html.Button("Export PNG", id='export-png', n_clicks=0, style={'margin-left': '10px'}),
        html.Button("Export HTML", id='export-html', n_clicks=0, style={'margin-left': '10px'})
    ], style={'margin-bottom': '20px'}),
    dcc.Graph(id='ohlc-chart', style={'height': '800px'}),
    html.Div(id='download-link', style={'margin-top': '20px'}),
    html.Div(id='notification', style={'margin-top': '10px', 'color': 'green'}),
    dcc.Store(id='current-index', data=0),
    dcc.Store(id='loaded-companies', data=promising_companies)
])

# === Navigation Callback ===
@app.callback(
    Output('current-index', 'data'),
    Input('next-btn', 'n_clicks'),
    Input('back-btn', 'n_clicks'),
    State('current-index', 'data'),
    State('loaded-companies', 'data')
)
def navigate(next_clicks, back_clicks, current_index, loaded_companies):
    ctx = callback_context
    if not loaded_companies:
        return current_index
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'next-btn':
            current_index = (current_index + 1) % len(loaded_companies)
        elif button_id == 'back-btn':
            current_index = (current_index - 1) % len(loaded_companies)
    return current_index

# === Chart Update Callback ===
@app.callback(
    Output('ohlc-chart', 'figure'),
    Output('notification', 'children'),
    Input('company-dropdown', 'value'),
    Input('current-index', 'data'),
    Input('toggle-slider', 'n_clicks'),
    Input('toggle-dark', 'n_clicks'),
    State('loaded-companies', 'data')
)
def update_chart(selected_company, current_index, toggle_slider_clicks, toggle_dark_clicks, loaded_companies):
    notification = ""
    slider_visible = (toggle_slider_clicks % 2 == 1)
    dark_mode = (toggle_dark_clicks % 2 == 1)
    template = 'plotly_dark' if dark_mode else 'plotly_white'

    # Determine company to show
    if selected_company:
        company = selected_company
        if company not in loaded_companies:
            notification = f"Loading data for {company} in background..."
            loaded_companies.append(company)  # Simulate lazy load
    elif loaded_companies:
        company = loaded_companies[current_index]
    else:
        fig = go.Figure(layout=go.Layout(title="No data available", template=template))
        return fig, "No promising companies loaded."

    # Filter data for company
    if df.empty or company not in df['Company'].unique():
        fig = go.Figure(layout=go.Layout(title=f"No data for {company}", template=template))
        return fig, notification

    company_df = df[df['Company'] == company].copy()
    company_df['DeliveryPct'] = (company_df['Delivery'] / company_df['Volume']) * 100

    candlestick = go.Candlestick(
        x=company_df['Date'],
        open=company_df['Open'],
        high=company_df['High'],
        low=company_df['Low'],
        close=company_df['Close'],
        name='OHLC'
    )

    volume_bar = go.Bar(
        x=company_df['Date'],
        y=company_df['Volume'],
        name='Volume',
        marker_color='rgba(50,150,255,0.6)',
        yaxis='y2'
    )

    delivery_bar = go.Bar(
        x=company_df['Date'],
        y=company_df['Delivery'],
        name='Delivery',
        marker_color='rgba(0,200,100,0.8)',
        yaxis='y2'
    )

    last_week_start = datetime.now() - timedelta(days=7)
    shapes = []
    if company_df['Date'].min() < last_week_start:
        shapes.append(dict(
            type="rect",
            xref="x",
            yref="paper",
            x0=company_df['Date'].min(),
            x1=last_week_start,
            y0=0,
            y1=1,
            fillcolor="lightgray",
            opacity=0.3,
            layer="below",
            line_width=0
        ))

    layout = go.Layout(
        title=f"OHLC with Volume & Delivery for {company}",
        template=template,
        xaxis=dict(title="Date", rangeslider=dict(visible=slider_visible)),
        yaxis=dict(title="Price", domain=[0.4, 1]),
        yaxis2=dict(title="Volume & Delivery", domain=[0, 0.35], anchor="x"),
        hovermode="x unified",
        barmode='overlay',
        shapes=shapes,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig = go.Figure(data=[candlestick, volume_bar, delivery_bar], layout=layout)
    return fig, notification

# === Export Callback ===
@app.callback(
    Output('download-link', 'children'),
    Input('export-png', 'n_clicks'),
    Input('export-html', 'n_clicks'),
    State('ohlc-chart', 'figure')
)
def export_chart(png_clicks, html_clicks, fig_dict):
    ctx = callback_context
    if not ctx.triggered:
        return ""
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    fig = go.Figure(fig_dict)
    if button_id == 'export-png' and png_clicks > 0:
        img_bytes = fig.to_image(format="png")
        encoded = base64.b64encode(img_bytes).decode()
        return html.A("Download PNG", href=f"data:image/png;base64,{encoded}", download="ohlc_chart.png")
    elif button_id == 'export-html' and html_clicks > 0:
        html_str = fig.to_html()
        encoded = base64.b64encode(html_str.encode()).decode()
        return html.A("Download HTML", href=f"data:text/html;base64,{encoded}", download="ohlc_chart.html")
    return ""

if __name__ == '__main__':
    app.run(debug=True)
