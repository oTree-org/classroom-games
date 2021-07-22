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


class Subsession(BaseSubsession):
    pass


# returns color based on whether a player cooperated or defected
def get_column_chart_color(payoff):
    cooperated = Constants.betrayed_payoff # indicates blue color in highcharts
    defected = Constants.betray_payoff # indicates red color in highcharts
    color = ""
    if payoff == Constants.betrayed_payoff:
        color = cooperated
    elif payoff == Constants.both_defect_payoff:
        color = defected
    elif payoff == Constants.both_cooperate_payoff:
        color = cooperated
    elif payoff == Constants.betray_payoff:
        color = defected
    return color


def get_group_strategy(payoffs_for_this_group):
    p = payoffs_for_this_group
    strategy = ""
    if (p[0] == Constants.both_cooperate_payoff) & (p[1] == Constants.both_cooperate_payoff):
        strategy = "all_cooperated"
    elif (p[0] == Constants.betray_payoff) & (p[1] == Constants.betrayed_payoff):
        strategy = "both_cooperated_and_defected"
    elif (p[0] == Constants.betrayed_payoff) & (p[1] == Constants.betray_payoff):
        strategy = "both_cooperated_and_defected"
    elif (p[0] == Constants.both_defect_payoff) & (p[1] == Constants.both_defect_payoff):
        strategy = "all_defected"
    return strategy


def vars_for_admin_report(subsession: Subsession):
    group_names = ["Group " + str(g.id_in_subsession) for g in subsession.get_groups()]
    # todo id_in_subsession is wrong! fix later

    # create player data list
    player_data = []
    group_strategies = []
    for g in subsession.get_groups():
        i = 0
        payoffs_for_this_group = []
        for p in g.get_players():
            i = i + 1
            payoff = 0
            if get_or_none(p, 'payoff') == None:
                payoff = 0
            else:
                payoff = p.payoff

            player_data.append(
                dict(
                    name="Player " + str(p.id_in_group),
                    data=[dict(
                        y=payoff,
                        colorValue=get_column_chart_color(payoff)
                    )],
                    type='column',
                    colorKey='colorValue'
                )
            )

            # updated local group payoffs list with this group's payoff inorder to calculate the group strategy
            payoffs_for_this_group.append(payoff)

        group_strategies.append(get_group_strategy(payoffs_for_this_group))

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
    all_cooperated_percent = group_strategies.count("all_cooperated")/3*100
    all_defected_percent = group_strategies.count("all_defected")/3*100
    both_cooperated_and_defected_percent = group_strategies.count("both_cooperated_and_defected")/3*100

    pie_chart_data = [
        dict(
            name="All Cooperated",
            y=round(all_cooperated_percent),
            color="#00bfff"
        ),
        dict(
            name="All Defected",
            y=round(all_defected_percent),
            color="#ff4000"
        ),
        dict(
            name="Mix of Defection and Cooperation",
            y=round(both_cooperated_and_defected_percent),
            color="#800040"
        )
    ]

    nash_equilibrium_vector="(" + str(Constants.both_cooperate_payoff) + ", " + str(Constants.both_cooperate_payoff) + ")"
    optimal_equilibrium_vector="(" + str(Constants.both_defect_payoff) + ", " + str(Constants.both_defect_payoff) + ")"

    if payoff_all_players:
        return dict(
            avg_payoff=sum(payoff_all_players) / len(payoff_all_players),
            min_payoff=min(payoff_all_players),
            max_payoff=max(payoff_all_players),
            group_names=group_names,
            player_data_matched=player_data_matched,
            pie_chart_data=pie_chart_data,
            nash_equilibrium_vector=nash_equilibrium_vector,
            optimal_equilibrium_vector=optimal_equilibrium_vector
        )
    else:
        return dict(
            avg_upayoff='(no data)',
            min_payoff='(no data)',
            max_payoff='(no data)',
            group_names=group_names,
            player_data_matched=player_data_matched,
            pie_chart_data=pie_chart_data,
            nash_equilibrium_vector=nash_equilibrium_vector,
            optimal_equilibrium_vector=optimal_equilibrium_vector
        )


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    decision = models.StringField(
        choices=[['Cooperate', 'Cooperate'], ['Defect', 'Defect']],
        doc="""This player's decision""",
        widget=widgets.RadioSelect,
    )


# FUNCTIONS
def set_payoffs(group: Group):
    for p in group.get_players():
        set_payoff(p)


def other_player(player: Player):
    return player.get_others_in_group()[0]


def set_payoff(player: Player):
    payoff_matrix = dict(
        Cooperate=dict(
            Cooperate=Constants.both_cooperate_payoff, Defect=Constants.betrayed_payoff
        ),
        Defect=dict(
            Cooperate=Constants.betray_payoff, Defect=Constants.both_defect_payoff
        ),
    )
    player.payoff = payoff_matrix[player.decision][other_player(player).decision]


# PAGES
class Introduction(Page):
    timeout_seconds = 100


class Decision(Page):
    form_model = 'player'
    form_fields = ['decision']


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        me = player
        opponent = other_player(me)
        return dict(
            my_decision=me.decision,
            opponent_decision=opponent.decision,
            same_choice=me.decision == opponent.decision,
        )


page_sequence = [Introduction, Decision, ResultsWaitPage, Results]
