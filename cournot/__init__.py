from otree.api import *

from shared_out import get_or_none

doc = """
In Cournot competition, firms simultaneously decide the units of products to
manufacture. The unit selling price depends on the total units produced. In
this implementation, there are 2 firms competing for 1 period.
"""


class Constants(BaseConstants):
    name_in_url = 'cournot'
    players_per_group = 2
    num_rounds = 1
    instructions_template = 'cournot/instructions.html'
    # Total production capacity of all players
    total_capacity = 60
    max_units_per_player = int(total_capacity / players_per_group)


class Subsession(BaseSubsession):
    pass


def vars_for_admin_report(subsession: Subsession):
    group_names = ["Group " + str(g.id_in_subsession) for g in subsession.get_groups()]

    # create player data list
    player_data = []
    for g in subsession.get_groups():
        i = 0
        for p in g.get_players():
            i = i + 1
            units = 0
            if get_or_none(p, 'units') == None:
                units = 0
            else:
                units = p.units
            player_data.append(
                dict(
                    # player_position="Player "+ str(i), # this is only needed if the players
                    # dont have similar ids in the different groups
                    name="Player " + str(p.id_in_group),
                    data=[units]
                )
            )

    # todo
    # sort from least total units per group to highest on graph - this not possible/complicated with highcharts
    # use table to show optimal outcome (put table on top) - try "color by value in excel "

    # match players in player data by index so that; the "first" player in each group
    # has units assigned for each highcharts series - design limitation by highcharts
    player_data_matched = {}
    for player in player_data:
        name = player['name']
        if name in player_data_matched.keys():
            player_data_matched[name]['data'].append(player['data'][0])
        else:
            player_data_matched[name] = player

    # convert the values to a list
    player_data_matched = list(player_data_matched.values())

    lowest_payoff_best_response_function = [
        g.lowest_payoff_best_response_function
        for g in subsession.get_groups()
        if get_or_none(g, 'lowest_payoff_best_response_function') != None
    ]

    # add brf units to player_data_matched list
    player_data_matched.append(dict(
        name='Best response function units for player with least payoff',
        color='#00FF00',
        data=lowest_payoff_best_response_function
    ))

    units_all_players = [
        p.units for p in subsession.get_players()
        if get_or_none(p, 'units') != None
    ]

    nash_equilibrium=(Constants.total_capacity/3) * Constants.players_per_group

    context = dict(
        group_names=group_names,
        player_data_matched=player_data_matched,
        nash_equilibrium=nash_equilibrium
    )
    if units_all_players:
        context.update(
            avg_units=sum(units_all_players) / len(units_all_players),
            min_units=min(units_all_players),
            max_units=max(units_all_players)
        )
        return context
    else:
        context.update(
            avg_units='(no data)',
            min_units='(no data)',
            max_units='(no data)'
        )
        return context


class Group(BaseGroup):
    unit_price = models.CurrencyField()
    total_units = models.IntegerField(doc="""Total units produced by all players""")
    name = models.StringField()
    player_with_lowest_payoff = models.StringField()
    lowest_payoff_best_response_function = models.FloatField(
        doc="""Highest number of units for lowest payoff player"""
    )


class Player(BasePlayer):
    units = models.IntegerField(
        min=0,
        max=Constants.max_units_per_player,
        doc="""Quantity of units to produce""",
        label="How many units will you produce (from 0 to 30)?",
    )


# FUNCTIONS
def set_payoffs(group: Group):
    players = group.get_players()
    group.total_units = sum([p.units for p in players])
    group.unit_price = Constants.total_capacity - group.total_units

    lower_payoff = min([p.units for p in players])
    group.player_with_lowest_payoff = "Player " + str(
        next((p.id_in_group for p in players if p.units == lower_payoff), None)
    ) # currently not in use but could come in handy
    group.lowest_payoff_best_response_function = (Constants.total_capacity - lower_payoff)/2
    for p in players:
        p.payoff = group.unit_price * p.units


def other_player(player: Player):
    return player.get_others_in_group()[0]


# PAGES
class Introduction(Page):
    pass


class Decide(Page):
    form_model = 'player'
    form_fields = ['units']


class ResultsWaitPage(WaitPage):
    body_text = "Waiting for the other participant to decide."
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(other_player_units=other_player(player).units)


page_sequence = [Introduction, Decide, ResultsWaitPage, Results]
