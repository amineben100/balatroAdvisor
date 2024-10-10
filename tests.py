kskhkdqdjs7s4h4c
2c2d3dqdjs7s8h7h
ac2d3dqdqs7d8c7h


asacad7d5d4s4h3h

# 1. High card only; no pairs or stronger hands
test_1 = "2h4d6s8cJdKs9h"

# 2. Pair of 5s; expect 'Pair' as the highest-ranked pattern
test_2 = "5d5s7h3c8sKdJh"

# 3. Two pairs: 9s and 3s
test_3 = "9h9d3s3c7hKcQd"

# 4. Three of a Kind: Kings
test_4 = "KhKsKd8d2c4s3h"

# 5. Full House: Aces over 4s
test_5 = "AcAhAs4c4d7h2s"

# 6. Four of a Kind: Queens
test_6 = "QhQsQdQc7s2h5d"

# 7. Straight: 5 to 9, mixed suits
test_7 = "5h6d7s8c9dJc3h"

# 8. Flush: Hearts (5 cards of the same suit)
test_8 = "AhKhQh8h5h4d2s"

# 9. Straight Flush: 6 to 10 of spades
test_9 = "6s7s8s9s10s2d4c"

# 10. Royal Flush: Hearts
test_10 = "10hJhQhKhAh3d6s"

# 11. Three Pairs (will only count as Two Pair)
test_11 = "2h2d3c3d4s4h8c"

# 12. Mix of low cards and high cards, no obvious patterns
test_12 = "3h5d7s9cJdQc2s"

# 13. Four pairs with mixed ranks
test_13 = "5h5d6s6c7d7h8c8s"

# 14. Potential Full House and Four of a Kind
test_14 = "9h9d9s3c3s6d8h"

# 15. Full House (Aces over Jacks) with extra cards
test_15 = "AsAhAdJcJs2h4d5c"

# 16. Straight with Ace as low (Ace to Five)
test_16 = "Ah2d3s4c5h8s10d"

# 17. Flush with potential for a Straight Flush
test_17 = "2s4s6s8s10s3cJh"

# 18. High card, potential Two Pair or Three of a Kind
test_18 = "9h9dKsQc7s3c3h"

# 19. Three of a Kind with extra cards
test_19 = "5d5s5h7c6d4s2h"

# 20. Multiple combinations possible, including Straight, Flush, and Full House
test_20 = "4h5h6h7h8h9d3sAs"

    """Display the hacker-style banner for Balatro Advisor."""
    banner = """
██████╗  █████╗ ██╗      █████╗ ████████╗██████╗  ██████╗ 
██╔══██╗██╔══██╗██║     ██╔══██╗╚══██╔══╝██╔══██╗██╔═══██╗
██████╔╝███████║██║     ███████║   ██║   ██████╔╝██║   ██║
██╔══██ ██╔══██║██║     ██╔══██║   ██║   ██╔══██║██║   ██║
██████╔╝██║  ██║███████╗██║  ██║   ██║   ██║  ██║╚██████╔╝
╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ 
                      Balatro Advisor v1.0                                  
    """