from otree.api import *
from shared_out import set_players_per_group
import time
import random


class Constants(BaseConstants):
    name_in_url = 'double_auction'
    players_per_group = None
    num_rounds = 1
    items_per_seller = 3
    valuation_min = cu(50)
    valuation_max = cu(110)
    production_costs_min = cu(10)
    production_costs_max = cu(80)


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    set_players_per_group(subsession)
    players = subsession.get_players()
    for p in players:
        # for more buyers, change the 2 to 3
        p.is_buyer = p.id_in_group % 2 > 0
        participant = p.participant
        participant.transaction_history = []
        if p.is_buyer:
            p.num_items = 0
            p.break_even_point = random.randint(
                Constants.valuation_min, Constants.valuation_max
            )
            p.current_offer = 0
        else:
            p.num_items = Constants.items_per_seller
            p.break_even_point = random.randint(
                Constants.production_costs_min, Constants.production_costs_max
            )
            p.current_offer = Constants.valuation_max + 1
        participant.transaction_history.append([0, int(p.break_even_point)])


def vars_for_admin_report(subsession: Subsession):
    groups = subsession.get_groups()

    break_evens = {}
    transaction_data = {}
    group_counter = 0

    for group in groups:
        group_counter += 1
        players = group.get_players()
        break_evens_group = {
            'BE: G{}-P{}'.format(
                group_counter, player.id_in_group
            ): player.participant.transaction_history
            for player in players
        }
        break_evens.update(break_evens_group)
        for tx in Transaction.filter(group=group):
            key = 'Transactions: G{}'.format(group_counter)
            if key not in transaction_data:
                transaction_data[key] = []
            transaction_data[key].append([tx.seconds, tx.price])

    highcharts_series = []

    for key in break_evens.keys():
        highcharts_series.append(
            {'name': key, 'data': break_evens[key], 'type': 'line'}
        )

    for key in transaction_data.keys():
        highcharts_series.append(
            {'name': key, 'data': transaction_data[key], 'type': 'scatter',}
        )

    return dict(highcharts_series=highcharts_series)


class Group(BaseGroup):
    start_timestamp = models.IntegerField()


class Player(BasePlayer):
    is_buyer = models.BooleanField()
    current_offer = models.CurrencyField()
    break_even_point = models.CurrencyField()
    num_items = models.IntegerField()


class Transaction(ExtraModel):
    group = models.Link(Group)
    buyer = models.Link(Player)
    seller = models.Link(Player)
    price = models.CurrencyField()
    seconds = models.IntegerField(doc="Timestamp (seconds since beginning of trading)")


def find_match(buyers, sellers):
    for buyer in buyers:
        for seller in sellers:
            if seller.num_items > 0 and seller.current_offer <= buyer.current_offer:
                return [buyer, seller]


def live_method(player: Player, data):
    group = player.group
    players = group.get_players()
    buyers = [p for p in players if p.is_buyer]
    sellers = [p for p in players if not p.is_buyer]
    news = None
    if data:
        try:
            offer = int(data['offer'])
        except Exception:
            print('invalid message received:', data)
            return
        player.current_offer = offer
        if player.is_buyer:
            match = find_match(buyers=[player], sellers=sellers)
        else:
            match = find_match(buyers=buyers, sellers=[player])
        if match:
            [buyer, seller] = match
            price = buyer.current_offer
            seconds = int(time.time() - group.start_timestamp)
            Transaction.create(
                group=group, buyer=buyer, seller=seller, price=price, seconds=seconds,
            )
            buyer.num_items += 1
            seller.num_items -= 1
            buyer.payoff += buyer.break_even_point - price
            seller.payoff += price - seller.break_even_point
            buyer.current_offer = 0
            seller.current_offer = Constants.valuation_max + 1
            buyer.break_even_point = random.randint(
                Constants.valuation_min, buyer.break_even_point
            )
            buyer.participant.transaction_history.append(
                [seconds, int(buyer.break_even_point)]
            )
            seller.participant.transaction_history.append(
                [seconds, int(seller.break_even_point)]
            )
            news = dict(buyer=buyer.id_in_group, seller=seller.id_in_group, price=price)

    bids = sorted(
        [p.current_offer for p in buyers if p.current_offer > 0], reverse=True
    )
    asks = sorted(
        [p.current_offer for p in sellers if p.current_offer <= Constants.valuation_max]
    )
    highcharts_series = [
        [tx.seconds, tx.price] for tx in Transaction.filter(group=group)
    ]

    return {
        p.id_in_group: dict(
            bids=bids,
            asks=asks,
            highcharts_series=highcharts_series,
            num_items=p.num_items,
            current_offer=p.current_offer,
            news=news,
            payoff=p.payoff,
            break_even=p.break_even_point,
        )
        for p in players
    }


# PAGES
class WaitToStart(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        group.start_timestamp = int(time.time())


class Trading(Page):
    live_method = live_method

    @staticmethod
    def js_vars(player: Player):
        return dict(id_in_group=player.id_in_group, is_buyer=player.is_buyer)

    @staticmethod
    def get_timeout_seconds(player: Player):
        import time

        group = player.group
        return 5 * 60 + group.start_timestamp - time.time()


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [WaitToStart, Trading, ResultsWaitPage, Results]
