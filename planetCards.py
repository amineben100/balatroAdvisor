# planetCards.py

from dataclasses import dataclass

@dataclass
class PlanetCard:
    """Represents a Planet Card that boosts specific poker hand scores."""
    name: str
    associated_hand: str
    chip_value_bonus: int
    multiplier_bonus: int
    is_secret: bool = False
    quantity: int = 0  # Number of cards the user has

    def add(self, qty=1):
        """Add one or more copies of the Planet Card."""
        self.quantity += qty

    def remove(self, qty=1):
        """Remove one or more copies of the Planet Card."""
        self.quantity = max(0, self.quantity - qty)

    def is_active(self):
        """Check if the Planet Card is active (i.e., quantity > 0)."""
        return self.quantity > 0

    def __str__(self):
        """String representation of the Planet Card."""
        status = f"Quantity: {self.quantity}" if self.is_active() else "Inactive"
        return (f"{self.name} (Boosts {self.associated_hand}) - "
                f"Chip Bonus: +{self.chip_value_bonus}/card, "
                f"Multiplier Bonus: +{self.multiplier_bonus}/card, {status}")

# Define all Planet Cards
PLANET_CARDS = {
    'Pluto': PlanetCard('Pluto', 'High Card', chip_value_bonus=10, multiplier_bonus=1),
    'Mercury': PlanetCard('Mercury', 'Pair', chip_value_bonus=15, multiplier_bonus=1),
    'Uranus': PlanetCard('Uranus', 'Two Pair', chip_value_bonus=20, multiplier_bonus=1),
    'Venus': PlanetCard('Venus', 'Three of a Kind', chip_value_bonus=20, multiplier_bonus=2),
    'Saturn': PlanetCard('Saturn', 'Straight', chip_value_bonus=30, multiplier_bonus=3),
    'Jupiter': PlanetCard('Jupiter', 'Flush', chip_value_bonus=15, multiplier_bonus=2),
    'Earth': PlanetCard('Earth', 'Full House', chip_value_bonus=25, multiplier_bonus=2),
    'Mars': PlanetCard('Mars', 'Four of a Kind', chip_value_bonus=30, multiplier_bonus=3),
    'Neptune': PlanetCard('Neptune', 'Straight Flush', chip_value_bonus=40, multiplier_bonus=4),
    # Secret Planet Cards
    'Eris': PlanetCard('Eris', 'Four of a Kind', chip_value_bonus=50, multiplier_bonus=5, is_secret=True),
    'Ceres': PlanetCard('Ceres', 'Full House', chip_value_bonus=45, multiplier_bonus=4, is_secret=True),
    'Planet X': PlanetCard('Planet X', 'Straight Flush', chip_value_bonus=60, multiplier_bonus=6, is_secret=True)
}

def list_planet_cards():
    """Display all Planet Cards and their current status."""
    for card in PLANET_CARDS.values():
        print(card)

def add_planet_card(name, qty=1):
    """Add one or more copies of a Planet Card to the user's collection."""
    card = PLANET_CARDS.get(name)
    if card:
        card.add(qty)
        print(f"Added {qty} {name} card(s). Total now: {card.quantity}")
    else:
        print(f"{name} does not exist.")

def remove_planet_card(name, qty=1):
    """Remove one or more copies of a Planet Card from the user's collection."""
    card = PLANET_CARDS.get(name)
    if card:
        card.remove(qty)
        print(f"Removed {qty} {name} card(s). Total now: {card.quantity}")
    else:
        print(f"{name} does not exist.")

def get_active_planet_cards():
    """Retrieve all active Planet Cards (those with quantity > 0)."""
    return [card for card in PLANET_CARDS.values() if card.is_active()]

def calculate_hand_score(hand_name, base_chip, base_multiplier):
    """
    Calculate the adjusted score for a hand based on active Planet Cards.

    Parameters:
    - hand_name (str): The name of the poker hand.
    - base_chip (int): The base chip value from HAND_SCORES.
    - base_multiplier (int): The base multiplier from HAND_SCORES.

    Returns:
    - adjusted_chip (int): The new chip value after applying bonuses.
    - adjusted_multiplier (int): The new multiplier after applying bonuses.
    """
    adjusted_chip = base_chip
    adjusted_multiplier = base_multiplier
    for card in get_active_planet_cards():
        if card.associated_hand == hand_name:
            adjusted_chip += card.chip_value_bonus * card.quantity
            adjusted_multiplier += card.multiplier_bonus * card.quantity
    return adjusted_chip, adjusted_multiplier