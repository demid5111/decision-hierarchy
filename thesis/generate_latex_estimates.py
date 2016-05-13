import random

import math

expert = [False,  # managerial
          False,  # economical
          True,  # sci
          False,  # juri
          False,  # politi
          True,  # episte
          True,  # ethi
          True]  # aesthe

alternatives = [["A.MYA.1", "A.MYA.2", "A.MYA.3"],
                ["A.EKYA.1", "A.EKYA.2", "A.EKYA.3", "A.EKYA.4", "A.EKYA.5", "A.EKYA.6", "A.EKYA.7"],
                ["A.HYA.1", "A.HYA.2", "A.HYA.3", "A.HYA.4"],
                ["A.JUR.1", "A.JUR.2", "A.JUR.3"],
                ["A.POL.1", ],
                ["A.EPI.1", ],
                ["A.ETH.1", "A.ETH.2", "A.ETH.3", "A.ETH.4", "A.ETH.5", "A.ETH.6"],
                ["A.AEST.1", "A.AEST.2"]
                ]

ABSTRACTION_LEVELS = {"MYA":"МУА","EKYA":"ЭКУА","HYA":"НУА","JUR":"ЮУА","POL":"ПУА","EPI":"ЭПУА","ETH":"ЭТУА","AEST":"ЭСТУА"}
ABSTRACTION_ORDER = ["MYA","EKYA","HYA","JUR","POL","EPI","ETH","AEST"]
NAME = "name"
QUALITY = "qualitative"
SIZE = "size"
criteria = {
    # managerial
    "MYA": [
        {
            NAME: "K.MYA.1",
            QUALITY: True
        },
        {
            NAME: "K.MYA.2",
            QUALITY: False,
            SIZE: 1
        },
        {
            NAME: "K.MYA.3",
            QUALITY: False,
            SIZE: 1
        },
        {
            NAME: "K.MYA.4",
            QUALITY: True
        },
        {
            NAME: "K.MYA.5",
            QUALITY: True
        },
        {
            NAME: "K.MYA.6",
            QUALITY: False,
            SIZE: 3
        }
    ],

    # economical
    "EKYA": [
        {
            NAME: "K.EKYA.1",
            QUALITY: False,
            SIZE: 7
        },
        {
            NAME: "K.EKYA.2",
            QUALITY: False,
            SIZE: 7
        },
        {
            NAME: "K.EKYA.3",
            QUALITY: False,
            SIZE: 7
        },
        {
            NAME: "K.EKYA.4",
            QUALITY: False,
            SIZE: 7
        },
        {
            NAME: "K.EKYA.5",
            QUALITY: False,
            SIZE: 7
        },
        {
            NAME: "K.EKYA.6",
            QUALITY: True
        }
    ],

    # SCIENTIFIC
    "HYA": [
        {
            NAME: "K.HYA.1",
            QUALITY: True
        },
        {
            NAME: "K.HYA.2",
            QUALITY: False,
            SIZE: 2
        }
    ],

    # JURIDICIAL
    "JUR": [
        {
            NAME: "K.JUR.1",
            QUALITY: True
        },
        {
            NAME: "K.JUR.2",
            QUALITY: False,
            SIZE: 2
        }
    ],

    # POLITICAL
    "POL": [
        {
            NAME: "K.POL.1",
            QUALITY: True
        },
        {
            NAME: "K.POL.2",
            QUALITY: True
        },
        {
            NAME: "K.POL.3",
            QUALITY: True
        }
    ],

    # EPISTEMOLOGICAL
    "EPI": [
        {
            NAME: "K.EPI.1",
            QUALITY: True
        }
    ],

    # ETHICAL
    "ETH": [
        {
            NAME: "K.ETH.1",
            QUALITY: True
        },
        {
            NAME: "K.ETH.2",
            QUALITY: False,
            SIZE: 2
        }
    ],

    # AESTHETICAL
    "AEST": [
        {
            NAME: "K.AEST.1",
            QUALITY: True
        },
        {
            NAME: "K.AEST.2",
            QUALITY: True
        },
        {
            NAME: "K.AEST.3",
            QUALITY: True
        }
    ]
}

MAX_GRANULARITY = 9


def generate_liguistic_estimate(max_level, isExactNeeded=False):
    level = max_level
    if not isExactNeeded:
        level = 0
        while level % 2 == 0:
            level = random.randint(3, max_level)
    estimate = random.randint(1, level)
    return "\\(s_{{{}}}^{{{}}}\\)".format(estimate, level)


def generate_numeric_estimate(num_digits):
    return int(random.random() * math.pow(10, num_digits))


final_list = {}
for criteria_group in criteria:
    str_list = []

    for index, level_alternative in enumerate(alternatives):
        for alternative in level_alternative:
            res_list = []
            for criterion in criteria[criteria_group]:


                estimate = ""
                if (criterion[QUALITY]):
                    # it is the qualitative estimate
                    isExpert = expert[index]
                    if (isExpert):
                        estimate = generate_liguistic_estimate(MAX_GRANULARITY, isExactNeeded=True)
                    else:
                        estimate = generate_liguistic_estimate(MAX_GRANULARITY - 2)
                else:
                    estimate = generate_numeric_estimate(criterion[SIZE])
                res_list.append(str(estimate))

            res_list.insert(0, ".".join(["А",ABSTRACTION_LEVELS[alternative.split(".")[1]],alternative.split(".")[2]]))
            tmpStr = " & ".join(res_list)
            str_list.append(tmpStr + " \\\\ \\hline ")

    headStr = "\n".join(str_list)
    final_list[criteria_group] = headStr

for i in ABSTRACTION_ORDER:
    print(ABSTRACTION_LEVELS[i] + "\n\n")
    print(final_list[i])
    print("\n\n")
