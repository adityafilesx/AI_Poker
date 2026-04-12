import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
from card import Deck, Card
from hand_evaluator import HandEvaluator, HandRank

def generate_data(num_samples=10000):
    data = []
    
    for _ in range(num_samples):
        deck = Deck()
        
        # Player 1 (Our bot's cards)
        player_hole = deck.deal(2)
        
        # Player 2 (Opponent's cards)
        opp_hole = deck.deal(2)
        
        # Community cards
        community = deck.deal(5)
        
        # Evaluate hand
        p1_result = HandEvaluator.evaluate_hand(player_hole, community)
        p2_result = HandEvaluator.evaluate_hand(opp_hole, community)
        
        # 1 if we win, 0 otherwise
        if p1_result.hand_rank.value > p2_result.hand_rank.value:
            win = 1
        elif p1_result.hand_rank.value == p2_result.hand_rank.value:
            if p1_result.hand_value > p2_result.hand_value:
                win = 1
            else:
                win = 0
        else:
            win = 0
            
        # Features
        p_ranks = sorted([player_hole[0].rank.value, player_hole[1].rank.value])
        is_suited = 1 if player_hole[0].suit == player_hole[1].suit else 0
        c_ranks = sorted([c.rank.value for c in community])
        
        # Generate samples for different phases
        # Phase 1: Pre-flop
        data.append(({
            'hc1': p_ranks[1], 'hc2': p_ranks[0], 'suited': is_suited,
            'c1': 0, 'c2': 0, 'c3': 0, 'c4': 0, 'c5': 0
        }, win))
        
        # Phase 2: Flop
        data.append(({
            'hc1': p_ranks[1], 'hc2': p_ranks[0], 'suited': is_suited,
            'c1': c_ranks[4], 'c2': c_ranks[3], 'c3': c_ranks[2], 'c4': 0, 'c5': 0
        }, win))
        
        # Phase 3: Turn
        data.append(({
            'hc1': p_ranks[1], 'hc2': p_ranks[0], 'suited': is_suited,
            'c1': c_ranks[4], 'c2': c_ranks[3], 'c3': c_ranks[2], 'c4': c_ranks[1], 'c5': 0
        }, win))
        
        # Phase 4: River
        data.append(({
            'hc1': p_ranks[1], 'hc2': p_ranks[0], 'suited': is_suited,
            'c1': c_ranks[4], 'c2': c_ranks[3], 'c3': c_ranks[2], 'c4': c_ranks[1], 'c5': c_ranks[0]
        }, win))
        
    return data

def train_model():
    print("Generating synthetic poker dataset...")
    raw_data = generate_data(10000)
    
    df = pd.DataFrame([d[0] for d in raw_data])
    y = np.array([d[1] for d in raw_data])
    
    X = df.values
    
    print("Training models based on Hand features...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)
    rf.fit(X_train, y_train)
    rf_acc = rf.score(X_test, y_test)
    
    # XGBoost
    import xgboost as xgb
    xg = xgb.XGBClassifier(n_estimators=100, max_depth=8, learning_rate=0.1, random_state=42)
    xg.fit(X_train, y_train)
    xg_acc = xg.score(X_test, y_test)
    
    print(f"Random Forest Validation Accuracy: {rf_acc:.4f}")
    print(f"XGBoost Validation Accuracy: {xg_acc:.4f}")
    print("(Note: Poker is highly stochastic)")
    with open('benchmarks.txt', 'w') as f:
        f.write(f'RF: {rf_acc:.4f}, XGB: {xg_acc:.4f}')
    
    if xg_acc > rf_acc:
        print("XGBoost performed better. Saving XGBoost model...")
        joblib.dump(xg, 'poker_ml_model.pkl')
    else:
        print("Random Forest performed better. Saving RF model...")
        joblib.dump(rf, 'poker_ml_model.pkl')
    print("Saved successfully to poker_ml_model.pkl.")

if __name__ == '__main__':
    train_model()
