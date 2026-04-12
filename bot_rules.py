from card import Rank, Suit

def evaluate_rules(hole_cards, community_cards, current_raise, stack):
    """
    Evaluates Sarthak's 12 rules map.
    Returns: action_type, target_amount
    """
    if len(hole_cards) != 2:
        return 'fold', 0
        
    c1, c2 = hole_cards
    p_ranks = [c1.rank.value, c2.rank.value]
    p_suits = [c1.suit.value, c2.suit.value]
    
    c_ranks = [c.rank.value for c in community_cards]
    c_suits = [c.suit.value for c in community_cards]
    
    all_ranks = p_ranks + c_ranks
    all_suits = p_suits + c_suits
    
    high_card_values = [14, 13, 12, 11, 10]
    
    # 1. Royal flush approx check (Q,K,10 etc 5 same suit) -> Raise All
    if any(r in high_card_values for r in p_ranks):
        for s in set(all_suits):
            suit_ranks = [all_ranks[i] for i in range(len(all_ranks)) if all_suits[i] == s]
            if all(v in suit_ranks for v in high_card_values):
                return 'all', stack
                
    is_suited = (c1.suit == c2.suit)
    is_consec = (abs(c1.rank.value - c2.rank.value) in [1, 2])
    is_pair = (c1.rank.value == c2.rank.value)
    
    pair_match_count = sum(1 for cr in c_ranks if cr in p_ranks)
    suit_match_count = sum(1 for cs in c_suits if (cs == c1.suit.value or cs == c2.suit.value))
    
    # Evaluate Sarthak's Rules conceptually
    
    # 3. Two cards same num, 3/4 of a kind check
    if is_pair and pair_match_count >= 1:
        # Rule 3 approx
        if len(c_ranks) >= 3:
            return 'raise', 45
        
    # 4. Another pair
    if is_pair and pair_match_count > 1:
        return 'raise', 25
        
    # 5. Same suit, check if 3 cards same suit in community -> Flush draw
    if is_suited and suit_match_count >= 3:
        return 'raise', 20
        
    # 6. Consecutive, check if 3 cards in range
    if is_consec:
        in_range_count = sum(1 for r in c_ranks if min(p_ranks)-2 <= r <= max(p_ranks)+2)
        if in_range_count >= 3:
            return 'raise', 15
            
    # 7. Pair, matched at least 1 in comm
    if is_pair and pair_match_count == 1:
        return 'raise', 8
        
    # 9. Just a pair
    if is_pair:
        return 'raise', 4
        
    # 10. High cards with no matches
    if any(r in [14, 13, 12] for r in p_ranks) and len(community_cards) > 0 and pair_match_count == 0:
        return 'raise', 2
        
    # 11. Small numbers -> fold
    if all(r < 10 for r in p_ranks) and len(community_cards) >= 3 and pair_match_count == 0:
        return 'fold', 0
        
    # 12. Else call or fold
    if current_raise > stack * 0.1 and not is_pair and not is_suited:
        return 'fold', 0
        
    return 'call', 0
