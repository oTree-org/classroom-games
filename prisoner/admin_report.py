from shared_out import get_or_none

COLOR_RED_DEFECT = "#ff4000"
COLOR_BLUE_COOPERATE = "#00bfff"
COLOR_MAROON_MIX = "#800040"


def vars_for_admin_report_prisoner(subsession, constants):
    group_names = []

    # create player data list
    player_data = []
    group_strategies = []
    for g in subsession.get_groups():
        group_names.append("Group {}".format(g.id_in_subsession))
        players = g.get_players()
        num_cooperated = 0
        if any(get_or_none(p, 'cooperated') is None for p in players):
            continue
        for p in players:
            # color is a numeric value sent to highcharts colorAxis. The lower value (0) is set to blue, while the
            # higher value (300) will result in red
            color = {True: constants.betrayed_payoff, False: constants.betray_payoff}[p.cooperated]
            player_data.append(
                dict(
                    name="Player {}".format(p.id_in_group),
                    data=[dict(y=p.payoff, colorValue=color)],
                    type='column',
                    colorKey='colorValue',
                )
            )

            # updated local group payoffs list with this group's payoff inorder to calculate the group strategy
            num_cooperated += p.cooperated

        group_strategies.append(num_cooperated)

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

    payoff_all_players = [p.payoff for p in subsession.get_players()]

    num_groups = len(group_strategies)
    # build pie chart data - could be extracted into function!
    both_cooperated_percent = group_strategies.count(2) / num_groups * 100
    both_defected_percent = group_strategies.count(0) / num_groups * 100
    mixed_outcome_percent = group_strategies.count(1) / num_groups * 100

    pie_chart_data = [
        dict(
            name="Groups where both players cooperated",
            y=round(both_cooperated_percent),
            color=COLOR_BLUE_COOPERATE,
        ),
        dict(
            name="Groups where both players defected",
            y=round(both_defected_percent),
            color=COLOR_RED_DEFECT,
        ),
        dict(
            name="Groups where one player defected and the other cooperated",
            y=round(mixed_outcome_percent),
            color=COLOR_MAROON_MIX,
        ),
    ]

    context = dict(
        group_names=group_names,
        player_data_matched=player_data_matched,
        pie_chart_data=pie_chart_data,
    )
    if payoff_all_players:
        context.update(
            avg_payoff=sum(payoff_all_players) / len(payoff_all_players),
            min_payoff=min(payoff_all_players),
            max_payoff=max(payoff_all_players),
        )
        return context
    else:
        context.update(
            avg_payoff='(no data)', min_payoff='(no data)', max_payoff='(no data)'
        )
        return context
