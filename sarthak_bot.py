from player import Player, PlayerAction
from card import Card, Suit, Rank
from bot_rules import evaluate_rules
import joblib
import os
import pandas as pd

class SarthakBot(Player):
    def __init__(self, name, stack):
        super().__init__(name, stack)
        self.ml_model = None
        if os.path.exists("poker_ml_model.pkl"):
            try:
                self.ml_model = joblib.load("poker_ml_model.pkl")
            except Exception as e:
                print("Could not load ML model:", e)

    def action(self, game_state: list[int], action_history: list):
        # Decode state
        hc1_idx = game_state[0]
        hc2_idx = game_state[1]
        
        hc1_suit = Suit((hc1_idx - 1) // 13)
        hc1_rank = Rank(((hc1_idx - 1) % 13) + 2)
        hc2_suit = Suit((hc2_idx - 1) // 13)
        hc2_rank = Rank(((hc2_idx - 1) % 13) + 2)
        
        hc1 = Card(hc1_rank, hc1_suit)
        hc2 = Card(hc2_rank, hc2_suit)
        hole_cards = [hc1, hc2]
        
        c_cards = []
        for i in range(2, 7):
            idx = game_state[i]
            if idx != 0:
                s = Suit((idx - 1) // 13)
                r = Rank(((idx - 1) % 13) + 2)
                c_cards.append(Card(r, s))
                
        pot = game_state[7]
        current_raise = game_state[8]
        blind = game_state[9]
        active_idx = game_state[10]
        num_players = game_state[11]
        
        # Win Probability Prediction
        win_prob = 0.5
        if self.ml_model:
            p_ranks = sorted([hc1.rank.value, hc2.rank.value])
            is_suited = 1 if hc1.suit == hc2.suit else 0
            
            c_ranks = sorted([c.rank.value for c in c_cards], reverse=True)
            while len(c_ranks) < 5:
                c_ranks.append(0)
                
            features = {
                'hc1': p_ranks[1], 'hc2': p_ranks[0], 'suited': is_suited,
                'c1': c_ranks[0], 'c2': c_ranks[1], 'c3': c_ranks[2], 'c4': c_ranks[3], 'c5': c_ranks[4]
            }
            try:
                X = pd.DataFrame([features]).values
                win_prob = self.ml_model.predict_proba(X)[0][1]
            except Exception as e:
                pass
                
        # Evaluate 12-rules
        base_action, base_amount = evaluate_rules(hole_cards, c_cards, current_raise, self.stack)
        
        # ML + Rule Integration
        opp_aggression = sum(1 for a in action_history if a[2] in ['raise', 'all-in'])
        
        if win_prob > 0.70:
            if base_action in ['fold', 'call']:
                base_action = 'raise'
                base_amount = max(current_raise * 2, 20)
        elif win_prob < 0.35 and opp_aggression > 2:
            if base_action == 'raise' and base_amount < 20: 
                base_action = 'fold'
                base_amount = 0
                
        if base_action == 'fold':
            return PlayerAction.FOLD, 0
            
        call_amount = current_raise - self.bet_amount
        
        if base_action == 'call':
            if call_amount >= self.stack:
                return PlayerAction.ALL_IN, self.stack
            return PlayerAction.CALL, call_amount
            
        if base_action == 'raise':
            amount = max(base_amount, current_raise + blind)
            if amount >= self.stack:
                return PlayerAction.ALL_IN, self.stack
            return PlayerAction.RAISE, amount
            
        if base_action == 'all':
            return PlayerAction.ALL_IN, self.stack
            
        return PlayerAction.FOLD, 0
