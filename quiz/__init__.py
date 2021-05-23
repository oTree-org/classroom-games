from otree.api import *
from shared_out import *

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'quiz'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    for p in subsession.get_players():
        stimuli = read_csv()
        p.num_trials = len(stimuli)
        for stim in stimuli:
            Trial.create(player=p, **stim)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    num_completed = models.IntegerField(initial=0)
    num_correct = models.IntegerField(initial=0)
    num_trials = models.IntegerField()


def get_current_trial(player: Player):
    return Trial.filter(player=player, choice=None)[0]


def is_finished(player: Player):
    return player.num_completed == player.num_trials


class Trial(ExtraModel):
    player = models.Link(Player)
    question = models.StringField()
    optionA = models.StringField()
    optionB = models.StringField()
    optionC = models.StringField()
    solution = models.StringField()
    choice = models.StringField()
    is_correct = models.BooleanField()


def to_dict(trial: Trial):
    return dict(
        question=trial.question,
        optionA=trial.optionA,
        optionB=trial.optionB,
        optionC=trial.optionC,
        id=trial.id,
    )


def read_csv():
    import csv
    import random

    f = open('quiz/stimuli.csv', encoding='utf8')
    rows = list(csv.DictReader(f))

    random.shuffle(rows)
    return rows


# PAGES
class Stimuli(Page):
    @staticmethod
    def live_method(player: Player, data):
        my_id = player.id_in_group

        if 'choice' in data:
            if is_finished(player):
                return
            trial = get_current_trial(player)
            if data['trialId'] != trial.id:
                return
            trial.choice = data['choice']
            trial.is_correct = trial.choice == trial.solution
            player.num_correct += int(trial.is_correct)
            player.num_completed += 1

        if is_finished(player):
            return {my_id: dict(status='finished')}
        return {my_id: dict(status='next_stimulus', stimulus=to_dict(get_current_trial(player)))}


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(trials=Trial.filter(player=player))


page_sequence = [Stimuli, Results]
