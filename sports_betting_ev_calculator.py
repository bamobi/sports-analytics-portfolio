"""
sports_betting_ev_calculator.py
================================
A command-line tool for sports bettors to evaluate expected value, parlay
math, and Kelly criterion staking on individual bets and parlays.

Author: Buchi Amobi
Portfolio piece — applied probability, decision theory, and clean CLI design.

USAGE
-----
    # Single bet EV analysis
    python sports_betting_ev_calculator.py single --odds -110 --prob 0.55 --bankroll 1000

    # Parlay analysis
    python sports_betting_ev_calculator.py parlay -- -110,0.55 -120,0.60 +105,0.45 --bankroll 1000

    # Kelly criterion sizing
    python sports_betting_ev_calculator.py kelly --odds +150 --prob 0.45 --bankroll 1000 --fraction 0.25

CONCEPTS
--------
• American odds <-> implied probability conversion
• Expected value (EV) = P(win) * payout - P(lose) * stake
• Kelly criterion: f* = (bp - q) / b  where b = decimal odds - 1, p = win prob, q = 1-p
• Parlay probability = product of individual win probabilities (independence assumption)
• Parlay payout = product of individual decimal odds
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass


# ---------- Odds conversions ----------

def american_to_decimal(american: int) -> float:
    """Convert American odds to decimal odds. +150 -> 2.50, -200 -> 1.50"""
    if american >= 100:
        return 1 + american / 100
    elif american <= -100:
        return 1 + 100 / abs(american)
    else:
        raise ValueError(f"Invalid American odds: {american}. Must be >=+100 or <=-100.")


def american_to_implied(american: int) -> float:
    """Convert American odds to implied probability (with vig)."""
    if american >= 100:
        return 100 / (american + 100)
    elif american <= -100:
        return abs(american) / (abs(american) + 100)
    else:
        raise ValueError(f"Invalid American odds: {american}")


def decimal_to_american(decimal: float) -> int:
    """Convert decimal odds to American odds."""
    if decimal >= 2.0:
        return round((decimal - 1) * 100)
    else:
        return round(-100 / (decimal - 1))


# ---------- Core math ----------

@dataclass
class BetAnalysis:
    american_odds: int
    decimal_odds: float
    implied_prob: float    # book-implied probability (includes vig)
    true_prob: float       # your estimate of true win probability
    edge: float            # true_prob - implied_prob
    ev_per_dollar: float   # expected value per $1 staked
    kelly_full: float      # full Kelly stake fraction
    kelly_fractional: float
    kelly_stake: float     # actual dollar amount to stake

    def print(self) -> None:
        print("=" * 60)
        print(f"  Bet Analysis")
        print("=" * 60)
        print(f"  American odds:        {self.american_odds:+d}")
        print(f"  Decimal odds:         {self.decimal_odds:.3f}")
        print(f"  Book implied prob:    {self.implied_prob:.2%}")
        print(f"  Your estimated prob:  {self.true_prob:.2%}")
        print(f"  Edge:                 {self.edge:+.2%}")
        print(f"  EV per $1 staked:     ${self.ev_per_dollar:+.4f}")
        print()
        print(f"  Full Kelly fraction:  {self.kelly_full:+.2%} of bankroll")
        print(f"  Fractional Kelly:     {self.kelly_fractional:+.2%} of bankroll")
        print(f"  Recommended stake:    ${self.kelly_stake:,.2f}")
        print()
        if self.edge < 0:
            print("  >> VERDICT: NEGATIVE EV - do not bet.")
        elif self.edge < 0.01:
            print("  >> VERDICT: marginal edge - bet only if confident in probability estimate.")
        elif self.edge < 0.03:
            print("  >> VERDICT: small +EV - acceptable bet at conservative sizing.")
        else:
            print("  >> VERDICT: strong +EV - bet at recommended Kelly stake.")
        print()


def analyze_single_bet(american_odds: int, true_prob: float, bankroll: float,
                       kelly_fraction: float = 0.25) -> BetAnalysis:
    """Compute EV, edge, and Kelly stake for a single bet."""
    if not 0 < true_prob < 1:
        raise ValueError(f"true_prob must be between 0 and 1, got {true_prob}")
    if bankroll <= 0:
        raise ValueError(f"bankroll must be positive, got {bankroll}")
    if not 0 < kelly_fraction <= 1:
        raise ValueError(f"kelly_fraction must be in (0, 1], got {kelly_fraction}")

    decimal = american_to_decimal(american_odds)
    implied = american_to_implied(american_odds)
    edge = true_prob - implied

    # EV per $1: P(win) * (decimal - 1) - P(lose) * 1
    ev_per_dollar = true_prob * (decimal - 1) - (1 - true_prob)

    # Kelly: f* = (bp - q) / b, where b = decimal - 1
    b = decimal - 1
    p = true_prob
    q = 1 - p
    kelly_full = (b * p - q) / b if b > 0 else 0.0
    kelly_fr = max(0.0, kelly_full * kelly_fraction)  # don't go negative
    kelly_stake = kelly_fr * bankroll

    return BetAnalysis(
        american_odds=american_odds,
        decimal_odds=decimal,
        implied_prob=implied,
        true_prob=true_prob,
        edge=edge,
        ev_per_dollar=ev_per_dollar,
        kelly_full=kelly_full,
        kelly_fractional=kelly_fr,
        kelly_stake=kelly_stake,
    )


@dataclass
class ParlayAnalysis:
    n_legs: int
    individual: list[tuple[int, float]]  # list of (american_odds, true_prob)
    parlay_decimal: float
    parlay_american: int
    parlay_true_prob: float
    parlay_implied_prob: float
    edge: float
    ev_per_dollar: float
    stake: float
    expected_payout: float
    expected_profit: float

    def print(self) -> None:
        print("=" * 60)
        print(f"  Parlay Analysis ({self.n_legs} legs)")
        print("=" * 60)
        for i, (odds, prob) in enumerate(self.individual, 1):
            implied = american_to_implied(odds)
            edge = prob - implied
            print(f"  Leg {i}:  {odds:+d}  |  est prob {prob:.2%}  |  edge {edge:+.2%}")
        print()
        print(f"  Combined decimal odds:    {self.parlay_decimal:.2f}")
        print(f"  Combined American odds:   {self.parlay_american:+d}")
        print(f"  Parlay true probability:  {self.parlay_true_prob:.2%}")
        print(f"  Parlay implied (book):    {self.parlay_implied_prob:.2%}")
        print(f"  Parlay edge:              {self.edge:+.2%}")
        print(f"  EV per $1 staked:         ${self.ev_per_dollar:+.4f}")
        print()
        print(f"  Stake:                    ${self.stake:,.2f}")
        print(f"  Potential payout:         ${self.expected_payout:,.2f}")
        print(f"  Expected profit:          ${self.expected_profit:+,.2f}")
        print()
        print("  >> NOTE: parlays assume leg independence. Correlated legs")
        print("     (same game, weather-affected props) violate this and")
        print("     real probability is typically lower than computed here.")
        print()


def analyze_parlay(legs: list[tuple[int, float]], bankroll: float,
                   stake_pct: float = 0.01) -> ParlayAnalysis:
    """Compute parlay EV and stake recommendation."""
    if not legs:
        raise ValueError("parlay must have at least one leg")

    decimal_product = 1.0
    true_prob_product = 1.0
    implied_prob_product = 1.0

    for american, prob in legs:
        if not 0 < prob < 1:
            raise ValueError(f"probability must be in (0,1), got {prob}")
        decimal_product *= american_to_decimal(american)
        true_prob_product *= prob
        implied_prob_product *= american_to_implied(american)

    parlay_american = decimal_to_american(decimal_product)
    edge = true_prob_product - implied_prob_product

    # EV = P(win) * (decimal - 1) - P(lose) * 1
    ev_per_dollar = true_prob_product * (decimal_product - 1) - (1 - true_prob_product)

    stake = bankroll * stake_pct  # conservative flat stake for parlays
    expected_payout = stake * decimal_product
    expected_profit = ev_per_dollar * stake

    return ParlayAnalysis(
        n_legs=len(legs),
        individual=legs,
        parlay_decimal=decimal_product,
        parlay_american=parlay_american,
        parlay_true_prob=true_prob_product,
        parlay_implied_prob=implied_prob_product,
        edge=edge,
        ev_per_dollar=ev_per_dollar,
        stake=stake,
        expected_payout=expected_payout,
        expected_profit=expected_profit,
    )


# ---------- CLI ----------

def parse_leg(s: str) -> tuple[int, float]:
    """Parse 'american_odds,probability' string."""
    parts = s.split(',')
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(f"Leg must be 'odds,prob', got '{s}'")
    return int(parts[0]), float(parts[1])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sports betting EV calculator with Kelly criterion sizing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest='cmd', required=True)

    # Single bet
    p_single = sub.add_parser('single', help='analyze a single bet')
    p_single.add_argument('--odds', type=int, required=True, help='American odds (e.g. -110, +150)')
    p_single.add_argument('--prob', type=float, required=True, help='your estimated win probability (0-1)')
    p_single.add_argument('--bankroll', type=float, required=True, help='current bankroll in dollars')
    p_single.add_argument('--fraction', type=float, default=0.25, help='Kelly fraction (default 0.25 = quarter Kelly)')

    # Parlay
    p_parlay = sub.add_parser('parlay', help='analyze a parlay')
    p_parlay.add_argument('legs', type=parse_leg, nargs='+',
                          help='one or more "odds,probability" pairs (positional)')
    p_parlay.add_argument('--bankroll', type=float, required=True, help='current bankroll in dollars')
    p_parlay.add_argument('--stake-pct', type=float, default=0.01, help='flat stake as % of bankroll (default 1%%)')

    # Kelly only
    p_kelly = sub.add_parser('kelly', help='Kelly criterion stake sizing only')
    p_kelly.add_argument('--odds', type=int, required=True)
    p_kelly.add_argument('--prob', type=float, required=True)
    p_kelly.add_argument('--bankroll', type=float, required=True)
    p_kelly.add_argument('--fraction', type=float, default=0.25)

    args = parser.parse_args()

    try:
        if args.cmd in ('single', 'kelly'):
            result = analyze_single_bet(args.odds, args.prob, args.bankroll, args.fraction)
            result.print()
        elif args.cmd == 'parlay':
            result = analyze_parlay(args.legs, args.bankroll, args.stake_pct)
            result.print()
    except (ValueError, ZeroDivisionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
