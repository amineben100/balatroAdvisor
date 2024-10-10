# balatroAdvisor.py
import os
import time
import threading
from play import parse_playing_cards, find_best_hands, update_hand_scores, HAND_SCORES
from discard import recommend_discard_strategies
from planetCards import PLANET_CARDS, list_planet_cards, add_planet_card, remove_planet_card, get_active_planet_cards

# Attempt to import colorama for colored output
try:
    from colorama import init, Fore, Style

    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


def clear_screen():
    """Clear the console screen without error messages."""
    try:
        if os.name == 'nt':
            os.system('cls')
        else:
            import subprocess
            subprocess.run(['clear'], stderr=subprocess.DEVNULL)
    except Exception:
        pass


def display_hacker_banner():
    """Display the hacker-style banner for Balatro Advisor."""
    banner = f"""
{Fore.GREEN if COLORAMA_AVAILABLE else ''}██████╗  █████╗ ██╗      █████╗ ████████╗██████╗  ██████╗ 
██╔══██╗██╔══██╗██║     ██╔══██╗╚══██╔══╝██╔══██╗██╔═══██╗
██████╔╝███████║██║     ███████║   ██║   ██████╔╝██║   ██║
██╔══██ ██╔══██║██║     ██╔══██║   ██║   ██╔══██║██║   ██║
██████╔╝██║  ██║███████╗██║  ██║   ██║   ██║  ██║╚██████╔╝
╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ 
                   Balatro Advisor v2.5                                  
{Style.RESET_ALL if COLORAMA_AVAILABLE else ''}
    """
    print(banner)


def manage_planet_cards():
    """Allow users to add or remove Planet Cards by typing the planet name or -planet name."""
    # Define secret planets
    secret_planets = {'Planet X', 'Eris', 'Ceres'}

    while True:
        print("\n--- Planet Cards Menu ---")
        # Display only non-secret planet names with their current quantities
        for planet, card in PLANET_CARDS.items():
            if planet not in secret_planets:
                print(f"{planet}: {card.quantity}")

        print("\nInstructions:")
        print(" - To add a Planet Card, type its name (e.g., 'Earth').")
        print(" - To remove a Planet Card, type '-' followed by its name (e.g., '-Earth').")
        print(" - Type 'back' to return to the main menu.")

        user_input = input("Your choice: ").strip()

        if user_input.lower() == 'back':
            break
        elif user_input.startswith('-'):
            # Attempt to remove a Planet Card
            planet_name = user_input[1:].strip().title()
            if planet_name in PLANET_CARDS:
                card = PLANET_CARDS[planet_name]
                if card.quantity > 0:
                    card.remove()
                    print(f"Removed one {planet_name} card. Total now: {card.quantity}")
                    update_hand_scores()  # Update HAND_SCORES after removal
                else:
                    print(f"No active {planet_name} cards to remove.")
            else:
                print("Invalid Planet Card name. Please try again.")
        else:
            # Attempt to add a Planet Card
            planet_name = user_input.strip().title()
            if planet_name in PLANET_CARDS:
                card = PLANET_CARDS[planet_name]
                card.add()
                print(f"Added one {planet_name} card. Total now: {card.quantity}")
                update_hand_scores()  # Update HAND_SCORES after addition
            else:
                print("Invalid Planet Card name. Please try again.")
def get_shorthand(card):
    """
    Convert a full card name to its shorthand representation.

    Parameters:
    - card (str): Full card name (e.g., 'Ace Spade').

    Returns:
    - str: Shorthand representation (e.g., 'as').
    """
    value_map = {
        'Ace': 'a',
        '2': '2',
        '3': '3',
        '4': '4',
        '5': '5',
        '6': '6',
        '7': '7',
        '8': '8',
        '9': '9',
        '10': '10',
        'Jack': 'j',
        'Queen': 'q',
        'King': 'k'
    }
    suit_map = {
        'Heart': 'h',
        'Diamond': 'd',
        'Spade': 's',
        'Club': 'c'
    }

    try:
        value, suit = card.split()
        value_short = value_map.get(value, value[0].lower())
        suit_short = suit_map.get(suit, '?')  # '?' for unknown suits
        return f"{value_short}{suit_short}"
    except ValueError:
        # Handle unexpected card format
        print(f"Warning: Unable to parse card '{card}'. Using original string.")
        return card.lower()

def print_delayed(lines, delay=0.07):
    """Print lines with a small delay between each line."""
    for line in lines:
        print(line)
        time.sleep(delay)


def format_hand(cards):
    """Convert the full card names to a concise format with suit symbols (e.g., 'Ace Heart' -> 'A♥')."""
    suit_symbols = {'Heart': '♥', 'Diamond': '♦', 'Spade': '♠', 'Club': '♣'}
    formatted = []
    for card in cards:
        try:
            value, suit = card.split()
            # Handle special cases for face cards
            if value in ['10', 'Jack', 'Queen', 'King', 'Ace']:
                value_symbol = value[0] if value != '10' else '10'
            else:
                value_symbol = value[0]
            suit_symbol = suit_symbols.get(suit, '?')  # '?' for unknown suits
            formatted.append(f"{value_symbol}{suit_symbol}")
        except ValueError:
            formatted.append(card)  # In case of unexpected format
    return ' '.join(formatted)


def get_card_value(card):
    """Helper function to get the numerical value of a card."""
    value_map = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
        '7': 7, '8': 8, '9': 9, '10': 10,
        'Jack': 11, 'Queen': 12, 'King': 13, 'Ace': 14
    }
    value, _ = card.split()
    return value_map.get(value, 0)


def calculate_high_card_score(card):
    """Calculate a score for the High Card pattern based on its value."""
    value = get_card_value(card)
    # Example scoring: score is equal to card value
    return value


def display_best_hand_recommendation(cards):
    """Show the best play recommendation and return top_hands."""
    top_hands = find_best_hands(cards, top_n=1)
    if top_hands:
        hand = top_hands[0]
        formatted_hand = format_hand(hand['pattern_cards'])
        lines = [
            f"\n>> {Fore.CYAN if COLORAMA_AVAILABLE else ''}Best Hand Recommendation:{Style.RESET_ALL if COLORAMA_AVAILABLE else ''}",
            f"   Pattern: {hand['pattern']}",
            f"   Cards: {formatted_hand}",
            f"   Calculation: {hand['calculation']}",
            f"   Score: {hand['score']}\n"
        ]
        print_delayed(lines)
    else:
        # **Ensure at least a High Card recommendation exists**
        high_card = max(cards, key=lambda card: get_card_value(card))
        lines = [
            f"\n>> {Fore.CYAN if COLORAMA_AVAILABLE else ''}Best Hand Recommendation:{Style.RESET_ALL if COLORAMA_AVAILABLE else ''}",
            f"   Pattern: High Card",
            f"   Cards: {format_hand([high_card])}",
            f"   Calculation: High card value",
            f"   Score: {calculate_high_card_score(high_card)}\n"
        ]
        print_delayed(lines)
        # Create a dummy hand for consistency
        top_hands = [{
            'pattern': 'High Card',
            'pattern_cards': [high_card],
            'calculation': 'High card value',
            'score': calculate_high_card_score(high_card)
        }]
    return top_hands


def display_best_discard_recommendation(current_hand, best_play_pattern, remaining_deck):
    """Show the best discard recommendation."""
    top_discards = recommend_discard_strategies(current_hand, remaining_deck, top_n=1)
    if top_discards:
        strategy = top_discards[0]
        if best_play_pattern and strategy['pattern'] == best_play_pattern and not strategy['discard']:
            # If the best play is already the current hand's pattern and no discard is recommended
            line = f">> {Fore.MAGENTA if COLORAMA_AVAILABLE else ''}Best Discard Recommendation:{Style.RESET_ALL if COLORAMA_AVAILABLE else ''} Play your current hand; it's already strong.\n"
            print_delayed([line])
        else:
            formatted_discard = format_hand(strategy['discard'])
            formatted_kept = format_hand(strategy['kept_cards'])
            probability = f"{strategy['probability'] * 100:.2f}%"
            expected_score = f"{strategy['score']:.2f}"
            lines = [
                f"\n>> {Fore.MAGENTA if COLORAMA_AVAILABLE else ''}Best Discard Recommendation:{Style.RESET_ALL if COLORAMA_AVAILABLE else ''}",
                f"   Pattern to Aim For: {strategy['pattern']}",
                f"   Discard: {formatted_discard}",
                f"   Kept Cards: {formatted_kept}",
                f"   Probability: {probability}"
            ]
            print_delayed(lines)
    else:
        print_delayed(["\n>> No valid discard recommendations available.\n"])


def show_deck_table(remaining_deck):
    """Display the remaining deck as a table categorized by rank and suit."""
    ranks = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
    suits = ['Heart', 'Diamond', 'Spade', 'Club']

    # Initialize a dictionary to map suits to their ranks
    deck_dict = {suit: [] for suit in suits}
    for card in remaining_deck:
        value, suit = card.split()
        deck_dict[suit].append(value)

    # Sort the ranks within each suit
    for suit in suits:
        deck_dict[suit].sort(key=lambda x: get_card_value(f"{x} {suit}"))

    # Prepare the table header
    header = f"{'Rank':<10} " + " ".join([f"{suit[:3]}" for suit in suits])
    print(header)
    print("-" * len(header))

    # Iterate through each rank and display presence in suits
    for rank in ranks:
        row = f"{rank:<10} "
        for suit in suits:
            card = f"{rank} {suit}"
            if card in remaining_deck:
                display_card = format_hand([card]).replace(" ", "")
            else:
                display_card = "--"
            row += f"{display_card:<5} "
        print(row)


def display_remaining_card_count(remaining_deck):
    """Display the number of remaining cards in the deck."""
    print(f"\n>> Cards Remaining in Deck: {len(remaining_deck)}\n")


def display_remaining_deck(remaining_deck):
    """Show the cards still available in the deck in a table format."""
    display_remaining_card_count(remaining_deck)
    show_deck_table(remaining_deck)


def loading_indicator(stop_event):
    """Display dynamic loading messages based on elapsed time."""
    start_time = time.time()
    messages = [
        (10, "Meditating..."),
        (30, "Pondering existential questions..."),
        (60, "Reaching enlightenment..."),
        (120, "Achieving omniscience...")
    ]
    message_idx = 0
    while not stop_event.is_set():
        elapsed = time.time() - start_time
        if message_idx < len(messages) and elapsed >= messages[message_idx][0]:
            print(f"{messages[message_idx][1]}", flush=True)
            message_idx += 1
        time.sleep(1)  # Check every second


def update_deck(current_deck, cards_to_remove):
    """
    Remove specific cards from the current deck in place.

    Parameters:
    - current_deck: Set of remaining cards in the deck.
    - cards_to_remove: Iterable of cards to remove from the deck.

    Returns:
    - None
    """
    current_deck.difference_update(cards_to_remove)


def show_detailed_options():
    """Display menu options for further details."""
    print("\nOptions:")
    print("p - View all play recommendations")
    print("d - View all discard recommendations")
    print("deck - View the cards remaining in the deck")
    print("back - Return to the previous menu")
    print("go - Input a new set of cards")
    choice = input("Your choice: ").strip().lower()
    return choice


def display_all_play_recommendations(cards):
    """Show all play recommendations with calculations."""
    top_hands = find_best_hands(cards, top_n=5)
    if not top_hands:
        # **Ensure at least a High Card recommendation exists**
        high_card = max(cards, key=lambda card: get_card_value(card))
        top_hands = [{
            'pattern': 'High Card',
            'pattern_cards': [high_card],
            'calculation': 'High card value',
            'score': calculate_high_card_score(high_card)
        }]
    lines = ["\n>> Top 5 Play Recommendations:"]
    for idx, hand in enumerate(top_hands, 1):
        formatted_hand = format_hand(hand['pattern_cards'])
        lines.extend([
            f"\nRank {idx}:",
            f"Pattern: {hand['pattern']}",
            f"Cards: {formatted_hand}",
            f"Calculation: {hand['calculation']}",
            f"Total Score: {hand['score']}"
        ])
    print_delayed(lines)


def display_all_discard_recommendations(current_hand, remaining_deck):
    """Show all discard recommendations with probability and expected score."""
    top_discards = recommend_discard_strategies(current_hand, remaining_deck, top_n=5)
    lines = ["\n>> Top 5 Discard Recommendations:"]
    if not top_discards:
        lines.append("\n>> No discard recommendations available.\n")
    else:
        for idx, strategy in enumerate(top_discards, 1):
            formatted_discard = format_hand(strategy['discard'])
            formatted_kept = format_hand(strategy['kept_cards'])
            probability = f"{strategy['probability'] * 100:.2f}%"
            expected_score = f"{strategy['score']:.2f}"
            lines.extend([
                f"\nRank {idx}:",
                f"Pattern to Aim For: {strategy['pattern']}",
                f"Discard: {formatted_discard if formatted_discard else 'None'}",
                f"Kept Cards: {formatted_kept}",
                f"Probability: {probability}",
                f"Expected Score Increase: {expected_score}"
            ])
    print_delayed(lines)


def process_card_input(user_input, remaining_deck, previous_hand):
    """
    Process the card input string, update the deck, and display recommendations.

    Parameters:
    - user_input: String input representing the user's hand.
    - remaining_deck: Set of remaining cards in the deck.
    - previous_hand: Set of cards from the previous hand.

    Returns:
    - Updated current_hand (set) or None if an error occurs.
    """
    stop_event = threading.Event()
    loader_thread = threading.Thread(target=loading_indicator, args=(stop_event,))
    loader_thread.start()

    # Display "Calculating Best Outcomes..." message immediately
    print("\nCalculating Best Outcomes...", end='', flush=True)
    time.sleep(0.4)  # Simulate loading delay after message is shown

    try:
        # Parse the input cards
        new_hand, n = parse_playing_cards(user_input)
        new_hand_set = set(new_hand)

        # Identify new cards by comparing with the previous hand
        if previous_hand:
            new_cards = new_hand_set - previous_hand
        else:
            new_cards = new_hand_set  # All cards are new if no previous hand

        # Check if new cards are available in the remaining deck
        if not new_cards.issubset(remaining_deck):
            missing = new_cards - remaining_deck
            raise ValueError(f"The following cards are not available in the deck: {', '.join(missing)}")

        # Remove new cards from the deck
        update_deck(remaining_deck, new_cards)

        # Stop the loading indicator
        stop_event.set()
        loader_thread.join()

        # Clear the screen (do not display the banner again)
        clear_screen()

        # Show the parsed hand
        formatted_hand = format_hand(new_hand)
        print_delayed([f"\nYour Hand: {formatted_hand}"])

        # Display Best Hand Recommendation
        top_hands = display_best_hand_recommendation(new_hand)
        best_play_pattern = top_hands[0]['pattern'] if top_hands else None

        # Display Best Discard Recommendation
        display_best_discard_recommendation(new_hand, best_play_pattern, remaining_deck)

        # Display number of remaining cards and the deck
        display_remaining_card_count(remaining_deck)

        return new_hand_set  # Return the updated current hand

    except ValueError as e:
        # Stop the loading indicator in case of error
        stop_event.set()
        loader_thread.join()
        print_delayed([f"\nError: {e}\n"])
        retry = input("Do you want to try again? (y/n): ").strip().lower()
        if retry != 'y':
            print_delayed(["\nExiting Balatro Advisor... Stay sharp!\n"])
            exit(0)
        else:
            clear_screen()
            display_hacker_banner()
            return None


def input_play_game():
    """Handle the Play Game input by prompting for each suit separately."""
    suits = ['Spade', 'Heart', 'Diamond', 'Club']
    collected_cards = []

    for suit in suits:
        while True:
            user_input = input(
                f"Input {suit} card values, separated by a comma (e.g., a,3,j or 0 if none): ").strip().lower()
            if user_input == '0':
                break  # No cards in this suit
            else:
                # Split the input by comma and validate
                card_values = [card.strip().lower() for card in user_input.split(',')]
                valid_values = {'a', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'j', 'q', 'k'}
                if all(card in valid_values for card in card_values):
                    # Convert to full card names
                    for card in card_values:
                        if card == 'a':
                            value = 'Ace'
                        elif card == 'j':
                            value = 'Jack'
                        elif card == 'q':
                            value = 'Queen'
                        elif card == 'k':
                            value = 'King'
                        else:
                            value = card.upper()  # '2', '3', ..., '10'

                        full_card = f"{value} {suit}"
                        collected_cards.append(full_card)
                    break
                else:
                    print(
                        f"Invalid card values detected. Please enter valid values for {suit} (a,2-10,j,q,k) or '0' if none.")

    if not collected_cards:
        print("No cards entered. Exiting Play Game.")
        return None

    # Convert collected_cards to a single string for processing using the helper function
    card_string = ''.join([get_shorthand(card) for card in collected_cards])
    return card_string


def jokers_menu():
    """Placeholder for Jokers menu."""
    while True:
        print("\n--- Jokers Menu ---")
        print("Jokers feature is under development. Stay tuned!")
        print(" - Type 'back' to return to the main menu.")
        user_input = input("Your choice: ").strip().lower()
        if user_input == 'back':
            break
        else:
            print("Invalid choice. Please type 'back' to return.")


def main():
    clear_screen()
    display_hacker_banner()

    # Initialize the full deck
    full_deck = {f"{v} {s}"
                 for v in (list(map(str, range(2, 11))) + ['Jack', 'Queen', 'King', 'Ace'])
                 for s in ['Heart', 'Diamond', 'Spade', 'Club']}
    remaining_deck = set(full_deck)  # Copy of the full deck

    previous_hand = set()  # To store the previous hand

    while True:
        # Prompt for input
        print("\n--- Balatro Advisor Main Menu ---")
        print("Options:")
        print("1. Play Game")
        print("2. Planets")
        print("3. Jokers")

        choice = input("Select an option (1-3): ").strip()

        if choice == '1':
            # Handle Play Game
            card_string = input_play_game()
            if not card_string:
                continue  # If no cards were entered, return to main menu

            # Process the card input and display recommendations
            current_hand = process_card_input(card_string, remaining_deck, previous_hand)
            if current_hand is None:
                continue  # If processing failed, prompt again

            # Update the previous_hand for the next iteration
            previous_hand = current_hand

            # Main loop for detailed view options
            while True:
                choice = show_detailed_options()

                if choice == 'p':
                    display_all_play_recommendations(current_hand)
                elif choice == 'd':
                    display_all_discard_recommendations(current_hand, remaining_deck)
                elif choice == 'deck':
                    display_remaining_deck(remaining_deck)
                elif choice == 'back':
                    break  # Return to the main menu
                elif choice == 'go':
                    # Prompt the user for a new set of cards
                    print("\n--- Enter a New Set of Cards ---")
                    new_card_string = input_play_game()
                    if not new_card_string:
                        print("No cards entered. Returning to detailed options.")
                        continue
                    # Process the new card input
                    new_hand = process_card_input(new_card_string, remaining_deck, previous_hand)
                    if new_hand:
                        previous_hand = new_hand
                        current_hand = new_hand
                    else:
                        print_delayed(["\nInvalid card input. Please try again.\n"])
                else:
                    # Handle unexpected inputs
                    print_delayed(["\nInvalid choice. Please select again.\n"])

                input("\nPress Enter to continue...")
                clear_screen()
                print(f"\nYour Hand: {format_hand(current_hand)}")

        elif choice == '2':
            # Handle Planets
            manage_planet_cards()
            # After managing, continue to main menu
            continue
        elif choice == '3':
            # Handle Jokers
            jokers_menu()
            continue
        else:
            print("Invalid choice. Please select a valid option.")


if __name__ == "__main__":
    main()