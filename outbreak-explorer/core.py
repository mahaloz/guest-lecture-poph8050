"""Explicit data interpretation and aggregation, independent of the UI."""
import io
import pandas as pd

CSV_URL = "https://casey891.github.io/hpai-dashboard/data/poultry_detections.csv"
APHIS_URL = "https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections/commercial-backyard-flocks"
STATE_CODES = dict(zip(
    "Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming".split("|"),
    "AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split()))


def parse_data(raw):
    df = pd.read_csv(io.BytesIO(raw))
    required = {"Date", "State", "County", "Operation Type", "Birds Impacted"}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing source columns: {required - set(df.columns)}")
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y", errors="raise")
    if df.empty or df[["Date", "State", "Operation Type"]].isna().any().any():
        raise ValueError("Source has no rows or missing required date/state/operation values.")
    df["Birds Impacted"] = pd.to_numeric(df["Birds Impacted"], errors="raise")
    if (df["Birds Impacted"].dropna() < 0).any():
        raise ValueError("Negative affected-bird counts in source.")
    df = df.loc[df["Date"] >= "2022-01-01"].copy()
    df["Month"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    df["Category"] = df["Operation Type"].map(
        lambda x: "Commercial (explicit label)" if x.startswith("Commercial ")
        else "Other source labels (backyard not identified)"
    )
    return df


def aggregate(df, group):
    return df.groupby(group).agg(
        Detections=("Date", "size"),
        Birds=("Birds Impacted", lambda s: s.sum(min_count=1)),
        Missing_birds=("Birds Impacted", lambda s: s.isna().sum()),
    ).reset_index()


def monthly(df, months):
    result = aggregate(df, "Month").set_index("Month").reindex(months)
    # Only months without any detections get zero; missing bird counts remain missing.
    empty = result["Detections"].isna()
    result.loc[empty, ["Detections", "Birds", "Missing_birds"]] = 0
    return result.rename_axis("Month").reset_index()


def map_window(df, month, cumulative):
    return df.loc[df["Month"] <= month] if cumulative else df.loc[df["Month"] == month]
