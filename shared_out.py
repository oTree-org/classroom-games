def set_players_per_group(subsession):
    session = subsession.session
    config = session.config
    ppg = config['players_per_group']

    players = subsession.get_players()
    matrix = [players[i : i + ppg] for i in range(0, len(players), ppg)]
    subsession.set_group_matrix(matrix)
