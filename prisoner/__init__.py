from otree.api import *

from shared_out import get_or_none

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


# returns color based on whether a player cooperated or defected
def get_column_chart_color(cooperated):
    cooperated_color = Constants.betrayed_payoff  # numeric value of betrayed_payoff indicates blue color in highcharts
    defected_color = Constants.betray_payoff  # numeric value of betray_payoff indicates red color in highcharts
    if cooperated:
        return cooperated_color
    else:
        return defected_color


def get_group_strategy(sum_of_cooperations_in_group):
    strategy = ""
    if sum_of_cooperations_in_group == 0:
        strategy = "all_defected"
    elif sum_of_cooperations_in_group == 1:
        strategy = "both_cooperated_and_defected"
    elif sum_of_cooperations_in_group == 2:
        strategy = "all_cooperated"
    return strategy


def vars_for_admin_report(subsession: Subsession):
    group_names = ["Group " + str(g.id_in_subsession) for g in subsession.get_groups()]

    # create player data list
    player_data = []
    group_strategies = []
    for g in subsession.get_groups():
        cooperated_decision_for_group = []
        for p in g.get_players():
            player_data.append(
                dict(
                    name="Player " + str(p.id_in_group),
                    data=[dict(
                        y=p.payoff,
                        colorValue=get_column_chart_color(p.cooperated)
                    )],
                    type='column',
                    colorKey='colorValue'
                )
            )

            # updated local group payoffs list with this group's payoff inorder to calculate the group strategy
            cooperated_decision_for_group.append(p.cooperated)

        group_strategies.append(get_group_strategy(sum(cooperated_decision_for_group)))

    # match players in player data by index so that; the "first" player in each group
    # has payoff assigned for each highcharts series - design limitation by highcharts
    player_data_matched = {}
    for player in player_data:
        name = player['name']
        if name in player_data_matched.keys():
            player_data_matched[name]['data'].append(player['data'][0])
        else:
            player_data_matched[name] = player

    # convert the values to a list
    player_data_matched = list(player_data_matched.values())

    payoff_all_players = [
        p.payoff for p in subsession.get_players()
        if get_or_none(p, 'payoff') != None
    ]

    # build pie chart data - could be extracted into function!
    all_cooperated_percent = group_strategies.count("all_cooperated") / len(group_strategies) * 100
    all_defected_percent = group_strategies.count("all_defected") / len(group_strategies) * 100
    both_cooperated_and_defected_percent = group_strategies.count("both_cooperated_and_defected") / len(
        group_strategies) * 100

    pie_chart_data = [
        dict(
            name="Groups where both players cooperated",
            y=round(all_cooperated_percent),
            color=Constants.color_blue_cooperate
        ),
        dict(
            name="Groups where both players defected",
            y=round(all_defected_percent),
            color=Constants.color_red_defect
        ),
        dict(
            name="Groups where both players has a mix of defection and cooperation",
            y=round(both_cooperated_and_defected_percent),
            color=Constants.color_maroon_mix
        )
    ]

    nash_equilibrium_vector = "( {x}, {y} )".format(x=Constants.both_cooperate_payoff,
                                                    y=Constants.both_cooperate_payoff)
    optimal_equilibrium_vector = "( {x}, {y} )".format(x=Constants.both_defect_payoff, y=Constants.both_defect_payoff)

    context = dict(
        group_names=group_names,
        player_data_matched=player_data_matched,
        pie_chart_data=pie_chart_data,
        nash_equilibrium_vector=nash_equilibrium_vector,
        optimal_equilibrium_vector=optimal_equilibrium_vector
    )
    if payoff_all_players:
        context.update(
            avg_payoff=sum(payoff_all_players) / len(payoff_all_players),
            min_payoff=min(payoff_all_players),
            max_payoff=max(payoff_all_players)
        )
        return context
    else:
        context.update(
            avg_upayoff='(no data)',
            min_payoff='(no data)',
            max_payoff='(no data)'
        )
        return context


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
