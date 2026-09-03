from nuteval.config import MODELS, NUTRIENT_FIELDS
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


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
        template="plotly_white",
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
