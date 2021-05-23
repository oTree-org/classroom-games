from otree.api import *
from shared_out import *

doc = """
Monty Hall problem
"""


class Constants(BaseConstants):
    name_in_url = 'monty_hall'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    door_first_chosen = models.IntegerField(choices=[1, 2, 3])
    door_opened = models.IntegerField()
    door_not_opened = models.IntegerField()
    door_finally_chosen = models.IntegerField()
    door_with_prize = models.IntegerField()
    is_winner = models.BooleanField()


def door_finally_chosen_choices(player: Player):
    return [player.door_first_chosen, player.door_not_opened]


class Decide1(Page):
    form_model = 'player'
    form_fields = ['door_first_chosen']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        import random

        player.door_with_prize = random.choice([1, 2, 3])
        remaining_doors = [1, 2, 3]
        remaining_doors.remove(player.door_first_chosen)
        if player.door_with_prize == player.door_first_chosen:
            random.shuffle(remaining_doors)
            [player.door_opened, player.door_not_opened] = remaining_doors
        else:
            player.door_not_opened = player.door_with_prize
            remaining_doors.remove(player.door_not_opened)
            [player.door_opened] = remaining_doors


class Decide2(Page):
    form_model = 'player'
    form_fields = ['door_finally_chosen']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.is_winner = player.door_finally_chosen == player.door_with_prize


class Results(Page):
    pass


page_sequence = [Decide1, Decide2, Results]
