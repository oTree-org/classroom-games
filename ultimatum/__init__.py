from otree.api import *
from shared_out import get_or_none

doc = """
This is a standard 2-player Ultimatum Game where the offer by Player 1 gets
accepted or rejected by Player 2. If the offer is rejected, both players get no payoff. The game was first proposed by
<a href="https://journals-sagepub-com.proxyiub.uits.iu.edu/doi/pdf/10.1177/002200276100500205" target="_blank">
    Harsanyi, John C. (1961)
</a>.
"""


class Constants(BaseConstants):
    name_in_url = 'ultimatum'
    players_per_group = 2
    num_rounds = 3
    instructions_template = 'ultimatum/instructions.html'
    # Initial amount allocated to each player
    endowment = cu(100)
    # Payoff to both players in case offer is rejected, generally taken to be zero
    reject_payoff = cu(0)


class Subsession(BaseSubsession):
    pass


def vars_for_admin_report(subsession: Subsession):
    offers = [
        g.offer for g in subsession.get_groups() if get_or_none(g, 'offer') != None
    ]

    offer_acceptance = [
        g.offer_accepted
        for g in subsession.get_groups()
        if get_or_none(g, 'offer_accepted') != None
    ]

    # creating two separate visualisations for accepted and rejected offers
    # with groups and rounds depicted on the X-axis and the size of the offers
    # y-axis
    accepted_offers = []
    rejected_offers = []

    if offers and offer_acceptance:
        for ss in subsession.in_all_rounds():
            groups = ss.get_groups()
            round_accepted = []
            round_rejected = []
            for group in groups:
                if group.offer_accepted:
                    round_accepted.append(group.offer)
                    round_rejected.append(None)
                else:
                    round_accepted.append(None)
                    round_rejected.append(group.offer)
            accepted_offers.append(
                {'name': 'Round {}'.format(ss.round_number), 'data': round_accepted}
            )
            rejected_offers.append(
                {'name': 'Round {}'.format(ss.round_number), 'data': round_rejected}
            )

        group_names = ['Group {}'.format(i) for i in range(1, len(ss.get_groups()) + 1)]

        return dict(
            offer_exists=True,
            avg_offer=sum(offers) / len(offers),
            max_offer=max(offers),
            min_offer=min(offers),
            offer_acceptance_rate='{}%'.format(
                round((sum(offer_acceptance) / len(offer_acceptance)) * 100, 2)
            ),
            group_names=group_names,
            accepted_offers=accepted_offers,
            rejected_offers=rejected_offers,
        )
    else:
        return dict(
            offer_exists=False,
            avg_offer='(No Data)',
            max_offer='(No Data)',
            min_offer='(No Data)',
            offer_acceptance_rate='(No Data)',
            group_names='(No Data)',
            accepted_offers='(No Data)',
            rejected_offers='(No Data)',
        )


class Group(BaseGroup):
    offer = models.CurrencyField(
        min=0,
        max=Constants.endowment,
        doc="""Offer by Player A""",
        label="Please enter an offer amount between 0 to 100:",
    )
    offer_accepted = models.BooleanField(
        choices=[[True, 'Accept'], [False, 'Reject'],],
        label="Do you accept or reject Participant A's offer?",
        doc="""Whether Participant A's offer has been accepted by B""",
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

        return dict(offer=group.offer, offer_accepted=group.offer_accepted)


page_sequence = [
    Introduction,
    Offer,
    OfferWaitPage,
    AcceptOrReject,
    ResultsWaitPage,
    Results,
]
