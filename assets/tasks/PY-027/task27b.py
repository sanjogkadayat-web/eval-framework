import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-027 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def _score_quantiles(s: pd.Series, ascending: bool = True, buckets: int = 4) -> pd.Series:
    if s.isna().all():
        return pd.Series([pd.NA] * len(s), index=s.index, dtype="Int64")

    ranks = s.rank(method="average", ascending=ascending)
    scores = pd.qcut(ranks, q=buckets, labels=False, duplicates="drop")
    if scores is None:
        return pd.Series([pd.NA] * len(s), index=s.index, dtype="Int64")
    return (scores.astype("Int64") + 1).astype("Int64")


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"], errors="coerce")
    transactions_df["txn_amount"] = pd.to_numeric(transactions_df["txn_amount"], errors="coerce")

    tx = transactions_df.dropna(subset=["account_id"]).copy()
    if tx.empty:
        return pd.DataFrame(
            columns=[
                "account_id",
                "recency_days",
                "frequency",
                "monetary",
                "r_score",
                "f_score",
                "m_score",
                "rfm_score",
            ]
        )

    max_date = tx["txn_date"].max()
    agg = (
        tx.groupby("account_id", dropna=False)
        .agg(
            last_txn_date=("txn_date", "max"),
            frequency=("txn_id", "count"),
            monetary=("txn_amount", "sum"),
        )
        .reset_index()
    )

    agg["recency_days"] = (max_date - agg["last_txn_date"]).dt.days

    agg["r_score"] = _score_quantiles(agg["recency_days"], ascending=False)
    agg["f_score"] = _score_quantiles(agg["frequency"], ascending=True)
    agg["m_score"] = _score_quantiles(agg["monetary"], ascending=True)

    agg["rfm_score"] = (
        agg["r_score"].astype("Int64") * 100
        + agg["f_score"].astype("Int64") * 10
        + agg["m_score"].astype("Int64")
    )

    return agg[
        ["account_id", "recency_days", "frequency", "monetary", "r_score", "f_score", "m_score", "rfm_score"]
    ]
