from shared_out import get_or_none


def get_column_chart_color(cooperated, constants):
    cooperated_color = constants.betrayed_payoff  # numeric value of betrayed_payoff indicates blue color in highcharts
    defected_color = constants.betray_payoff  # numeric value of betray_payoff indicates red color in highcharts
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


def vars_for_admin_report_prisoner(subsession, constants):
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
                        colorValue=get_column_chart_color(p.cooperated, constants)
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
            color=constants.color_blue_cooperate
        ),
        dict(
            name="Groups where both players defected",
            y=round(all_defected_percent),
            color=constants.color_red_defect
        ),
        dict(
            name="Groups where both players has a mix of defection and cooperation",
            y=round(both_cooperated_and_defected_percent),
            color=constants.color_maroon_mix
        )
    ]

    nash_equilibrium_vector = "( {x}, {y} )".format(
        x=constants.both_cooperate_payoff, y=constants.both_cooperate_payoff
    )
    optimal_equilibrium_vector = "( {x}, {y} )".format(
        x=constants.both_defect_payoff, y=constants.both_defect_payoff
    )

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
