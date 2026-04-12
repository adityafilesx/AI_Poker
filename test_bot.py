from sarthak_bot import SarthakBot
from baseplayers import RaisePlayer, FoldPlayer
from game import PokerGame, GamePhase

def main():
    print('Testing SarthakBot...')
    p1 = SarthakBot('SarthakAI', 1000)
    p2 = RaisePlayer('Raiser', 1000)
    p3 = FoldPlayer('Folder', 1000)
    
    game = PokerGame([p1, p2, p3], big_blind=20)
    for _ in range(5):
        print(f'\nHand {game.hand_number + 1}')
        game_status = game.start_new_hand()
        if not game_status:
            break
        while game.phase != GamePhase.SHOWDOWN:
            player = game.players[game.active_player_index]
            if game.num_active_players() == 1 and player.bet_amount == game.current_bet:
                game.advance_game_phase()
                continue
            try:
                is_successful = game.get_player_input()
            except Exception as e:
                print(f'Exception: {e}')
                from player import PlayerAction
                game.player_action(PlayerAction.FOLD, 0)
                break
            if not is_successful:
                break
    print('Test complete.')

if __name__ == '__main__':
    main()
