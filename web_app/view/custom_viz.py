import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st


colors = ['#3792d7fc', '#ed1f91']

def visualize_piechart(labels=None, values=None, 
                       explode=(0, 0.05), colors=colors, var=None):

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                pull=explode,
                marker=dict(
                    colors=colors,
                    line=dict(color='#000000', width=2)
                )
            )
        ]
    )

    fig.update_layout(
        legend=dict(
            x=0.5, y=1.15,
            xanchor='center',
            orientation='h',
            bgcolor='rgba(211,211,211,0.3)',
            font=dict(size=12)
        ),
        title=dict(text=f"{var} Distribution", x=0.05, y=0.95)
    )
    

    return fig


def visualize_histogram(
    df=None,
    x=None,
    hue=None,
    nbins=20,
    colors=None,
    title=None
):
    """
    Visualize a histogram using Plotly GO.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataset containing the columns to visualize.
    x : str
        Column to be plotted on the X-axis.
    hue : str, optional
        Categorical column used to separate histogram by groups.
    nbins : int, optional
        Number of bins for the histogram.
    colors : list, optional
        List of colors to assign to each group. Works like color_discrete_sequence in Plotly Express.
    title : str, optional
        Title of the histogram chart.

    Returns
    -------
    plotly.graph_objects.Figure
        The generated histogram figure.
    """

    if df is None or x is None:
        raise ValueError("`df` and `x` must not be None.")

    # Default colors if not provided
    if colors is None:
        colors = ['#a2b4fc', '#ed1f91']

    fig = go.Figure()

    # Case 1: No hue
    if hue is None:
        fig.add_trace(
            go.Histogram(
                x=df[x],
                nbinsx=nbins,
                marker=dict(color=colors[0])
            )
        )
    else:
        # Case 2: Histogram by categories
        unique_classes = df[hue].dropna().unique()

        for i, cls in enumerate(unique_classes):
            fig.add_trace(
                go.Histogram(
                    x=df[df[hue] == cls][x],
                    name=str(cls),
                    nbinsx=nbins,
                    marker=dict(color=colors[i % len(colors)])
                )
            )

    # Update layout
    fig.update_layout(
        title=dict(
            text=title or f"Distribution of {x}" + (f" by {hue}" if hue else ""),
            x=0.5,
            xanchor="center",
            font=dict(size=16)
        ),
        barmode="overlay",
        #bargap=0,
        #bargroupgap=0,
        #plot_bgcolor="white",
        xaxis=dict(title=x),
        yaxis=dict(title="Count"),
        legend=dict(
            title=hue if hue else "",
            bgcolor="rgba(211,211,211,0.2)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1
        )
        
    )
    # Reduce opacity to see both histograms
    fig.update_traces(opacity=0.75)
    # Remove gridlines
    #fig.update_xaxes(showgrid=False)
    #fig.update_yaxes(showgrid=False)

    return fig


def visualize_boxplot(df=None, x=None, y=None, hue=None, colors=None, var=None):
    """
    Create a boxplot using Plotly Express (seaborn-style).
    - df: DataFrame
    - x: categorical column
    - y: numeric column
    - hue: grouping column (like seaborn's hue)
    - colors: list of colors
    - var: title
    """

    if df is None or y is None:
        return None

    fig = px.box(
        df,
        x=x,
        y=y,
        color=hue,
        color_discrete_sequence=colors,
        points="outliers",      
        title=f"{var if var else y} Distribution"
    )

    fig.update_layout(
        boxmode="overlay",         
        xaxis_title=x,
        yaxis_title=y,
        legend_title=hue,
        title=dict(text=f"{var} Distribution", x=0.05, y=0.95)
    )

    return fig

def visualize_histogram_with_boxplot(
    df=None,
    x=None,
    hue=None,
    nbins=20,
    colors=None,
    title=None
):
    """
    Visualize a boxplot on top and histogram below using Plotly GO subplots.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataset containing the columns to visualize.
    x : str
        Column to be plotted.
    hue : str, optional
        Categorical column for grouping.
    nbins : int, optional
        Number of histogram bins.
    colors : list, optional
        Colors for traces (acts like color_discrete_sequence).
    title : str, optional
        Chart title.

    Returns
    -------
    plotly.graph_objects.Figure
        The combined subplot figure.
    """

    if df is None or x is None:
        raise ValueError("`df` and `x` must not be None.")

    if colors is None:
        colors = ['#a2b4fc', '#ed1f91']

    # Create subplot layout (2 rows: boxplot + histogram)
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.3, 0.7]
    )

    # Case 1: No hue
    if hue is None:
        # --- Boxplot (legend OFF) ---
        fig.add_trace(
            go.Box(
                x=df[x],
                marker_color=colors[0],
                name="Distribution",
                boxmean=True,
                 notched=True, # used notched shape
                legendgroup="main",
                showlegend=False  # prevent duplicate legend
            ),
            row=1, col=1
        )

        # --- Histogram (legend ON) ---
        fig.add_trace(
            go.Histogram(
                x=df[x],
                nbinsx=nbins,
                opacity=0.75,
                marker_color=colors[0],
                name="Distribution",
                legendgroup="main"
            ),
            row=2, col=1
        )

    else:
        # Case 2: Grouped by categories
        unique_classes = df[hue].dropna().unique()

        for i, cls in enumerate(unique_classes):
            group_color = colors[i % len(colors)]
            group_data = df[df[hue] == cls][x]

            # --- Boxplot (legend OFF)---
            fig.add_trace(
                go.Box(
                    x=group_data,
                    name=str(cls),
                    marker_color=group_color,
                    boxmean=True,
                    notched=True, # used notched shape
                    legendgroup=str(cls),
                    showlegend=False      # <–– hide duplicate
                ),
                row=1, col=1
            )

            # --- Histogram (legend ON)---
            fig.add_trace(
                go.Histogram(
                    x=group_data,
                    name=str(cls),
                    nbinsx=nbins,
                    opacity=0.75,
                    marker_color=group_color,
                    legendgroup=str(cls)  # link with boxplot
                ),
                row=2, col=1
            )

    # Layout
    fig.update_layout(
        title=dict(
            text=title or f"{x} Distribution" + (f" by {hue}" if hue else ""),
            x=0.5,
            xanchor="center",
            font=dict(size=16)
        ),
        barmode="overlay",
        legend=dict(
            title=hue if hue else "",
            bgcolor="rgba(211,211,211,0.2)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1
        )
    )

    # Labels
    fig.update_xaxes(title_text=x, row=2, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=1)

    # Row 1 (boxplot) => grid ON
    #fig.update_yaxes(showgrid=True, gridcolor="lightgray", row=1, col=1)
    fig.update_xaxes(showgrid=True, gridcolor="rgba(180,180,180,0.2)",gridwidth=0.1, row=1, col=1)
    return fig

def kpi_card(title, value, icon="📊"):
    st.markdown(
        f"""
        <div style="
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            text-align: center;
            border: 1px solid #f0f0f0;
        ">
            <div style="font-size: 28px;">{icon}</div>
            <div style="font-size: 14px; color: #555; margin-top: 4px;">{title}</div>
            <div style="font-size: 32px; font-weight: bold; color: #111; margin-top: 6px;">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def visualize_barchart(df=None, x=None, y=None, hue=None, colors=None, var=None, orientation="v"):
    """
    Create a bar chart using Plotly Express.
    
    Parameters:
    - df: pandas DataFrame
    - x: categorical column (or horizontal if orientation='h')
    - y: numeric column (value)
    - hue: grouping column (optional, like seaborn's hue)
    - colors: list of colors
    - var: title / variable name
    - orientation: "v" (vertical) or "h" (horizontal)
    
    Returns:
    - Plotly Figure object
    """
    if df is None or x is None or y is None:
        return None

    fig = px.bar(
        df,
        x=x if orientation=="v" else y,
        y=y if orientation=="v" else x,
        color=hue,
        color_discrete_sequence=colors,
        orientation=orientation
    )

    fig.update_layout(
        xaxis_title=x,
        yaxis_title=y,
        legend_title=hue,
        title=dict(text=f"{var}", x=0.05, y=0.95)
    )

    return fig


