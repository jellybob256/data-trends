from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime
import os
import time

# ---------- CONFIG ----------
KEYWORDS = [
    "slow morning",
    "cozy desk",
    "digital journaling",
    "clean girl aesthetic",
    "soft productivity",
    "morning routine aesthetic",
    "self care routine",
    "soft girl aesthetic", 
    "yogurt bowl"
]

BATCH_SIZE = 5          # Google allows max 5 keywords per request
SAVE_DIR = "data/google_trends"
GEO = "US"
TIMEFRAME = "today 12-m"
WAIT_BETWEEN_REQUESTS = 2  # seconds

# ---------- SETUP ----------
os.makedirs(SAVE_DIR, exist_ok=True)
pytrends = TrendReq(hl='en-US', tz=360, retries=2, backoff_factor=0.5)

all_data = []

# ---------- PROCESS IN BATCHES ----------
for i in range(0, len(KEYWORDS), BATCH_SIZE):
    batch = KEYWORDS[i:i+BATCH_SIZE]
    try:
        pytrends.build_payload(batch, timeframe=TIMEFRAME, geo=GEO, gprop="")
        data = pytrends.interest_over_time()
        if "isPartial" in data.columns:
            data = data.drop(columns=["isPartial"])
        all_data.append(data)
        print(f"✅ Fetched batch: {batch}")
    except Exception as e:
        print(f"❌ Error fetching batch {batch}: {e}")
    time.sleep(WAIT_BETWEEN_REQUESTS)  # avoid Google rate-limiting

# ---------- MERGE ALL BATCHES ----------
if all_data:
    merged_data = pd.concat(all_data, axis=1)
    # remove duplicate columns if any
    merged_data = merged_data.loc[:, ~merged_data.columns.duplicated()]
    
    # Save CSV
    filename = f"{SAVE_DIR}/lifestyle_{datetime.today().date()}.csv"
    merged_data.to_csv(filename)
    print(f"🎉 Saved merged data to {filename}")
else:
    print("⚠️ No data fetched.")
