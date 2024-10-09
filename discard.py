# discard.py
import itertools
import math
from collections import Counter
from play import (
    parse_playing_cards,
    evaluate_hand,
    calculate_pattern_score,
    HAND_SCORES,
    VALUE_MAP,
    RANK_MAP
)

def calculate_pattern_probability(kept_cards, desired_pattern, remaining_deck, num_draws):
    """
    Calculate the probability of achieving the desired pattern after drawing num_draws cards.
    """
    kept_ranks = [RANK_MAP[card.split()[0]] for card in kept_cards]
    kept_suits = [card.split()[1] for card in kept_cards]
    rank_counts = Counter(kept_ranks)
    suit_counts = Counter(kept_suits)
    total_remaining_cards = len(remaining_deck)
    remaining_ranks = Counter([RANK_MAP[card.split()[0]] for card in remaining_deck])
    remaining_suits = Counter([card.split()[1] for card in remaining_deck])

    if desired_pattern == 'Four of a Kind':
        # Check if we have three of a kind already
        for rank, count in rank_counts.items():
            if count == 3:
                remaining_same_rank = 4 - count
                probability = remaining_same_rank / total_remaining_cards
                return probability
        return 0

    elif desired_pattern == 'Full House':
        # Need at least one three of a kind and one pair
        threes = [rank for rank, cnt in rank_counts.items() if cnt >= 3]
        pairs = [rank for rank, cnt in rank_counts.items() if cnt >= 2 and rank not in threes]

        # If we already have a three of a kind, need at least one pair
        if threes:
            # Calculate probability to draw at least one pair in num_draws
            # Simplified: probability to draw at least two cards of any pair
            # This is a complex calculation; here we provide an approximation
            prob = 0
            for pair_rank in [rank for rank, cnt in remaining_ranks.items() if cnt >= 2]:
                prob += (math.comb(remaining_ranks[pair_rank], 2)) / math.comb(total_remaining_cards,
                                                                               2) if num_draws >= 2 else 0
            return prob
        else:
            # Need to draw at least three of a kind
            for rank, count in remaining_ranks.items():
                if count >= 3:
                    prob = math.comb(count, 3) / math.comb(total_remaining_cards, 3) if num_draws >= 3 else 0
                    return prob
            return 0

    elif desired_pattern == 'Flush':
        # Find the suit with the maximum number of kept cards
        if not kept_suits:
            return 0
        target_suit, count = suit_counts.most_common(1)[0]
        needed = 5 - count
        if needed <= 0:
            return 1.0  # Already a flush
        remaining_same_suit = remaining_suits[target_suit]
        if remaining_same_suit < needed:
            return 0
        # Calculate hypergeometric probability
        probability = (math.comb(remaining_same_suit, needed) / math.comb(total_remaining_cards,
                                                                          needed)) if total_remaining_cards >= needed else 0
        return probability

    elif desired_pattern == 'Three of a Kind':
        # Check if we have a pair already
        for rank, count in rank_counts.items():
            if count == 2:
                remaining_same_rank = 4 - count
                probability = remaining_same_rank / total_remaining_cards
                return probability
        return 0

    elif desired_pattern == 'Straight':
        # Calculate possible straights with kept cards
        # This is a complex calculation; we provide a simplified version
        # Find all possible straights that include kept cards
        possible_sequences = []
        kept_values = set(kept_ranks)
        for start in range(2, 11):
            sequence = set(range(start, start + 5))
            if kept_values.issubset(sequence):
                possible_sequences.append(sequence)
        # Ace-low straight
        if {14, 2, 3, 4, 5}.issubset(kept_values):
            possible_sequences.append({14, 2, 3, 4, 5})

        if not possible_sequences:
            return 0

        # For each possible sequence, calculate missing cards
        prob = 0
        for seq in possible_sequences:
            missing = seq - kept_values
            if len(missing) > num_draws:
                continue
            # Calculate probability of drawing all missing cards
            missing_cards = [card for card in remaining_deck if RANK_MAP[card.split()[0]] in missing]
            if len(missing_cards) < len(missing):
                continue
            prob += math.comb(len(missing_cards), len(missing)) / math.comb(total_remaining_cards, len(missing))
        return prob

    elif desired_pattern == 'Two Pair':
        # If we have one pair, need to draw another pair
        existing_pairs = [rank for rank, cnt in rank_counts.items() if cnt >= 2]
        if existing_pairs:
            # Calculate probability to draw at least another pair
            prob = 0
            for pair_rank in [rank for rank, cnt in remaining_ranks.items() if cnt >= 2 and rank not in existing_pairs]:
                prob += math.comb(remaining_ranks[pair_rank], 2) / math.comb(total_remaining_cards,
                                                                             2) if num_draws >= 2 else 0
            return prob
        return 0

    else:
        return 0


def recommend_discard_strategies(current_hand, remaining_deck, top_n=5):
    """
    Recommend discard strategies to improve the hand.
    """
    # Evaluate current hand
    current_patterns = evaluate_hand(current_hand)
    # Find the best current pattern based on HAND_SCORES
    best_current_pattern = max(current_patterns, key=lambda x: HAND_SCORES.get(x[0], (0, 0))[0])
    best_pattern_name = best_current_pattern[0]
    best_pattern_cards = best_current_pattern[1]
    # Define strong patterns
    strong_patterns = ['Royal Flush', 'Straight Flush', 'Four of a Kind', 'Full House']
    if best_pattern_name in strong_patterns:
        # Hand is already strong; recommend keeping it
        score, calculation = calculate_pattern_score(best_pattern_name, best_pattern_cards)
        return [{
            'discard': [],
            'pattern': best_pattern_name,
            'score': score,
            'probability': 1.0,
            'kept_cards': current_hand,
            'calculation': calculation
        }]

    # Potential patterns to aim for, prioritized by HAND_SCORES
    potential_patterns = ['Four of a Kind', 'Full House', 'Flush', 'Three of a Kind', 'Two Pair', 'Straight']
    # Filter patterns that have a higher HAND_SCORES than the current best pattern
    current_score = HAND_SCORES.get(best_pattern_name, (0, 0))[0]
    potential_patterns = [p for p in potential_patterns if HAND_SCORES.get(p, (0, 0))[0] > current_score]

    if not potential_patterns:
        # No higher patterns available; recommend keeping current hand
        score, calculation = calculate_pattern_score(best_pattern_name, best_pattern_cards)
        return [{
            'discard': [],
            'pattern': best_pattern_name,
            'score': score,
            'probability': 1.0,
            'kept_cards': current_hand,
            'calculation': calculation
        }]

    # Initialize list to hold all possible strategies
    strategy_scores = []

    # For each potential pattern, determine which cards to keep and which to discard
    for pattern in potential_patterns:
        if pattern == 'Four of a Kind':
            # Keep all cards that are part of any Three of a Kind
            rank_counts = Counter([RANK_MAP[card.split()[0]] for card in current_hand])
            threes = [rank for rank, cnt in rank_counts.items() if cnt >= 3]
            if threes:
                # Assuming only one three of a kind
                keep_rank = threes[0]
                kept_cards = [card for card in current_hand if RANK_MAP[card.split()[0]] == keep_rank]
                discard_cards = [card for card in current_hand if RANK_MAP[card.split()[0]] != keep_rank]
                # Only keep three cards of the same rank
                # To maximize probability, keep exactly three
                kept_cards = kept_cards[:3]
                discard_cards = [card for card in current_hand if card not in kept_cards]
                num_draws = len(discard_cards)
                # Ensure that remaining_deck is passed
                probability = calculate_pattern_probability(kept_cards, pattern, remaining_deck, num_draws)
                if probability > 0:
                    score, calculation = calculate_pattern_score(pattern, kept_cards)
                    expected_score = probability * score
                    strategy_scores.append({
                        'discard': discard_cards,
                        'pattern': pattern,
                        'score': expected_score,
                        'probability': probability,
                        'kept_cards': kept_cards,
                        'calculation': calculation
                    })

        elif pattern == 'Full House':
            # Keep any Three of a Kind and any Pair
            rank_counts = Counter([RANK_MAP[card.split()[0]] for card in current_hand])
            threes = [rank for rank, cnt in rank_counts.items() if cnt >= 3]
            pairs = [rank for rank, cnt in rank_counts.items() if cnt >= 2 and rank not in threes]
            if threes:
                keep_rank = threes[0]
                kept_cards = [card for card in current_hand if RANK_MAP[card.split()[0]] == keep_rank]
                if pairs:
                    # Keep the pair as well
                    pair_rank = pairs[0]
                    pair_cards = [card for card in current_hand if RANK_MAP[card.split()[0]] == pair_rank]
                    kept_cards.extend(pair_cards)
                num_draws = len(current_hand) - len(kept_cards)
                discard_cards = [card for card in current_hand if card not in kept_cards]
                probability = calculate_pattern_probability(kept_cards, pattern, remaining_deck, num_draws)
                if probability > 0:
                    score, calculation = calculate_pattern_score(pattern, kept_cards)
                    expected_score = probability * score
                    strategy_scores.append({
                        'discard': discard_cards,
                        'pattern': pattern,
                        'score': expected_score,
                        'probability': probability,
                        'kept_cards': kept_cards,
                        'calculation': calculation
                    })

        elif pattern == 'Flush':
            # Keep the suit with the highest count
            suit_counts = Counter([card.split()[1] for card in current_hand])
            if suit_counts:
                target_suit, count = suit_counts.most_common(1)[0]
                kept_cards = [card for card in current_hand if card.split()[1] == target_suit]
                discard_cards = [card for card in current_hand if card.split()[1] != target_suit]
                num_draws = len(discard_cards)
                probability = calculate_pattern_probability(kept_cards, pattern, remaining_deck, num_draws)
                if probability > 0:
                    score, calculation = calculate_pattern_score(pattern, kept_cards)
                    expected_score = probability * score
                    strategy_scores.append({
                        'discard': discard_cards,
                        'pattern': pattern,
                        'score': expected_score,
                        'probability': probability,
                        'kept_cards': kept_cards,
                        'calculation': calculation
                    })

        elif pattern == 'Three of a Kind':
            # Keep all cards that are part of any Pair
            rank_counts = Counter([RANK_MAP[card.split()[0]] for card in current_hand])
            pairs = [rank for rank, cnt in rank_counts.items() if cnt >= 2]
            if pairs:
                keep_rank = pairs[0]
                kept_cards = [card for card in current_hand if RANK_MAP[card.split()[0]] == keep_rank]
                discard_cards = [card for card in current_hand if RANK_MAP[card.split()[0]] != keep_rank]
                # Keep exactly two cards of the pair
                kept_cards = kept_cards[:2]
                discard_cards = [card for card in current_hand if card not in kept_cards]
                num_draws = len(discard_cards)
                probability = calculate_pattern_probability(kept_cards, pattern, remaining_deck, num_draws)
                if probability > 0:
                    score, calculation = calculate_pattern_score(pattern, kept_cards)
                    expected_score = probability * score
                    strategy_scores.append({
                        'discard': discard_cards,
                        'pattern': pattern,
                        'score': expected_score,
                        'probability': probability,
                        'kept_cards': kept_cards,
                        'calculation': calculation
                    })

        elif pattern == 'Two Pair':
            # Keep the two existing pairs
            rank_counts = Counter([RANK_MAP[card.split()[0]] for card in current_hand])
            pairs = [rank for rank, cnt in rank_counts.items() if cnt >= 2]
            if len(pairs) >= 2:
                keep_ranks = pairs[:2]
                kept_cards = [card for card in current_hand if RANK_MAP[card.split()[0]] in keep_ranks]
                discard_cards = [card for card in current_hand if card not in kept_cards]
                num_draws = len(discard_cards)
                probability = calculate_pattern_probability(kept_cards, pattern, remaining_deck, num_draws)
                if probability > 0:
                    score, calculation = calculate_pattern_score(pattern, kept_cards)
                    expected_score = probability * score
                    strategy_scores.append({
                        'discard': discard_cards,
                        'pattern': pattern,
                        'score': expected_score,
                        'probability': probability,
                        'kept_cards': kept_cards,
                        'calculation': calculation
                    })

        elif pattern == 'Straight':
            # Keep cards that can form a straight
            # Simplified: keep the cards with consecutive ranks
            kept_ranks = [RANK_MAP[card.split()[0]] for card in current_hand]
            kept_ranks = sorted(set(kept_ranks))
            sequences = []
            for start in range(2, 11):
                seq = set(range(start, start + 5))
                if seq.intersection(kept_ranks):
                    sequences.append(seq)
            # Ace-low straight
            if {14, 2, 3, 4, 5}.issubset(kept_ranks):
                sequences.append({14, 2, 3, 4, 5})
            # Find the sequence with the most overlap
            best_seq = max(sequences, key=lambda s: len(s.intersection(kept_ranks)), default=None)
            if best_seq:
                needed = best_seq - set(kept_ranks)
                # Keep all cards that are part of the best_seq
                kept_cards = [card for card in current_hand if RANK_MAP[card.split()[0]] in best_seq]
                discard_cards = [card for card in current_hand if RANK_MAP[card.split()[0]] not in best_seq]
                num_draws = len(discard_cards)
                probability = calculate_pattern_probability(kept_cards, pattern, remaining_deck, num_draws)
                if probability > 0:
                    score, calculation = calculate_pattern_score(pattern, kept_cards)
                    expected_score = probability * score
                    strategy_scores.append({
                        'discard': discard_cards,
                        'pattern': pattern,
                        'score': expected_score,
                        'probability': probability,
                        'kept_cards': kept_cards,
                        'calculation': calculation
                    })

        # Additional patterns can be added here with similar logic

    # Calculate expected score and collect strategies

    # Now, after collecting all strategies, sort and return top_n
    # Sort strategies by expected score in descending order
    sorted_strategies = sorted(strategy_scores, key=lambda x: x['score'], reverse=True)

    # Select top_n unique discard strategies
    top_strategies = []
    seen_discards = set()
    for strategy in sorted_strategies:
        discard_key = tuple(sorted(strategy['discard']))
        if discard_key not in seen_discards:
            seen_discards.add(discard_key)
            top_strategies.append(strategy)
            if len(top_strategies) >= top_n:
                break

    return top_strategies


def main(top_n=5):
    try:
        # Parse user input
        user_input = input("Enter the playing cards string (e.g., 7h10h2s3dah9c): ")
        current_hand, n = parse_playing_cards(user_input)
        print(f"\nParsed Cards ({n}):")
        for card in current_hand:
            print(card)
        top_strategies = recommend_discard_strategies(current_hand, top_n)
        if top_strategies:
            print("\nTop Discard Recommendations:")
            for idx, strategy in enumerate(top_strategies, 1):
                discard_cards = strategy['discard']
                pattern = strategy['pattern']
                score = strategy['score']
                probability = strategy['probability']
                kept_cards = strategy['kept_cards']
                calculation = strategy.get('calculation', '')
                print(f"\nRank {idx}:")
                print(f"Pattern to Aim For: {pattern}")
                if not discard_cards:
                    print("Recommendation: Keep your current hand; it's already strong.")
                    print(f"Expected Score: {score}")
                    print(f"Score Calculation: {calculation}")
                    print("Probability: 100%")
                else:
                    print(f"Cards to Discard: {', '.join(discard_cards)}")
                    print(f"Kept Cards: {', '.join(kept_cards)}")
                    print(f"Probability: {probability * 100:.2f}%")
                    print(f"Expected Score: {score:.2f}")
                    print(f"Score Calculation: {calculation}")
        else:
            print("\nNo valid discard strategies found.")
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()