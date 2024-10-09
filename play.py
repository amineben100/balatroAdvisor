import re
from collections import Counter
import itertools

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
    full_deck = {f"{v} {s}"
                 for v in (list(map(str, range(2, 11))) + ['Ace', 'Jack', 'Queen', 'King'])
                 for s in ['Heart', 'Diamond', 'Spade', 'Club']}
    return full_deck - set(cards)

def evaluate_hand(cards):
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

# --- Additional Scoring System ---

HAND_SCORES = {
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

def calculate_pattern_score(pattern, pattern_cards):
    """Calculate the score for a single pattern and its cards."""
    base_chips, mult = HAND_SCORES.get(pattern, (0, 0))
    # Get the chip values of the cards involved
    card_values = [VALUE_MAP[card.split()[0]] for card in pattern_cards]
    card_chip_sum = sum(card_values)
    # Prepare the calculation string
    calculation_str = f"({base_chips} + " + " + ".join(map(str, card_values)) + f") x {mult}"
    # Calculate the total score for this pattern
    score = (base_chips + card_chip_sum) * mult
    calculation_str += f" = {score}"
    return score, calculation_str

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
        user_input = input("Enter the playing cards string (e.g., 7h10h2s3dah9c): ")
        cards, n = parse_playing_cards(user_input)
        remaining_deck = update_deck(cards)

        print(f"\nParsed Cards ({n}):")
        for card in cards:
            print(card)
        print(f"\nRemaining Deck: {len(remaining_deck)} cards")

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
