# jokers.py

from typing import Dict, Any, List, Callable


class Joker:
    """
    Represents a single Joker with a name and an effect function.
    """

    def __init__(self, name: str, effect: Callable[[Dict[str, Any]], None]):
        """
        Initialize a Joker.

        Parameters:
        - name (str): The name of the Joker.
        - effect (Callable): A function that applies the Joker's effect to the game state.
        """
        self.name = name
        self.effect = effect
        self.enabled = False  # Indicates whether the Joker is enabled

    def apply_effect(self, game_state: Dict[str, Any]):
        """
        Apply the Joker's effect to the game state if enabled.

        Parameters:
        - game_state (dict): The current state of the game.
        """
        if self.enabled:
            self.effect(game_state)
        else:
            print(f"Joker '{self.name}' is not enabled. No effect applied.")


class JokerManager:
    """
    Manages all Jokers: enabling, disabling, listing, and applying their effects.
    """

    def __init__(self):
        """
        Initialize the JokerManager with all Jokers defined.
        """
        self.all_jokers: Dict[str, Joker] = {}
        self.enabled_jokers: List[Joker] = []
        self._initialize_jokers()

    def _initialize_jokers(self):
        """
        Define and initialize all Jokers with their respective effects.
        """

        # Define effect functions for each Joker

        def joker_effect(game_state: Dict[str, Any]):
            """
            "Joker": +4 Mult.
            """
            game_state['multiplier'] += 4
            print(f"Joker 'Joker' applied: +4 Multiplier. Total Multiplier: {game_state['multiplier']}")

        def greedy_joker_effect(game_state: Dict[str, Any]):
            """
            "Greedy Joker": Played cards with Diamond suit give +3 Mult when scored.
            """
            played_cards = game_state.get('played_cards', [])
            if any(card['suit'].lower() == 'diamond' for card in played_cards):
                game_state['multiplier'] += 3
                print(
                    f"Joker 'Greedy Joker' applied: +3 Multiplier for Diamond suit. Total Multiplier: {game_state['multiplier']}")
            else:
                print("Joker 'Greedy Joker' not applied: No played cards with Diamond suit.")

        def lusty_joker_effect(game_state: Dict[str, Any]):
            """
            "Lusty Joker": Played cards with Heart suit give +3 Mult when scored.
            """
            played_cards = game_state.get('played_cards', [])
            if any(card['suit'].lower() == 'heart' for card in played_cards):
                game_state['multiplier'] += 3
                print(
                    f"Joker 'Lusty Joker' applied: +3 Multiplier for Heart suit. Total Multiplier: {game_state['multiplier']}")
            else:
                print("Joker 'Lusty Joker' not applied: No played cards with Heart suit.")

        def wrathful_joker_effect(game_state: Dict[str, Any]):
            """
            "Wrathful Joker": Played cards with Spade suit give +3 Mult when scored.
            """
            played_cards = game_state.get('played_cards', [])
            if any(card['suit'].lower() == 'spade' for card in played_cards):
                game_state['multiplier'] += 3
                print(
                    f"Joker 'Wrathful Joker' applied: +3 Multiplier for Spade suit. Total Multiplier: {game_state['multiplier']}")
            else:
                print("Joker 'Wrathful Joker' not applied: No played cards with Spade suit.")

        def gluttonous_joker_effect(game_state: Dict[str, Any]):
            """
            "Gluttonous Joker": Played cards with Club suit give +3 Mult when scored.
            """
            played_cards = game_state.get('played_cards', [])
            if any(card['suit'].lower() == 'club' for card in played_cards):
                game_state['multiplier'] += 3
                print(
                    f"Joker 'Gluttonous Joker' applied: +3 Multiplier for Club suit. Total Multiplier: {game_state['multiplier']}")
            else:
                print("Joker 'Gluttonous Joker' not applied: No played cards with Club suit.")

        def jolly_joker_effect(game_state: Dict[str, Any]):
            """
            "Jolly Joker": +8 Mult if played hand contains a Pair.
            """
            hand = game_state.get('hand', [])
            if check_hand_pattern(hand, "Pair"):
                game_state['multiplier'] += 8
                print(
                    f"Joker 'Jolly Joker' applied: +8 Multiplier for Pair. Total Multiplier: {game_state['multiplier']}")
            else:
                print("Joker 'Jolly Joker' not applied: Hand does not contain a Pair.")

        def zany_joker_effect(game_state: Dict[str, Any]):
            """
            "Zany Joker": +12 Mult if played hand contains a Three of a Kind.
            """
            hand = game_state.get('hand', [])
            if check_hand_pattern(hand, "Three of a Kind"):
                game_state['multiplier'] += 12
                print(
                    f"Joker 'Zany Joker' applied: +12 Multiplier for Three of a Kind. Total Multiplier: {game_state['multiplier']}")
            else:
                print("Joker 'Zany Joker' not applied: Hand does not contain a Three of a Kind.")

        def mad_joker_effect(game_state: Dict[str, Any]):
            """
            "Mad Joker": +10 Mult if played hand contains a Two Pair.
            """
            hand = game_state.get('hand', [])
            if check_hand_pattern(hand, "Two Pair"):
                game_state['multiplier'] += 10
                print(
                    f"Joker 'Mad Joker' applied: +10 Multiplier for Two Pair. Total Multiplier: {game_state['multiplier']}")
            else:
                print("Joker 'Mad Joker' not applied: Hand does not contain a Two Pair.")

        def crazy_joker_effect(game_state: Dict[str, Any]):
            """
            "Crazy Joker": +12 Mult if played hand contains a Straight.
            """
            hand = game_state.get('hand', [])
            if check_hand_pattern(hand, "Straight"):
                game_state['multiplier'] += 12
                print(
                    f"Joker 'Crazy Joker' applied: +12 Multiplier for Straight. Total Multiplier: {game_state['multiplier']}")
            else:
                print("Joker 'Crazy Joker' not applied: Hand does not contain a Straight.")

        def droll_joker_effect(game_state: Dict[str, Any]):
            """
            "Droll Joker": +10 Mult if played hand contains a Flush.
            """
            hand = game_state.get('hand', [])
            if check_hand_pattern(hand, "Flush"):
                game_state['multiplier'] += 10
                print(
                    f"Joker 'Droll Joker' applied: +10 Multiplier for Flush. Total Multiplier: {game_state['multiplier']}")
            else:
                print("Joker 'Droll Joker' not applied: Hand does not contain a Flush.")

        # Create Joker instances
        self.all_jokers = {
            "Joker": Joker("Joker", joker_effect),
            "Greedy Joker": Joker("Greedy Joker", greedy_joker_effect),
            "Lusty Joker": Joker("Lusty Joker", lusty_joker_effect),
            "Wrathful Joker": Joker("Wrathful Joker", wrathful_joker_effect),
            "Gluttonous Joker": Joker("Gluttonous Joker", gluttonous_joker_effect),
            "Jolly Joker": Joker("Jolly Joker", jolly_joker_effect),
            "Zany Joker": Joker("Zany Joker", zany_joker_effect),
            "Mad Joker": Joker("Mad Joker", mad_joker_effect),
            "Crazy Joker": Joker("Crazy Joker", crazy_joker_effect),
            "Droll Joker": Joker("Droll Joker", droll_joker_effect)
        }

    def enable_joker(self, joker_name: str):
        """
        Enable a Joker by its name.

        Parameters:
        - joker_name (str): The name of the Joker to enable.
        """
        joker = self.all_jokers.get(joker_name)
        if joker:
            if not joker.enabled:
                joker.enabled = True
                self.enabled_jokers.append(joker)
                print(f"Joker '{joker.name}' is now Enabled.")
            else:
                print(f"Joker '{joker.name}' is already Enabled.")
        else:
            print(f"Joker '{joker_name}' does not exist.")

    def disable_joker(self, joker_name: str):
        """
        Disable a Joker by its name.

        Parameters:
        - joker_name (str): The name of the Joker to disable.
        """
        joker = self.all_jokers.get(joker_name)
        if joker:
            if joker.enabled:
                joker.enabled = False
                self.enabled_jokers.remove(joker)
                print(f"Joker '{joker.name}' has been Disabled.")
            else:
                print(f"Joker '{joker.name}' is already Disabled.")
        else:
            print(f"Joker '{joker_name}' does not exist.")

    def list_enabled_jokers(self):
        """
        List all currently enabled Jokers.
        """
        if not self.enabled_jokers:
            print("No Jokers are currently enabled.")
            return
        print("Enabled Jokers:")
        for joker in self.enabled_jokers:
            print(f"- {joker.name} [Enabled]")

    def apply_jokers_effects(self, event: str, game_state: Dict[str, Any]):
        """
        Apply effects of all enabled Jokers based on the triggered event.

        Parameters:
        - event (str): The game event triggering the effects (e.g., "scoring").
        - game_state (dict): The current state of the game.
        """
        print(f"\n--- Applying Joker Effects for Event: '{event}' ---")
        for joker in self.enabled_jokers:
            if event.lower() == "scoring":
                joker.apply_effect(game_state)
        print("--- Joker Effects Applied ---\n")


def check_hand_pattern(hand: List[Dict[str, str]], pattern: str) -> bool:
    """
    Check if the hand contains the specified pattern.

    Parameters:
    - hand (list): List of card dictionaries with 'rank' and 'suit'.
    - pattern (str): The pattern to check for (e.g., "Pair", "Flush").

    Returns:
    - bool: True if the pattern is present, False otherwise.
    """
    ranks = [card['rank'].lower() for card in hand]
    suits = [card['suit'].lower() for card in hand]

    if pattern.lower() == "pair":
        return any(ranks.count(rank) >= 2 for rank in set(ranks))
    elif pattern.lower() == "three of a kind":
        return any(ranks.count(rank) >= 3 for rank in set(ranks))
    elif pattern.lower() == "two pair":
        return sum(ranks.count(rank) >= 2 for rank in set(ranks)) >= 2
    elif pattern.lower() == "straight":
        # Simplified straight detection assuming no duplicate ranks
        rank_order = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                      'jack': 11, 'queen': 12, 'king': 13, 'ace': 14}
        sorted_ranks = sorted([rank_order.get(rank, 0) for rank in ranks])
        unique_sorted = sorted(set(sorted_ranks))
        for i in range(len(unique_sorted) - 4):
            window = unique_sorted[i:i + 5]
            if window[-1] - window[0] == 4:
                return True
        return False
    elif pattern.lower() == "flush":
        return any(suits.count(suit) >= 5 for suit in set(suits))
    else:
        # Add more patterns as needed
        return False


# Example Usage
if __name__ == "__main__":
    # Initialize Joker Manager
    manager = JokerManager()

    # Example Game State
    game_state = {
        'multiplier': 1,
        'played_cards': [
            {'rank': 'Jack', 'suit': 'Diamond'},
            {'rank': 'Queen', 'suit': 'Diamond'},
            {'rank': 'King', 'suit': 'Spade'},
            {'rank': '7', 'suit': 'Heart'},
            {'rank': '7', 'suit': 'Heart'}
        ],
        'hand': [
            {'rank': '7', 'suit': 'Heart'},
            {'rank': '7', 'suit': 'Heart'},
            {'rank': 'King', 'suit': 'Spade'},
            {'rank': 'Queen', 'suit': 'Diamond'},
            {'rank': 'Jack', 'suit': 'Diamond'}
        ]
    }

    # Enable some Jokers
    manager.enable_joker("Joker")
    manager.enable_joker("Greedy Joker")
    manager.enable_joker("Jolly Joker")

    # List enabled Jokers
    manager.list_enabled_jokers()

    # Apply Joker effects during a 'scoring' event
    manager.apply_jokers_effects("scoring", game_state)

    # Display updated game state
    print(f"Updated Game State: {game_state}")

    # Disable a Joker
    manager.disable_joker("Greedy Joker")

    # List enabled Jokers after disabling
    manager.list_enabled_jokers()

    # Apply Joker effects again during another 'scoring' event
    manager.apply_jokers_effects("scoring", game_state)

    # Display updated game state
    print(f"Updated Game State: {game_state}")