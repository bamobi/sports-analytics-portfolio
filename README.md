# Buchi Amobi — AI & Analytics Portfolio

**Updated:** May 2026
**Focus:** Applied AI, statistical modeling, and analytics — with sports as the subject domain.

This folder contains four self-contained portfolio pieces that demonstrate practical proficiency across data analysis, predictive modeling, written research, and software engineering. The sports lens is intentional: the domain is data-rich, decisions are observable, and the math is the same as the financial and risk-management work used in insurance brokerage and capital markets.

---

## Contents

### 1. `NBA_Player_Analytics_Clustering.ipynb`
**Skills demonstrated:** Python · scikit-learn · pandas · matplotlib · unsupervised learning · regression

A Jupyter notebook that applies K-Means clustering and PCA to identify NBA player archetypes from per-game and advanced metrics, then fits a multiple linear regression to identify efficiency outliers (players whose PER outpaces their volume stats).

**Walkthrough:**
1. Loads a top-100 scorer dataset modeled on real 2024-25 NBA distributions.
2. Builds a correlation heatmap to inspect feature structure.
3. Uses the elbow method to pick optimal `k`, then fits K-Means at k=4.
4. Reduces to 2D via PCA for visualization, with clusters color-coded.
5. Runs OLS regression to identify statistical over- and under-performers.

**To run:** open in Jupyter or Google Colab. Dependencies: `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`.

---

### 2. `MLB_NRFI_Model.xlsx`
**Skills demonstrated:** Excel modeling · probabilistic reasoning · sports betting math · clean spreadsheet design

A four-sheet Excel workbook that builds a No-Runs-First-Inning (NRFI) probability model from pitcher, lineup, and ballpark inputs, then layers in a parlay calculator with full expected-value math.

**Sheets:**
- **README** — methodology and color-key
- **Inputs** — pitcher and lineup data for 10 games (BLUE = user input, YELLOW = key assumptions)
- **Model** — blended NRFI probability per game, edge vs. book odds, bet/pass recommendations
- **Parlay** — combine selected legs, compute parlay probability, EV, and ROI

**What's interesting here:** the model implements proper edge calculation (model probability minus book-implied probability) with a conditional formatting color scale showing where the +EV bets sit. Conservative independence assumption is flagged in the parlay summary.

---

### 3. `AI_in_Sports_Analytics_Research_Brief.docx`
**Skills demonstrated:** Industry research · technical writing · synthesis

An 8-page research brief examining the state of AI in professional sports across four areas: player evaluation, in-game decision support, fan engagement, and sports betting. Each section covers current state, methods in production use, vendor landscape, and where the technology is still falling short. Closes with three forecasts for the next 24 months and a note on how sports analytics methods transfer to commercial insurance.

Written in the voice of a practitioner brief — concise, opinionated, sourced. Not academic.

---

### 4. `sports_betting_ev_calculator.py`
**Skills demonstrated:** Python · CLI design · applied probability · Kelly criterion · clean code

A command-line tool for evaluating sports bets. Three subcommands:
- `single` — analyze a single bet with full Kelly criterion sizing
- `parlay` — combine multiple legs, compute parlay EV and recommended stake
- `kelly` — Kelly sizing only

**Example:**
```bash
python sports_betting_ev_calculator.py single --odds -110 --prob 0.55 --bankroll 1000

============================================================
  Bet Analysis
============================================================
  American odds:        -110
  Decimal odds:         1.909
  Book implied prob:    52.38%
  Your estimated prob:  55.00%
  Edge:                 +2.62%
  EV per $1 staked:     $+0.0500

  Full Kelly fraction:  +5.50% of bankroll
  Fractional Kelly:     +1.38% of bankroll
  Recommended stake:    $13.75

  >> VERDICT: small +EV - acceptable bet at conservative sizing.
```

The code is single-file, fully typed, no external dependencies beyond the standard library. Uses dataclasses for clean output, raises proper errors on invalid input, and applies quarter-Kelly by default (the variance-aware sizing most professional bettors actually use).

---

## How These Pieces Fit Together

Each piece demonstrates a different muscle:

| Piece | Muscle |
|---|---|
| NBA Notebook | Unsupervised ML, exploratory analysis |
| NRFI Model | Excel modeling, probabilistic reasoning |
| Research Brief | Technical writing, industry synthesis |
| EV Calculator | Software engineering, applied math |

The common thread: turning data into decisions under uncertainty. That same skill set is what makes someone effective in commercial insurance, capital markets, and quantitative finance — domains I'm moving toward in my career.

---

*Questions or feedback: camobi@iu.edu*
