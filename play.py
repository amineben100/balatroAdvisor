# play.py

import re
from collections import Counter
import itertools
from planetCards import get_active_planet_cards

# Defines the base hand scores
BASE_HAND_SCORES = {
    'High Card': (5, 1),
    'Pair': (10, 2),
    'Two Pair': (20, 2),
    'Three of a Kind': (30, 3),
    'Straight': (30, 4),
    'Flush': (35, 4),
    'Full House': (40, 4),
    'Four of a Kind': (60, 7),
    'Straight Flush': (100, 8),
    'Royal Flush': (100, 8)
}

# Initialize HAND_SCORES as a copy of BASE_HAND_SCORES
HAND_SCORES = BASE_HAND_SCORES.copy()

# Define global maps for card ranks and chip values
RANK_MAP = {
    '2': 2, '3': 3, '4': 4, '5':5, '6':6,
    '7':7, '8':8, '9':9, '10':10,
    'Jack':11, 'Queen':12, 'King':13, 'Ace':14
}

VALUE_MAP = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10,
    'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11
}

def parse_playing_cards(s):
    """
    Parses a string of playing cards and returns a list of card names.
    Example input: "ah kh qh jh 10h"
    """
    suits = {'H': 'Heart', 'D': 'Diamond', 'S': 'Spade', 'C': 'Club'}
    values = {'A': 'Ace', 'J': 'Jack', 'Q': 'Queen', 'K': 'King'}
    # Use case-insensitive matching and allow multiple characters for card values (e.g., 10)
    pattern = r'([2-9]|10|[AJQK])([HDSC])'
    matches = re.findall(pattern, s, re.I)
    if not matches:
        raise ValueError("Error: No valid cards found in the input.")
    cards = []
    for v, s in matches:
        v_upper = v.upper()
        s_upper = s.upper()
        card_value = values.get(v_upper, v_upper)
        card_suit = suits.get(s_upper)
        if not card_suit:
            raise ValueError(f"Error: Invalid suit '{s}'. Use H, D, S, or C.")
        card_full = f"{card_value} {card_suit}"
        if card_full in cards:
            raise ValueError(f"Error: Duplicate card '{card_full}' detected.")
        cards.append(card_full)
    return cards, len(cards)

def update_deck(cards):
    """
    Generates a full deck and removes the user’s cards to get the remaining deck.
    """
    full_deck = {f"{v} {s}"
                 for v in (list(map(str, range(2, 11))) + ['Ace', 'Jack', 'Queen', 'King'])
                 for s in ['Heart', 'Diamond', 'Spade', 'Club']}
    return full_deck - set(cards)

def evaluate_hand(cards):
    """
    Evaluates the given set of cards and identifies possible poker hands.
    Returns a list of tuples: (pattern_name, list_of_cards_in_pattern)
    """
    ranks = [RANK_MAP[card.split()[0]] for card in cards]
    suits = [card.split()[1] for card in cards]
    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)

    def find_sequences(vals):
        sequences = []
        unique_vals = sorted(set(vals))
        for i in range(len(unique_vals) - 4):
            seq = unique_vals[i:i+5]
            if all(seq[j] - seq[j-1] == 1 for j in range(1, 5)):
                sequences.append(seq)
        # Check for Ace-low straight (A-2-3-4-5)
        if set([14, 2, 3, 4, 5]).issubset(unique_vals):
            sequences.append([14, 2, 3, 4, 5])
        return sequences

    patterns = []

    # Royal Flush and Straight Flush
    for suit in suit_counts:
        suited_cards = [card for card in cards if card.split()[1] == suit]
        if len(suited_cards) >= 5:
            suited_ranks = [RANK_MAP[card.split()[0]] for card in suited_cards]
            sequences = find_sequences(suited_ranks)
            for seq in sequences:
                if len(seq) >= 5:
                    sequence_cards = [card for card in suited_cards if RANK_MAP[card.split()[0]] in seq]
                    if set(seq) == {10, 11, 12, 13, 14}:
                        patterns.append(('Royal Flush', sequence_cards))
                    else:
                        patterns.append(('Straight Flush', sequence_cards))
            if not sequences:
                patterns.append(('Flush', suited_cards))

    # Four of a Kind
    for rank, count in rank_counts.items():
        if count == 4:
            foak_cards = [card for card in cards if RANK_MAP[card.split()[0]] == rank]
            patterns.append(('Four of a Kind', foak_cards))

    # Full House
    threes = [rank for rank, count in rank_counts.items() if count == 3]
    pairs = [rank for rank, count in rank_counts.items() if count >= 2 and rank not in threes]
    for three in threes:
        for pair in pairs + [rank for rank in threes if rank != three]:
            fh_cards = [card for card in cards if RANK_MAP[card.split()[0]] in [three, pair]]
            patterns.append(('Full House', fh_cards))

    # Straight
    sequences = find_sequences(ranks)
    for seq in sequences:
        if len(seq) >= 5:
            straight_cards = [card for card in cards if RANK_MAP[card.split()[0]] in seq]
            patterns.append(('Straight', straight_cards))

    # Three of a Kind
    for rank, count in rank_counts.items():
        if count == 3:
            toak_cards = [card for card in cards if RANK_MAP[card.split()[0]] == rank]
            patterns.append(('Three of a Kind', toak_cards))

    # Two Pair
    pair_ranks = [rank for rank, count in rank_counts.items() if count == 2]
    if len(pair_ranks) >= 2:
        for i, j in itertools.combinations(pair_ranks, 2):
            tp_cards = [card for card in cards if RANK_MAP[card.split()[0]] in [i, j]]
            patterns.append(('Two Pair', tp_cards))

    # Pair
    for rank in pair_ranks:
        pair_cards = [card for card in cards if RANK_MAP[card.split()[0]] == rank]
        patterns.append(('Pair', pair_cards))

    # High Card
    if not patterns:
        max_rank = max(ranks)
        high_cards = [card for card in cards if RANK_MAP[card.split()[0]] == max_rank]
        patterns.append(('High Card', high_cards))

    return patterns

def get_card_value(card):
    """Return the numerical value of a card based on VALUE_MAP."""
    value_str = card.split()[0]  # Extract the rank from the card string
    return VALUE_MAP.get(value_str, 0)  # Retrieve the value from VALUE_MAP, defaulting to 0 if not found
def calculate_hand_score(hand_name, base_chip, base_multiplier, quantity, card):
    """
    Calculate the adjusted chip and multiplier based on Planet Cards.

    Parameters:
    - hand_name (str): The name of the poker hand.
    - base_chip (int): The base chip value.
    - base_multiplier (int): The base multiplier.
    - quantity (int): Number of active Planet Cards for this hand.
    - card (PlanetCard): The Planet Card object.

    Returns:
    - (adjusted_chip, adjusted_multiplier)
    """
    adjusted_chip = base_chip + (card.chip_value_bonus * quantity)
    adjusted_multiplier = base_multiplier + (card.multiplier_bonus * quantity)
    return adjusted_chip, adjusted_multiplier
def update_hand_scores():
    """Update HAND_SCORES based on active Planet Cards."""
    global HAND_SCORES
    HAND_SCORES = BASE_HAND_SCORES.copy()  # Reset to base scores

    active_planets = get_active_planet_cards()

    for card in active_planets:
        associated_hand = card.associated_hand
        if associated_hand in HAND_SCORES:
            base_chip, base_multiplier = HAND_SCORES[associated_hand]
            adjusted_chip, adjusted_multiplier = calculate_hand_score(associated_hand, base_chip, base_multiplier, card.quantity, card)
            HAND_SCORES[associated_hand] = (adjusted_chip, adjusted_multiplier)
        else:
            print(f"Warning: Associated hand '{associated_hand}' for Planet Card '{card.name}' not found in HAND_SCORES.")

def calculate_pattern_score(pattern_name, pattern_cards):
    """
    Calculate the score for a given pattern and its cards, considering active Planet Cards.
    """
    base_chip_value, base_multiplier = HAND_SCORES[pattern_name]
    adjusted_chip_value = base_chip_value
    adjusted_multiplier = base_multiplier

    card_values = sum(get_card_value(card) for card in pattern_cards)
    score = (adjusted_chip_value + card_values) * adjusted_multiplier
    calculation = f"({adjusted_chip_value} + sum of card values) x {adjusted_multiplier} = {score}"
    return score, calculation

# --- New Function to Find the Best Hands ---

def find_best_hands(cards, top_n=5):
    """Find the top_n best subsets of 5 cards with the highest scores."""
    hand_scores = []

    # Generate all possible subsets of size 5
    subsets = list(itertools.combinations(cards, 5))

    for subset in subsets:
        patterns = evaluate_hand(list(subset))
        # For each pattern in this subset, calculate the score
        for pattern, pattern_cards in patterns:
            # Ensure that pattern_cards are part of the current subset
            if all(card in subset for card in pattern_cards):
                score, calculation_str = calculate_pattern_score(pattern, pattern_cards)
                hand_scores.append({
                    'subset': subset,
                    'pattern': pattern,
                    'pattern_cards': pattern_cards,
                    'score': score,
                    'calculation': calculation_str
                })

    # Sort the hand_scores by score in descending order
    hand_scores.sort(key=lambda x: x['score'], reverse=True)

    # Remove duplicates based on the main pattern cards
    unique_hand_scores = []
    seen_patterns = set()
    for hand in hand_scores:
        # Use the sorted main pattern cards as the key
        main_cards_key = tuple(sorted(hand['pattern_cards']))
        if main_cards_key not in seen_patterns:
            seen_patterns.add(main_cards_key)
            unique_hand_scores.append(hand)
        if len(unique_hand_scores) >= top_n:
            break

    return unique_hand_scores

# --- Main Logic ---

def main():
    try:
        # Parse user input
        user_input = input("Enter the playing cards string (e.g., 7h10h2s3dah9c): ").strip()
        cards, n = parse_playing_cards(user_input)
        remaining_deck = update_deck(cards)

        print(f"\nParsed Cards ({n}):")
        for card in cards:
            print(card)
        print(f"\nRemaining Deck: {len(remaining_deck)} cards")

        # Update HAND_SCORES based on active Planet Cards
        update_hand_scores()

        # Find the best subsets of 5 cards
        top_hands = find_best_hands(cards, top_n=5)
        if top_hands:
            print("\nTop 5 Best Combinations:")
            for idx, hand in enumerate(top_hands, 1):
                print(f"\nRank {idx}:")
                print(f"Pattern: {hand['pattern']}")
                print(f"Cards to Play: {', '.join(hand['pattern_cards'])}")
                print(f"Score Calculation: {hand['calculation']}")
                print(f"Total Score: {hand['score']}")
        else:
            print("\nNo valid combinations found.")
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()