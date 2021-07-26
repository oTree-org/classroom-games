from otree.api import *
from shared_out import get_or_none

doc = """
This is a standard 2-player trust game where the amount sent by player 1 gets
tripled. The trust game was first proposed by
<a href="http://econweb.ucsd.edu/~jandreon/Econ264/papers/Berg%20et%20al%20GEB%201995.pdf" target="_blank">
    Berg, Dickhaut, and McCabe (1995)
</a>.
"""


class Constants(BaseConstants):
    name_in_url = 'trust'
    players_per_group = 2
    num_rounds = 3
    instructions_template = 'trust/instructions.html'
    # Initial amount allocated to each player
    endowment = cu(100)
    multiplier = 3


class Subsession(BaseSubsession):
    pass


def vars_for_admin_report(subsession: Subsession):
    amounts_sent = [
        g.sent_amount
        for g in subsession.get_groups()
        if get_or_none(g, 'sent_amount') != None
    ]

    amounts_sent_back = [
        g.sent_back_amount
        for g in subsession.get_groups()
        if get_or_none(g, 'sent_back_amount') != None
    ]

    all_amounts = []

    for ss in subsession.in_all_rounds():
        groups = ss.get_groups()
        round_sent = [
            g.sent_amount for g in groups if get_or_none(g, 'sent_amount') != None
        ]

        round_sent_back = [
            g.sent_back_amount
            for g in groups
            if get_or_none(g, 'sent_back_amount') != None
        ]

        all_amounts.append(
            {'name': 'Round {} Sent'.format(ss.round_number), 'data': round_sent}
        )

        all_amounts.append(
            {
                'name': 'Round {} Sent Back'.format(ss.round_number),
                'data': round_sent_back,
            }
        )

        group_names = ['Group {}'.format(i) for i in range(1, len(ss.get_groups()) + 1)]

    if amounts_sent and amounts_sent_back:
        return dict(
            amount_exists=True,
            avg_sent=sum(amounts_sent) / len(amounts_sent),
            avg_sent_back=sum(amounts_sent_back) / len(amounts_sent_back),
            max_sent=max(amounts_sent),
            max_sent_back=max(amounts_sent_back),
            min_sent=min(amounts_sent),
            min_sent_back=min(amounts_sent_back),
            group_names=group_names,
            all_amounts=all_amounts,
        )
    else:
        return dict(
            amount_exists=False,
            avg_sent='(No Data)',
            avg_sent_back='(No Data)',
            max_sent='(No Data)',
            max_sent_back='(No Data)',
            min_sent='(No Data)',
            min_sent_back='(No Data)',
            group_names='No Data',
            all_amounts='No Data',
        )


class Group(BaseGroup):
    sent_amount = models.CurrencyField(
        min=0,
        max=Constants.endowment,
        doc="""Amount sent by P1""",
        label="Please enter an amount from 0 to 100:",
    )
    sent_back_amount = models.CurrencyField(doc="""Amount sent back by P2""", min=cu(0))


class Player(BasePlayer):
    pass


# FUNCTIONS
def sent_back_amount_max(group: Group):
    return group.sent_amount * Constants.multiplier


def set_payoffs(group: Group):
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)
    p1.payoff = Constants.endowment - group.sent_amount + group.sent_back_amount
    p2.payoff = group.sent_amount * Constants.multiplier - group.sent_back_amount


# PAGES
class Introduction(Page):
    pass


class Send(Page):
    """This page is only for P1
    P1 sends amount (all, some, or none) to P2
    This amount is tripled by experimenter,
    i.e if sent amount by P1 is 5, amount received by P2 is 15"""

    form_model = 'group'
    form_fields = ['sent_amount']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1


class SendBackWaitPage(WaitPage):
    pass


class SendBack(Page):
    """This page is only for P2
    P2 sends back some amount (of the tripled amount received) to P1"""

    form_model = 'group'
    form_fields = ['sent_back_amount']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        tripled_amount = group.sent_amount * Constants.multiplier
        return dict(tripled_amount=tripled_amount)


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    """This page displays the earnings of each player"""

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        return dict(tripled_amount=group.sent_amount * Constants.multiplier)


page_sequence = [
    Introduction,
    Send,
    SendBackWaitPage,
    SendBack,
    ResultsWaitPage,
    Results,
]
