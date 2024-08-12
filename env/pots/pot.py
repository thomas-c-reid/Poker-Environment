from env.enums import actionNameEnum

class Pot:
    '''
    Class to keep track of current players in a certain pot
    Args:
        potValue: (int) current value in the pot
        isActive: (bool) keep track of if the pot is actively getting added to
        players_in_pot: (list) the players that are in with contention of winning money within a certain pot
        currentBet: (int) the amount being bet at this current stage of betting in the round
        winner: (list) list of people who won each pot and get a share of the total money
        allInValueToMatch: (int) the value that a user would have to bet on a certain round to close the pot
        allInFlag: (bool) whether the has been an all in action added to this pot (once all all-in bets have been matched, pot gets closed)
    '''
    pot_value: int
    players_in_pot: list
    winners: list = []
    current_bet: int
    round_index: int

    def __init__(self, pot_value: int = 0, players_in_pot: list = [], round_index: int = None):
        self.pot_value = pot_value
        self.winners = []
        self.current_bet = pot_value
        self.round_index = round_index
        if len(players_in_pot) > 0:
            self.players_in_pot = players_in_pot
            
    def add_to_pot(self, amount: int):
        self.pot_value += amount
            
    def remove_player(self, player_id: str):
        if player_id in self.players_in_pot:
            self.players_in_pot.remove(player_id)

    def next_round(self):
        self.current_bet = 0
        
    def __str__(self):
        return f'pot_value: {self.pot_value}, players_in_pot: {self.players_in_pot}, current_bet: {self.current_bet}'
