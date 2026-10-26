# Magnite Demo Track — Custom Algo Optimization

**Dashboard:** Magnite CTV + Deal Outcome Intelligence (7 tabs)
**Time:** ~13 minutes + questions
**Rule:** Mention only Affinity and Magnite. No other ad platforms.

---

## Before You Start

### The pitch in one line

> **"Magnite knows who saw every ad, on every screen. Affinity knows who went on to buy. Together, Magnite can prove which TV and web ad space drives real sales, and price and package it that way."**

### The problem

Magnite is the largest independent seller of ad space, and especially strong in streaming TV (CTV). Buyers can already get Magnite's log files showing every ad they ran: the app, the device, the deal, the time.

Magnite's own description of those files says buyers use them to *"validate the audience exposed to their ads and attribute campaign outcomes to ad exposure."*

But the log files stop at "the ad was shown." They can't say whether anyone bought anything. That missing piece is exactly what Affinity has.

### What each side brings

- **Affinity:** Real purchases from credit and debit cards, covering about half of US households and 5,300+ brands.
- **Magnite:** Two log files. *Streaming* covers TV apps, devices and locations. *DV+* covers websites, ad sizes and formats. Both include deals and buyers.
- **Snowflake:** A secure space where the two datasets meet without either side seeing the other's raw data, plus built-in machine learning to find the patterns. Magnite already delivers these logs straight into Snowflake.

### Words to know

| Word | Meaning |
|---|---|
| **CTV** | Streaming TV, meaning ads on a smart TV or streaming stick |
| **DV+** | Magnite's website and app ads (banners and video) |
| **Deal** | A pre-arranged package of ad space sold to a buyer |
| **Yield** | How often an ad leads to a real purchase |
| **2.0x** | Twice as likely to lead to a purchase as average |
| **BOOST / SUPPRESS** | Price this ad space higher / lower |

---

## Demo Order

| # | Tab | Time | Message |
|---|---|---|---|
| 1 | Identity Coverage | 1.5 min | We can connect the data, on both screens |
| 2 | CTV Yield | 2 min | Not all TV ad space is equal |
| 3 | Verified Deals + Packages | 2.5 min | Which deals really sell, and new ones to create |
| 4 | Buyer Outcomes | 2 min | Proof for every buyer |
| 5 | Pricing Rules | 1.5 min | What to charge |
| 6 | Cross-Screen | 1.5 min | TV + web together beats either alone |
| 7 | ML Models | 2 min | Why you can trust it |

---

## Opening (no screen)

> "Magnite already gives buyers a detailed record of every ad they ran. What that record can't show is whether those ads led to a sale. Affinity can show that. Today we'll show what happens when you put the two together."

---

## 1. Identity Coverage *(start here)*

**On screen:** 25.8% match rate (25,847 people), 10M ad views, 1.77M ad views with purchase data, plus a chart by ID type.

**Say:**
> "First, can we connect the two? Yes. We matched almost 26,000 people. Most matched on email-based IDs like UID2 and Yahoo ConnectID, the rest on device IDs and home internet addresses."

**Point to the right-hand chart:** Green bars are ad views we can tie to purchases.
> "Email-based IDs match about one in three. TV ads that only send a device and IP still match about one in five. That's how we reach households."

> **Careful:** RampID and no-ID ad views show 0% here. Don't say they can't work. Say: *"Those need one extra translation step, which we left out of this demo."*

**Affinity value:** Magnite has no purchase data of its own. For these 26,000 people and 6,000+ households, it now does.

**ML used:** None yet. This step is secure matching inside Snowflake. IDs are scrambled before matching, so nobody sees anyone's raw data.

---

## 2. CTV Yield

**On screen:** Three numbers at the top: streaming TV purchase rate **1.28%** vs web **0.71%** (**1.8x**). Below that, a grid of TV apps × device type, then daypart and screen-size charts.

**Say:**
> "Streaming TV ads lead to purchases almost twice as often as web ads, and bring in about $1,370 in sales per thousand ads."

**Point to the grid:**
> "Green means people who saw the ad went on to buy. Home, cooking and sports apps on a real TV run at more than twice the average. Kids and classic-TV apps on phones and laptops barely move the needle. Today these are often priced the same."

**Point to the bottom charts:**
- Evening prime time: **1.79%** vs late night **0.48%**
- 4K and full-HD screens: **1.5–1.7%** vs small phone players **~0.45%**

**Affinity value:** The colors come from Affinity's purchase data. Without it, every square looks the same.

**ML used:** A simple comparison against the average. The ML models in tab 7 confirm the same factors matter.

---

## 3. Verified Deals + Packages

**On screen:** 16 Magnite deals ranked by purchase yield, with a dashed "average" line. Below, 7 new curated packages.

**Say:**
> "Every deal gets a grade based on real purchases. The Home & Lifestyle TV deal runs at **2.9x** average, and Premium Sports TV at **2.6x**. Those are proven sellers."

**Point to a weak deal:** *Curated High-Attention Display* sits **below** the line (0.83x).
> "It's called premium, but it doesn't drive purchases. Now you know, and you can fix it before a buyer finds out."

**Scroll to packages:**
> "These are new curated deals built from what actually sells. *Prime-Time Big Screen* (TV, evenings, top apps) runs at **2.7x** average. *Home & Kitchen Shoppers* runs across TV and web at **1.6x**."

**Affinity value:** The grades and package lift come only from Affinity's purchase data. That turns "trust us, it's premium" into "here's the proof."

**ML used:** Packages are built from the factors the model found most important. They're totals, not individuals, so they're safe to share with buyers.

---

## 4. Buyer Outcomes

**On screen:** 40 buyer seats ranked by purchase lift (green / gray / red), **$2.0M** in sales tied to Magnite ads, and a report card for any seat.

**Say:**
> "This is the promise of Magnite's log files, finally delivered. For every buyer: what they won on Magnite, and what sales followed."

**Pick a seat in the dropdown** (start with the top one):
> "This buyer's ads led to purchases **43% more** than average, and their best app was KitchenPlay. That's a renewal conversation backed by proof."

**Then point to a red bar:**
> "Same marketplace, but this buyer is **30% below** average. That's not a reason to lose them. It's a reason to offer them a better deal from tab 3."

**Affinity value:** The purchase and sales columns are Affinity's. Without them, this report shows impressions, not results.

**ML used:** None needed. These are straight sums of purchases tied to each buyer's ads. The model confirms who buys is the top factor (tab 7).

---

## 5. Pricing Rules

**On screen:** 535 rules (103 BOOST, 269 SUPPRESS, 163 NEUTRAL), filters, a table and a chart. Below, price tiers.

**Say:**
> "These are 535 plain-English pricing rules. Not lists of people, just rules about ad space."

**Show two examples:**
- Filter **BOOST**: *Publisher Deal on Connected TV* = **2.7x**, raise the price. *PrimeLeague Sports in the evening* = **2.3x**
- Filter **SUPPRESS**: *Late night* = **0.40x**, and *puzzlepal.app* = **0.39x**, stop overpricing

**Scroll down:** Every app or site × device sorts into a tier: **7 Premium, 10 Plus, 48 Standard, 66 Value**, each with a suggested price multiplier.

> **Careful:** Magnite's log files don't include prices. These are *relative* multipliers (e.g. "1.5x your normal price"), not dollar floors.

**Affinity value:** Every BOOST or SUPPRESS is backed by real purchases.

**ML used:** Rules only use details known at the moment the ad is sold (app, device, time, deal), so they can be applied live. Small samples are toned down so they can't produce wild numbers.

---

## 6. Cross-Screen

**On screen:** Toggle for Household / Individual, two bar charts and lift numbers.

**Say:**
> "Here's something only this combination can show. Affinity recognizes the same household on Magnite's TV feed and its web feed."

> "Households that saw ads on **both** screens bought **1.43x** more often from their TV ads, and **1.35x** more from their web ads, than households reached on only one screen."

**The point for Magnite:**
> "Selling TV and web together is worth more than selling them separately. That's a cross-screen package Magnite can price higher."

> **Careful:** Cross-screen households also see more ads overall. The charts compare TV ads to TV ads and web ads to web ads, but if asked, say: *"Part of this is reach and frequency. A pilot with a test group gives the exact number."*

**Affinity value:** Affinity's household view is what links the two screens. Neither log file can do that alone.

**ML used:** None here. It's a straight comparison. The model also uses "cross-screen" as one of its inputs.

---

## 7. ML Models

**On screen:** Two model cards, a 10-bar chart, two "what matters most" charts, and a 4-panel holdout check.

**Say:**
> "Two machine learning models, built inside Snowflake on 1.77 million ad views. One predicts *will this lead to a purchase*. The other predicts *how much will they spend*."

### The 10-bar chart
> "We scored ad views the model had **never seen** and split them into 10 groups. The top group buys **3.9x** more than average. The top 30% drives **69% of all purchases**."

### What matters most
> "The #1 factor is **which buyer** is running the ad. Targeting quality varies a lot. Next is **which app or site**, then **Affinity's purchase score**. So it's who's buying, where it runs, and who's watching."

### Holdout check
> "Training and unseen data show the same purchase rate (**1.09% vs 1.09%**), so the model learned a real pattern, not a fluke. Within the unseen data, the model's top 30% converts at **2.53%** vs **0.48%** for the rest. That's about **5x**."

> **Careful:** The first two panels being equal is the *good* news (no overfitting). The lift story is panels 3 vs 4.

**Affinity value:** Affinity supplies the answers the models learn from (did they buy, how much) and the #3 factor.

**ML used:** Snowflake's built-in machine learning. The data never leaves Snowflake, there's no separate tool to run, and you can see exactly why the model decides what it does.

---

## Closing

> "Magnite's ad logs and Affinity's purchase data met in a secure space in Snowflake, and neither side saw the other's raw data. Snowflake's machine learning found which TV and web ad space actually drives purchases. The result: graded deals, 7 new curated packages, outcome reports for every buyer, and 535 pricing rules, all ready to use.
>
> **Your ad space, proven by real purchases.**"

**Next step:** A small pilot on real Magnite log files (already deliverable to Snowflake), measured against a test group.

---

## Common Questions

| Question | Answer |
|---|---|
| *Is this real Magnite data?* | No. It's realistic sample data built to Magnite's exact log-file fields (22 Streaming, 17 DV+). App, deal and buyer names are made up. A pilot would use real data. |
| *Does Affinity see our data?* | No. Only scrambled IDs are matched. Each side sees results, not the other's raw data. |
| *The logs don't have prices. How do you price?* | Rules give relative multipliers (e.g. 1.5x). Magnite applies them to its own prices. |
| *What about RampID traffic?* | It needs one ID translation step before matching. That's a pilot task, not a blocker. |
| *Do the rules need to know the viewer?* | No. Rules use app, device, time and deal, so they work on every ad. |
| *Can buyers see the outcome reports?* | Yes. They're totals per buyer, so they're safe to share. |
| *How often does it update?* | Magnite's logs arrive hourly and Affinity's purchase data daily. Rules can refresh as often as needed. |
| *Can it work at product (SKU) level?* | Not today, only at brand or store level. |

---

## Data Sources (presenter reference)

| Tab | Table (database `AFFINITY_DEMO`) |
|---|---|
| Identity Coverage | `CLEANROOM.MAGNITE_MATCH_RATE_SUMMARY`, `MAGNITE_CONSUMER.DEMO_OUTPUT_IDENTITY_COVERAGE` |
| CTV Yield | `MAGNITE_CONSUMER.DEMO_OUTPUT_SUPPLY_YIELD` |
| Verified Deals + Packages | `MAGNITE_CONSUMER.DEMO_OUTPUT_DEAL_OUTCOMES`, `DEMO_OUTPUT_CURATED_PACKAGES` |
| Buyer Outcomes | `MAGNITE_CONSUMER.DEMO_OUTPUT_BUYER_OUTCOMES` |
| Pricing Rules | `MAGNITE_CONSUMER.DEMO_OUTPUT_PRICING_RULES`, `DEMO_OUTPUT_PRICING_TIERS` |
| Cross-Screen | `MAGNITE_CONSUMER.DEMO_OUTPUT_CROSS_SCREEN` |
| ML Models | `ML.MODEL_REGISTRY`, `ML.MAGNITE_VALIDATION_DECILES`, `ML.MAGNITE_FEATURE_IMPORTANCE`, `ML.MAGNITE_HOLDOUT_RESULTS` |
| Source logs | `MAGNITE_CONSUMER.MAGNITE_STREAMING_LLD` (6M), `MAGNITE_CONSUMER.MAGNITE_DVPLUS_LLD` (4M) |
