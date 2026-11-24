"""Plotly visualization heuristics for tabular SQL analytics results."""

from typing import List, Dict, Any, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def generate_auto_chart(data: List[Dict[str, Any]]) -> Optional[go.Figure]:
    """Inspect tabular query output and generate the most informative Plotly chart."""
    if not data or len(data) == 0:
        return None

    df = pd.DataFrame(data)

    # Clean date / datetime objects to strings if needed
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].astype(str)

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and c.lower() != "id"]
    non_numeric_cols = [c for c in df.columns if c not in numeric_cols and c.lower() != "id"]

    if not numeric_cols:
        return None

    val_col = numeric_cols[0]

    # Heuristic 1: Time Series or Date based ordering -> Line or Bar Chart
    date_cols = [c for c in non_numeric_cols if any(k in c.lower() for k in ["date", "time", "day", "month", "year"])]
    if date_cols:
        time_col = date_cols[0]
        fig = px.line(
            df,
            x=time_col,
            y=val_col,
            title=f"Trend Analysis: {val_col.replace('_', ' ').title()} by {time_col.replace('_', ' ').title()}",
            markers=True,
            template="plotly_white"
        )
        fig.update_layout(xaxis_tickangle=-45, height=450)
        return fig

    # Heuristic 2: Categorical + Numeric -> Bar Chart or Pie Chart
    if non_numeric_cols:
        cat_col = non_numeric_cols[0]
        if len(df) <= 7:
            # Pie/Donut Chart for small categorical cardinality
            fig = px.pie(
                df,
                names=cat_col,
                values=val_col,
                title=f"Distribution: {val_col.replace('_', ' ').title()} across {cat_col.replace('_', ' ').title()}",
                hole=0.4,
                template="plotly_white"
            )
            fig.update_layout(height=450)
            return fig
        else:
            # Bar Chart
            fig = px.bar(
                df,
                x=cat_col,
                y=val_col,
                title=f"{val_col.replace('_', ' ').title()} by {cat_col.replace('_', ' ').title()}",
                color=val_col,
                color_continuous_scale="Viridis",
                template="plotly_white"
            )
            fig.update_layout(xaxis_tickangle=-45, height=450)
            return fig

    # Heuristic 3: Only Numeric Columns -> Single Index Bar Chart
    fig = px.bar(
        df,
        y=val_col,
        title=f"Metric Distribution: {val_col.replace('_', ' ').title()}",
        template="plotly_white"
    )
    fig.update_layout(height=420)
    return fig
