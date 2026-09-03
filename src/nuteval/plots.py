from nuteval.config import NUTRIENT_FIELDS
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


COLOR_PALETTE = px.colors.qualitative.Set2
PLOTLY_TEMPLATE = "plotly_white"


def plot_mean_ape_per_model_and_nutrient(df: pd.DataFrame) -> go.Figure:
    """Bar chart of mean absolute % error per model and nutrient."""
    ape_cols = [f"{n}_ape" for n in NUTRIENT_FIELDS]

    # One row per (model, run, nutrient)
    long_df = df.melt(
        id_vars=["model_name"],
        value_vars=ape_cols,
        var_name="nutrient",
        value_name="ape"
    )
    long_df["nutrient"] = long_df["nutrient"].str.replace("_ape", "", regex=False)

    # Mean APE per model per nutrient (NaNs / zero-gt excluded)
    summary = (
        long_df.groupby(["nutrient", "model_name"], as_index=False)["ape"]
        .mean()
        .rename(columns={"ape": "mean_ape"})
    )

    # Order models by mean APE (best -> worst)
    model_order = (
        summary.groupby("model_name")["mean_ape"]
        .mean()
        .sort_values()
        .index.tolist()
    )

    fig = px.bar(
        summary,
        x="model_name",
        y="mean_ape",
        facet_col="nutrient",
        facet_col_wrap=4,
        category_orders={"model_name": model_order},
        color="model_name",
        text=summary["mean_ape"].round(1),
        title="Mean Absolute % Error by Model, per Nutrient",
        labels={"mean_ape": "Mean APE (%)", "model_name": "Model"},
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=COLOR_PALETTE,
    )

    fig.update_yaxes(matches=None, showticklabels=True)
    fig.update_xaxes(showticklabels=False, title_text="")
    fig.for_each_annotation(
        lambda a: a.update(text=a.text.split("=")[-1], y=-0.12, yanchor="top")
    )
    fig.update_layout(
        title_x=0.5,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
        ),
        margin=dict(t=100, r=160),
    )

    return fig


def plot_error_distribution_per_model(df: pd.DataFrame, nutrient: str = "calories") -> go.Figure:
    """Box plot of % error distribution per model, for a single nutrient."""
    pct_col = f"{nutrient}_pct_err"
    ape_col = f"{nutrient}_ape"

    plot_df = df[["model_name", "meal_id", pct_col, ape_col]].dropna(subset=[pct_col])

    # Order models by median APE (best -> worst)
    model_order = (
        plot_df.groupby("model_name")[ape_col]
        .median()
        .sort_values()
        .index.tolist()
    )

    fig = px.box(
        plot_df,
        x="model_name",
        y=pct_col,
        color="model_name",
        category_orders={"model_name": model_order},
        points="all",
        hover_data={"meal_id": True, "model_name": False, pct_col: ":.1f"},
        title=f"Error Distribution by Model — {nutrient.capitalize()}",
        labels={pct_col: "% Error (pred - gt)", "model_name": "Model"},
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=COLOR_PALETTE,
    )

    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)

    fig.update_traces(
        boxmean=True,
        jitter=0.4,
        pointpos=0,
        marker=dict(size=4, opacity=0.7),
    )

    fig.update_layout(
        title_x=0.5,
        showlegend=True,
        xaxis_title=None,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            title_text="",
        ),
        margin=dict(t=80, b=100),
    )

    return fig
