from otree.api import *

doc = """
This is a standard 2-player ultimatum game where the amount sent by player 1 gets
tripled. The game was first proposed by
<a href="http://econweb.ucsd.edu/~jandreon/Econ264/papers/Berg%20et%20al%20GEB%201995.pdf" target="_blank">
    Berg, Dickhaut, and McCabe (1995)
</a>.
"""


class Constants(BaseConstants):
    name_in_url = 'ultimatum'
    players_per_group = 2
    num_rounds = 3
    instructions_template = 'ultimatum/instructions.html'
    # Initial amount allocated to each player
    endowment = cu(100)
    reject_payoff = cu(0)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    offer = models.CurrencyField(
        min=0,
        max=Constants.endowment,
        doc="""Offer by Player A""",
        label="Please enter an offer amount between 0 to 100:",
    )
    offer_accepted = models.BooleanField(
        choices=[
            [True, 'Accept'],
            [False, 'Reject'],
        ],
        label="Do you accept or reject Participant A's offer?",
        doc="""Whether Participant A's offer has been accepted by B"""
    )


class Player(BasePlayer):
    pass


# FUNCTIONS

def set_payoffs(group: Group):
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)

    if group.offer_accepted:
        p1.payoff = Constants.endowment - group.offer
        p2.payoff = group.offer

    else:
        p1.payoff = Constants.reject_payoff
        p2.payoff = Constants.reject_payoff

# PAGES
class Introduction(Page):
    pass


class Offer(Page):
    """This page is only for Player A
    P1 sends offer (all, some, or none) to P2
    """

    form_model = 'group'
    form_fields = ['offer']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1


class OfferWaitPage(WaitPage):
    pass


class AcceptOrReject(Page):
    """This page is only for Player B
    B chooses to accept or reject the offer made by A"""

    form_model = 'group'
    form_fields = ['offer_accepted']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        return dict(offer=group.offer)


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    """This page displays the earnings of each player"""

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        return dict(offer=group.offer,
                    offer_accepted=group.offer_accepted)


page_sequence = [
    Introduction,
    Offer,
    OfferWaitPage,
    AcceptOrReject,
    ResultsWaitPage,
    Results,
]
