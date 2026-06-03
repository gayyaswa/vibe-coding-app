import plotly.graph_objects as go


def apply_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="#F0F4F8",
        plot_bgcolor="#FFFFFF",
        font_color="#1A1A2E",
    )
    return fig
