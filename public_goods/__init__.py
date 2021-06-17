from otree.api import *

from shared_out import set_players_per_group, get_or_none

doc = """
This is a one-period public goods game with 3 players.
"""


class Constants(BaseConstants):
    name_in_url = 'public_goods'
    players_per_group = None
    num_rounds = 3
    instructions_template = 'public_goods/instructions.html'
    # """Amount allocated to each player"""


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    set_players_per_group(subsession)


def vars_for_admin_report(subsession: Subsession):
    contributions = [
        p.contribution
        for p in subsession.get_players()
        if get_or_none(p, 'contribution') != None
    ]

    contributions_dict = {}
    for ss in subsession.in_all_rounds():
        round_contributions = [p.contribution for p in ss.get_players() if get_or_none(p, 'contribution') != None]
        contributions_dict[ss.round_number] = round_contributions

    contributions_stats = {}
    if contributions:
        for key in contributions_dict.keys():
            li = contributions_dict[key]
            contributions_stats[key] = [max(li), min(li), (sum(li)/len(li))]

    if contributions:
        return dict(
            avg_contribution=sum(contributions) / len(contributions),
            min_contribution=min(contributions),
            max_contribution=max(contributions),
            contributions_stats=contributions_stats
        )
    else:
        return dict(
            avg_contribution='(no data)',
            min_contribution='(no data)',
            max_contribution='(no data)',
            contributions_stats=contributions_stats
        )


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()


class Player(BasePlayer):
    contribution = models.CurrencyField(
        min=0,
        doc="""The amount contributed by the player""",
        label="How much will you contribute to the project (from 0 to 100)?",
    )


def contribution_max(player: Player):
    session = player.session
    config = session.config

    return config['endowment']


def set_payoffs(group: Group):
    session = group.session
    config = session.config

    group.total_contribution = sum([p.contribution for p in group.get_players()])
    group.individual_share = (
        group.total_contribution * config['multiplier'] / config['players_per_group']
    )
    for p in group.get_players():
        p.payoff = (config['endowment'] - p.contribution) + group.individual_share


class Introduction(Page):
    pass


class Contribute(Page):

    form_model = 'player'
    form_fields = ['contribution']


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs
    body_text = "Waiting for other participants to contribute."


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        session = group.session

        return dict(
            total_earnings=group.total_contribution * session.config['multiplier']
        )


page_sequence = [Introduction, Contribute, ResultsWaitPage, Results]