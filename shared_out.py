def set_players_per_group(subsession):
    session = subsession.session
    config = session.config
    ppg = config['players_per_group']

    players = subsession.get_players()
    matrix = [players[i : i + ppg] for i in range(0, len(players), ppg)]
    subsession.set_group_matrix(matrix)


def get_or_none(obj, fieldname):
    """This is needed because accessing a null field raises an error,
    but you often need to do that in admin_report because it can be clicked before
    players filled out a particular field."""
    try:
        return getattr(obj, fieldname)
    except TypeError:
        return None
