from os import environ


SESSION_CONFIGS = [
    dict(
        name='double_auction',
        display_name='Double auction',
        app_sequence=['double_auction'],
        num_demo_participants=3,
        players_per_group=3,
    ),
    dict(
        name='dollar_auction',
        display_name='Dollar auction',
        app_sequence=['dollar_auction'],
        num_demo_participants=3,
        players_per_group=3,
    ),
    dict(
        name='stroop',
        display_name='Stroop test',
        app_sequence=['stroop'],
        num_demo_participants=1,
    ),
    dict(
        name='go_no_go',
        display_name='Go/No-Go task',
        app_sequence=['go_no_go'],
        num_demo_participants=1,
    ),
    dict(
        name='bigfive',
        display_name='Big 5 personality test',
        app_sequence=['bigfive'],
        num_demo_participants=1,
    ),
    dict(
        name='nim',
        display_name="Race game / Nim (take turns adding numbers to reach a target)",
        app_sequence=['nim'],
        num_demo_participants=2,
    ),
    dict(
        name='monty_hall',
        display_name="Monty Hall (3-door problem from 'The Price is Right')",
        app_sequence=['monty_hall'],
        num_demo_participants=1,
    ),
    dict(
        name='public_goods',
        display_name="Public Goods",
        num_demo_participants=3,
        players_per_group=3,
        app_sequence=['public_goods'],
        multiplier=2,
        endowment=100,
    ),
    dict(
        name='guess_two_thirds',
        display_name="Guess 2/3 of the Average",
        num_demo_participants=3,
        players_per_group=3,
        app_sequence=['guess_two_thirds'],
    ),
    dict(
        name='trust',
        display_name="Trust Game",
        num_demo_participants=2,
        app_sequence=['trust'],
    ),
    dict(
        name='ultimatum',
        display_name="Ultimatum Game",
        num_demo_participants=2,
        app_sequence=['ultimatum'],
    ),
    dict(
        name='prisoner',
        display_name="Prisoner's Dilemma",
        num_demo_participants=2,
        app_sequence=['prisoner'],
    ),
    dict(
        name='volunteer_dilemma',
        display_name="Volunteer's Dilemma",
        num_demo_participants=3,
        players_per_group=3,
        app_sequence=['volunteer_dilemma'],
    ),
    dict(
        name='cournot',
        display_name="Cournot Competition",
        num_demo_participants=2,
        app_sequence=['cournot'],
    ),
    dict(
        name='dictator',
        display_name="Dictator Game",
        num_demo_participants=2,
        app_sequence=['dictator'],
    ),
    dict(
        name='matching_pennies',
        display_name="Matching Pennies",
        num_demo_participants=2,
        app_sequence=['matching_pennies'],
    ),
    dict(
        name='traveler_dilemma',
        display_name="Traveler's Dilemma",
        num_demo_participants=2,
        app_sequence=['traveler_dilemma'],
    ),
    dict(
        name='bargaining',
        display_name="Bargaining Game",
        num_demo_participants=2,
        app_sequence=['bargaining'],
    ),
    dict(
        name='common_value_auction',
        display_name="Common Value Auction",
        num_demo_participants=3,
        players_per_group=3,
        app_sequence=['common_value_auction'],
    ),
    dict(
        name='bertrand',
        display_name="Bertrand Competition",
        num_demo_participants=2,
        app_sequence=['bertrand'],
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['transaction_history']

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '{{ secret_key }}'

INSTALLED_APPS = ['otree']
