from otree.api import *

from .admin_report import vars_for_admin_report_prisoner

doc = """
This is a one-shot "Prisoner's Dilemma". Two players are asked separately
whether they want to cooperate or defect. Their choices directly determine the
payoffs.
"""


class Constants(BaseConstants):
    name_in_url = 'prisoner'
    players_per_group = 2
    num_rounds = 1
    instructions_template = 'prisoner/instructions.html'
    # payoff if 1 player defects and the other cooperates""",
    betray_payoff = cu(300)
    betrayed_payoff = cu(0)
    # payoff if both players cooperate or both defect
    both_cooperate_payoff = cu(200)
    both_defect_payoff = cu(100)

    color_red_defect = "#ff4000"
    color_blue_cooperate = "#00bfff"
    color_maroon_mix = "#800040"


class Subsession(BaseSubsession):
    pass


def vars_for_admin_report(subsession: Subsession):
    return vars_for_admin_report_prisoner(subsession, Constants)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    cooperated = models.BooleanField()


# FUNCTIONS
def set_payoffs(group: Group):
    for p in group.get_players():
        set_payoff(p)


def other_player(player: Player):
    return player.get_others_in_group()[0]


def set_payoff(player: Player):
    # true represents "cooperated", false represents "defected"
    payoff_matrix = dict(
        true=dict(
            true=Constants.both_cooperate_payoff, false=Constants.betrayed_payoff
        ),
        false=dict(
            true=Constants.betray_payoff, false=Constants.both_defect_payoff
        ),
    )

    player.payoff = payoff_matrix[str(player.cooperated).lower()][str(other_player(player).cooperated).lower()]


def get_decision(cooperated):
    if cooperated:
        return "Cooperate"
    else:
        return "Defect"


# PAGES
class Introduction(Page):
    timeout_seconds = 100


class Decision(Page):
    form_model = 'player'
    form_fields = ['cooperated']


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        me = player
        opponent = other_player(me)
        return dict(
            my_decision=get_decision(me.cooperated),
            opponent_decision=get_decision(opponent.cooperated),
            same_choice=me.cooperated == opponent.cooperated,
        )


page_sequence = [Introduction, Decision, ResultsWaitPage, Results]
