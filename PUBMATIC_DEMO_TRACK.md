# PubMatic Demo Track — Custom Algo Optimization

**Dashboard:** PubMatic Inventory Yield Scorer (6 tabs)
**Time:** ~12 minutes + questions
**Rule:** Mention only Affinity and PubMatic. No other ad platforms.

---

## Before You Start

### The pitch in one line

> **"PubMatic knows what every ad slot sold for. Affinity knows whether it led to a purchase. Together, PubMatic can price its ad space on real results."**

### The problem

PubMatic sells ad space for publishers. For every slot, it sets a minimum price.

- Price too high → the slot goes unsold
- Price too low → money is left on the table

Today that price is based on what buyers paid before. Nobody on the selling side can see whether the ad led to anyone buying anything.

### What each side brings

- **Affinity:** Real purchases from credit and debit cards, covering about half of US households and 5,300+ brands.
- **PubMatic:** Details about every ad slot: website, ad type, device, location, price.
- **Snowflake:** A secure space where the two datasets meet without either side seeing the other's raw data, plus built-in machine learning to find the patterns.

### Words to know

| Word | Meaning |
|---|---|
| **Floor price** | The lowest price PubMatic will accept for an ad slot |
| **Yield** | How often an ad slot leads to a real purchase |
| **2.0x** | Twice as likely to lead to a purchase as average |
| **BOOST** | This ad slot sells well, so raise the price |
| **SUPPRESS** | This ad slot rarely leads to purchases, so stop overpricing it |

---

## Demo Order

| # | Tab | Time | Message |
|---|---|---|---|
| 1 | Identity Coverage | 1 min | We can connect the data |
| 2 | Yield Heatmap | 2 min | Not all ad space is equal |
| 3 | SSP Bidding Rules | 2 min | Simple rules you can use today |
| 4 | Floor Optimizer | 1.5 min | What to charge |
| 5 | Premium Packages | 1 min | What to sell |
| 6 | ML Models + Features | 2 min | Why you can trust it |

---

## Opening (no screen)

> "PubMatic prices billions of ad slots every day based on what buyers paid before. What you can't see is whether those ads led to a purchase. Affinity can see that. Today we'll show what happens when you put the two together."

---

## 1. Identity Coverage *(start here)*

**On screen:** 26.2% match rate (26,231 people), split across three ways of matching.

**Say:**
> "First, can we even connect the two? Yes. We matched 26,231 people between PubMatic's ad data and Affinity's purchase data, using hashed emails, phone IDs, and internet addresses."

**Affinity value:** PubMatic has no purchase data of its own. For these 26,000 people, it now does.

**ML used:** None yet. This step is secure matching inside Snowflake. Personal details are scrambled before matching, so nobody sees anyone's raw data.

---

## 2. Yield Heatmap

**On screen:** A grid of websites × ad types. Green converts well, red converts poorly. Best is 2.12x, worst is 0.35x.

**Say:**
> "Each square is a website and ad type. Green means people who saw it went on to buy. Red means they didn't. The best squares perform six times better than the worst, yet today they're priced about the same."

**Point to:** A green square and a red square on the same website. "Same site, very different value."

**Affinity value:** The colors come from Affinity's purchase data. Without it, every square would look the same.

**ML used:** A simple comparison of each square's purchase rate against the average. The ML models in tab 6 confirm the same factors matter.

---

## 3. SSP Bidding Rules

**On screen:** 271 rules: 122 BOOST, 96 SUPPRESS, 53 NEUTRAL. Filters, a table, and a chart.

**Say:**
> "This is what PubMatic gets: 271 plain-English rules. Not a list of people, just rules about ad slots."

**Show two examples:**
- Filter **BOOST** → *Connected TV + sports content* → **2.87x**: raise the price
- Filter **SUPPRESS** → *Desktop + news content* → **0.32x**: stop overpricing

> "Same marketplace, nine times difference in real value."

**Scroll down:** Every ad slot sorts into a price tier: **1,191 Premium**, **620 Standard**, **1,339 Discount**.

**Affinity value:** Every BOOST or SUPPRESS is based on real purchases. Only Affinity's data can tell you that.

**ML used:** The rules are built from the factors the ML model found most important. Rules with too little data are toned down so a small sample can't produce a wild number.

---

## 4. Floor Optimizer

**On screen:** 200 price recommendations (current price, suggested price, expected gain) and a top-20 chart.

**Say:**
> "Rules tell you what to do. This tells you how much. For each ad slot: today's minimum price, the suggested price, and the expected gain."

**Point to the top bar:** weather.com / native ads / Connected TV.

> **Careful:** The top bar shows ~384% gain. Don't lead with the number. Say: *"The point is which ad slots are underpriced. The exact gain depends on buyer demand."*

**Affinity value:** Suggested prices are based on real purchases, not just past auction prices.

**ML used:** A second model separates big spenders from small spenders, so "led to a purchase" and "led to a big purchase" aren't treated the same.

---

## 5. Premium Packages

**On screen:** 17 ready-made bundles of ad space, each with its purchase rate and reach.

**Say:**
> "These are bundles PubMatic can sell to advertisers *with proof*. Top ones: People.com, ESPN, and Weather.com."

> "Today the pitch is 'trust us, it's premium.' Now it's 'this ad space led to real purchases, and here's the evidence.'"

**Affinity value:** The purchase rate column is the proof, and it comes from Affinity.

**ML used:** Bundles are built from the best-performing ad slots. They're totals, not individuals, so they're safe to share with advertisers.

---

## 6. ML Models + Features

**On screen:** Two model cards, a 10-bar chart, a "what matters most" chart, and a test comparison.

**Say:**
> "Two machine learning models, built inside Snowflake on 2.5 million ad views. One predicts *will this lead to a purchase*. The other predicts *how much will they spend*."

### The 10-bar chart

> "We ranked every ad slot by the model's score and split them into 10 groups. The top group leads to purchases **2.5 times more** than average. The top 30% of ad space drives **over half of all purchases**."

### What matters most

> "The #1 factor is PubMatic's **own minimum price**. The #2 factor is **Affinity's purchase prediction**. So your current pricing already knows something, and Affinity tells it what."

### Test comparison

> **Careful:** Both sides show nearly the same numbers (1.07% vs 1.07%). Don't say the rules caused an improvement. Say:
> *"We tested the model on data it had never seen, and it held up. So it learned a real pattern, not a fluke."*

**Affinity value:** Affinity supplies the answers the models learn from (did they buy, how much) and the #2 factor. Without it there's nothing to learn from.

**ML used:** Snowflake's built-in machine learning. The data never leaves Snowflake, there's no separate tool to manage, and you can see exactly why the model decides what it does.

---

## Closing

> "PubMatic's ad data and Affinity's purchase data met in a secure space in Snowflake, and neither side saw the other's raw data. Snowflake's machine learning found which ad space actually drives purchases. The result: 271 simple rules, 200 price suggestions, and 17 sellable packages, all ready to use.
>
> **Your prices — now based on real purchases.**"

**Next step:** A small pilot on real PubMatic data, measured against a test group.

---

## Common Questions

| Question | Answer |
|---|---|
| *Is this real PubMatic data?* | No, it's realistic sample data built to PubMatic's format. A pilot would use real data. |
| *Does Affinity see our data?* | No. Only scrambled IDs are matched. Each side sees results, not the other's raw data. |
| *Do we need to know who the viewer is?* | No. Rules use ad slot details like site, device, and content, so they work on every ad slot. |
| *What about people you couldn't match?* | Rules describe ad space, not people, so every ad slot benefits. |
| *How often does it update?* | Affinity's purchase data refreshes daily. Rules can be refreshed as often as needed. |
| *Can it work at product (SKU) level?* | Not today, only at brand or store level. |

---

## Data Sources (presenter reference)

| Tab | Table (database `AFFINITY_DEMO`) |
|---|---|
| Identity Coverage | `CLEANROOM.MATCH_RATE_SUMMARY` |
| Yield Heatmap | `PUBMATIC_CONSUMER.DEMO_OUTPUT_INVENTORY_YIELD_SCORES` |
| SSP Bidding Rules | `PUBMATIC_CONSUMER.DEMO_OUTPUT_SSP_BIDDING_RULES`, `DEMO_OUTPUT_PUBLISHER_MULTIPLIERS` |
| Floor Optimizer | `PUBMATIC_CONSUMER.DEMO_OUTPUT_FLOOR_RECOMMENDATIONS` |
| Premium Packages | `PUBMATIC_CONSUMER.DEMO_OUTPUT_PURCHASE_INVENTORY_PACKAGES` |
| ML Models | `ML.MODEL_REGISTRY`, `ML.PUBMATIC_VALIDATION_DECILES`, `ML.PUBMATIC_FEATURE_IMPORTANCE`, `ML.PUBMATIC_HOLDOUT_RESULTS` |
