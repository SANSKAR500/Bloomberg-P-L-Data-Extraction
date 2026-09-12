"""
Builds RevBySegment.csv from the REV BY SEGMENT sheet of the original
Bloomberg extract workbook. Same cleaning pattern as clean_extract.py:
strip commas, drop the duplicated 'Footwear' row, tidy to long form.
"""
import openpyxl
import pandas as pd

YEARS = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]

wb = openpyxl.load_workbook(
    "/mnt/user-data/uploads/ADS_GY_Equity_Bloomberg_Extract_SYNTHETIC.xlsx",
    data_only=True,
)
ws = wb["REV BY SEGMENT"]

SECTIONS = {
    7: ("category", "Footwear"),
    8: ("category", "Apparel"),
    9: ("category", "Acc. & Gear"),
    # row 10 is a duplicate Footwear row (extraction glitch) -- skipped
    14: ("brand", "adidas"),
    15: ("brand", "Reebok"),
    19: ("channel", "Wholesale"),
    20: ("channel", "Retail"),
    21: ("channel", "Other Businesses"),
}


def to_num(v):
    if v is None:
        return None
    v = str(v).strip()
    if v in ("", "—", "-", "#N/A N/A", "NM"):
        return None
    return float(v.replace(",", ""))


rows = []
for r, (dim, name) in SECTIONS.items():
    for i, y in enumerate(YEARS):
        val = to_num(ws.cell(r, 3 + i).value)
        rows.append({"dimension": dim, "segment": name, "fiscal_year": y, "value": val})

df = pd.DataFrame(rows)
df.to_csv("RevBySegment.csv", index=False)
print(df)
print(f"\n{len(df)} rows exported")

# quick reconciliation vs Total Net Revenue, same as clean_extract.py
for dim in ["category", "brand", "channel"]:
    sub = df[df.dimension == dim].pivot(index="fiscal_year", columns="segment", values="value")
    totals = sub.sum(axis=1)
    print(f"\n{dim} sums by year:")
    print(totals)
