from pathlib import Path
import pandas as pd

PROJECT_FOLDER = Path(__file__).resolve().parent

Listings = pd.read_csv(
    PROJECT_FOLDER / "data" / "Listings.csv",
    encoding="ISO-8859-1",
    low_memory=False,
    parse_dates=["host_since"]
)

paris_Listings = Listings.loc[
    Listings["city"].str.strip().str.lower().eq("paris").fillna(False),
    ["host_since", "neighbourhood", "city", "accommodates", "price"]
]

print("Number of Paris listings:", len(paris_Listings))
print(paris_Listings.head())
paris_Listings.info()

print(paris_Listings.isna().sum())

print("\nSummary statistics:")
print(paris_Listings.describe())

print(paris_Listings.query("price == 0 and accommodates == 0"))

paris_Listings_neighbourhood = (
    paris_Listings
    .groupby("neighbourhood")
    .agg({"price": "mean"})
    .sort_values("price")
)

print(paris_Listings_neighbourhood.tail())

paris_Listings_accommodates = (
    paris_Listings
    .query("neighbourhood == 'Elysee'")
    .groupby("accommodates")
    .agg({"price": "mean"})
    .sort_values("price")
)
print(paris_Listings_accommodates.tail())

paris_Listings_over_time = (
    paris_Listings
    .set_index("host_since")
    .resample("YE")
    .agg({
        "neighbourhood": "count",
        "price": "mean"
        })
)

print(paris_Listings_over_time.head())


import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter, MaxNLocator
from pathlib import Path

# Consistent, smaller text
sns.set_theme(
    style="whitegrid",
    context="notebook",
    font_scale=0.85
)

plt.rcParams.update({
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9
})

plt.close("all")

# ONE figure: all five charts in the original arrangement
fig = plt.figure(figsize=(20, 17))

grid = fig.add_gridspec(
    nrows=3,
    ncols=2,
    height_ratios=[2.2, 1, 1.2]
)

ax1 = fig.add_subplot(grid[0, 0])
ax2 = fig.add_subplot(grid[0, 1])
ax3 = fig.add_subplot(grid[1, 0])
ax4 = fig.add_subplot(grid[1, 1])
ax5 = fig.add_subplot(grid[2, :])

fig.suptitle(
    "Paris Airbnb | Prices and Host-Start-Year Analysis",
    fontsize=18,
    fontweight="bold",
    y=0.985
)

green = "#278575"
blue = "#4472C4"

# --------------------------------------------------
# Chart 1: Average price by neighbourhood
# --------------------------------------------------
paris_Listings_neighbourhood["price"].sort_values().plot.barh(
    ax=ax1,
    color=green,
    width=0.65
)

ax1.set_title("Average Price by Paris Neighbourhood", pad=12)
ax1.set_xlabel("Average price per night (€)")
ax1.set_ylabel("")
ax1.set_xlim(left=0)
ax1.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
ax1.tick_params(axis="y", labelsize=8)

ax1.grid(axis="x", alpha=0.25)
ax1.grid(axis="y", visible=False)

sns.despine(ax=ax1)

# --------------------------------------------------
# Chart 2: Average price by capacity in Elysee
# --------------------------------------------------
paris_Listings_accommodates.sort_index()["price"].plot.barh(
    ax=ax2,
    color=blue,
    width=0.65
)

ax2.set_title("Average Price by Guest Capacity | Elysee", pad=12)
ax2.set_xlabel("Average price per night (€)")
ax2.set_ylabel("Guest capacity")
ax2.set_xlim(left=0)
ax2.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

ax2.grid(axis="x", alpha=0.25)
ax2.grid(axis="y", visible=False)

sns.despine(ax=ax2)

# --------------------------------------------------
# Annual series
# --------------------------------------------------
years = paris_Listings_over_time.index.year
average_prices = paris_Listings_over_time["price"]
listing_counts = paris_Listings_over_time["neighbourhood"]

# --------------------------------------------------
# Chart 3: Average price by host-start year
# --------------------------------------------------
ax3.plot(
    years,
    average_prices,
    color=blue,
    marker="o",
    markersize=5,
    linewidth=2
)

ax3.set_title("Average Price by Host-Start Year", pad=12)
ax3.set_xlabel("Host-start year")
ax3.set_ylabel("Average price (€)")
ax3.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

ax3.grid(axis="y", alpha=0.25)
ax3.grid(axis="x", visible=False)

sns.despine(ax=ax3)

# --------------------------------------------------
# Chart 4: Listing count by host-start year
# --------------------------------------------------
ax4.plot(
    years,
    listing_counts,
    color=green,
    marker="o",
    markersize=5,
    linewidth=2
)

ax4.set_title("Listing Count by Host-Start Year", pad=12)
ax4.set_xlabel("Host-start year")
ax4.set_ylabel("Number of listings")
ax4.set_ylim(bottom=0)
ax4.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

ax4.grid(axis="y", alpha=0.25)
ax4.grid(axis="x", visible=False)

sns.despine(ax=ax4)

# --------------------------------------------------
# Chart 5: Combined listing count and average price
# --------------------------------------------------
count_line, = ax5.plot(
    years,
    listing_counts,
    color=green,
    marker="o",
    markersize=5,
    linewidth=2,
    label="Number of listings"
)

ax5.set_title(
    "Listing Count and Average Price by Host-Start Year",
    pad=32
)

ax5.set_xlabel("Host-start year")
ax5.set_ylabel("Number of listings", color=green)
ax5.tick_params(axis="y", labelcolor=green)
ax5.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
ax5.set_ylim(bottom=0)

ax5.grid(axis="y", alpha=0.25)
ax5.grid(axis="x", visible=False)

# Right-hand price axis
ax5_price = ax5.twinx()

price_line, = ax5_price.plot(
    years,
    average_prices,
    color=blue,
    marker="o",
    markersize=5,
    linewidth=2,
    label="Average price"
)

ax5_price.set_ylabel("Average price (€)", color=blue)
ax5_price.tick_params(axis="y", labelcolor=blue)
ax5_price.yaxis.set_major_formatter(
    StrMethodFormatter("{x:,.0f}")
)
ax5_price.set_ylim(bottom=0)
ax5_price.grid(False)

# Place the legend above the plot so it does not cover the lines
ax5.legend(
    handles=[count_line, price_line],
    loc="lower center",
    bbox_to_anchor=(0.5, 1.01),
    ncol=2,
    frameon=False,
    fontsize=9
)

ax5.spines["top"].set_visible(False)
ax5_price.spines["top"].set_visible(False)

# --------------------------------------------------
# Fewer year labels, with no rotation
# --------------------------------------------------
for ax in [ax3, ax4, ax5]:
    ax.xaxis.set_major_locator(
        MaxNLocator(nbins=7, integer=True)
    )
    ax.tick_params(axis="x", rotation=0)
    ax.margins(x=0.03)

# Space around and between the five panels
fig.subplots_adjust(
    left=0.16,
    right=0.91,
    top=0.88,
    bottom=0.13,
    wspace=0.42,
    hspace=0.90
)

# Portfolio interpretation note
fig.text(
    0.53,
    0.025,
    "Annual charts group listings by their hosts' start year; "
    "they do not measure historical prices or unique new hosts.",
    ha="center",
    va="bottom",
    fontsize=8,
    color="#555555",
    linespacing=1.5
)

# --------------------------------------------------
# Export the complete five-chart dashboard
# --------------------------------------------------
output_folder = PROJECT_FOLDER / "outputs"
output_folder.mkdir(parents=True, exist_ok=True)

fig.savefig(
    output_folder / "Paris_Airbnb_Dashboard.png",
    dpi=200,
    bbox_inches="tight",
    facecolor="white"
)

fig.savefig(
    output_folder / "Paris_Airbnb_Dashboard.svg",
    bbox_inches="tight",
    facecolor="white"
)

print("\nFive-chart dashboard saved to:", output_folder)

plt.show()