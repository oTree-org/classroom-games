from otree.api import *
from shared_out import set_players_per_group
import time
import random
import ast


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
        if p.is_buyer:
            p.num_items = 0
            p.break_even_point = random.randint(Constants.valuation_min, Constants.valuation_max)
            p.current_offer = 0
        else:
            p.num_items = Constants.items_per_seller
            p.break_even_point = random.randint(
                Constants.production_costs_min, Constants.production_costs_max
            )
            p.current_offer = Constants.valuation_max + 1
        p.break_even_history = '[0,' + str(p.break_even_point) + ']'

def vars_for_admin_report(subsession: Subsession):
    players = subsession.get_players()
    group = players[0].group

    break_even_players = {player.id_in_group : ast.literal_eval('[ ' + player.break_even_history + ' ]')
                          for player in players}

    transactions = [[tx.seconds, tx.price] for tx in Transaction.filter(group=group)]

    return dict(
        transactions=transactions,
        break_even_players=break_even_players,
        num_players=len(players)
    )


class Group(BaseGroup):
    start_timestamp = models.IntegerField()


class Player(BasePlayer):
    is_buyer = models.BooleanField()
    current_offer = models.CurrencyField()
    break_even_point = models.CurrencyField()
    num_items = models.IntegerField()
    break_even_history = models.StringField()

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
                group=group,
                buyer=buyer,
                seller=seller,
                price=price,
                seconds=seconds,
            )
            buyer.num_items += 1
            seller.num_items -= 1
            buyer.payoff += buyer.break_even_point - price
            seller.payoff += price - seller.break_even_point
            buyer.current_offer = 0
            seller.current_offer = Constants.valuation_max + 1
            buyer.break_even_point = random.randint(Constants.valuation_min, buyer.break_even_point)
            buyer.break_even_history += ',[ ' + str(seconds) + ',' + str(buyer.break_even_point) + ']'
            seller.break_even_point = random.randint(seller.break_even_point, Constants.production_costs_max)
            seller.break_even_history += ',[ ' + str(seconds) + ',' + str(seller.break_even_point) + ']'
            news = dict(buyer=buyer.id_in_group, seller=seller.id_in_group, price=price)

    bids = sorted([p.current_offer for p in buyers if p.current_offer > 0], reverse=True)
    asks = sorted([p.current_offer for p in sellers if p.current_offer <= Constants.valuation_max])
    highcharts_series = [[tx.seconds, tx.price] for tx in Transaction.filter(group=group)]

    return {
        p.id_in_group: dict(
            bids=bids,
            asks=asks,
            highcharts_series=highcharts_series,
            num_items=p.num_items,
            current_offer=p.current_offer,
            news=news,
            payoff=p.payoff,
            break_even=p.break_even_point
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
