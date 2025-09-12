from enum import Enum

FieldIds = Enum(
    "FieldIds",
    [
        ("respondent", "Wz6EJ0SrP537"),
        ("email", "mQQ6n4XODVE8"),
        ("role", "7rGpb91gC5Zv"),
        ("church", "4yBh92Cyp8hz"),
    ],
)

CSV_HEADERS = [
    "submitted_at",
    "respondent",
    "email",
    "role",
    "church",
    "discipleship",
    "education",
    "training",
    "sending",
    "sending1",
    "membercare",
    "support",
    "praying",
    "giving",
    "community",
    "structure",
    "organisation",
    "policies",
    "partnerships",
    "score",
    "finalpercentage",
]

DOMAIN_HEADERS = [
    "discipleship",
    "sending",
    "support",
    "structure",
]

DISPLAY_NAMES = {
    "discipleship": "Discipleship",
    "sending": "Sending",
    "support": "Support",
    "structure": "Structure",
    "education": "Education",
    "training": "Training",
    "sending1": "Sending",
    "membercare": "Member Care",
    "praying": "Praying",
    "giving": "Giving",
    "community": "Community",
    "organisation": "Organisation",
    "policies": "Policies",
    "partnerships": "Partnerships",
}


def convertFromUpon25To100(scoreUpon25):
    return (scoreUpon25 / 25) * 100


class FormResponseAnswersFields:
    def __init__(self, **kwargs):
        self.respondent = kwargs.get("respondent")
        self.email = kwargs.get("email")
        self.role = kwargs.get("role")
        self.church = kwargs.get("church")


class FormResponseScores:
    def __init__(self, **kwargs):
        # Domain 1: Discipleship
        self.discipleship = convertFromUpon25To100(kwargs.get("discipleship"))
        self.education = kwargs.get("education")
        self.training = kwargs.get("training")

        # Domain 2: Sending
        self.sending = convertFromUpon25To100(kwargs.get("sending"))
        self.sending1 = kwargs.get("sending1")
        self.membercare = kwargs.get("membercare")

        # Domain 3: Support
        self.support = convertFromUpon25To100(kwargs.get("support"))
        self.praying = kwargs.get("praying")
        self.giving = kwargs.get("giving")
        self.community = kwargs.get("community")

        # Domain 4: Structure
        self.structure = convertFromUpon25To100(kwargs.get("structure"))
        self.organisation = kwargs.get("organisation")
        self.policies = kwargs.get("policies")
        self.partnerships = kwargs.get("partnerships")

        ranked_scores = [
            ("education", self.education),
            ("training", self.training),
            ("sending1", self.sending1),
            ("membercare", self.membercare),
            ("praying", self.praying),
            ("giving", self.giving),
            ("community", self.community),
            ("organisation", self.organisation),
            ("policies", self.policies),
            ("partnerships", self.partnerships),
        ]
        ranked_scores.sort(key=lambda x: x[1], reverse=True)

        self.top_3_strongest_subdomains = [ranked_scores[i] for i in range(3)]
        self.bottom_3_weakest_subdomains = [
            ranked_scores[i]
            for i in range(len(ranked_scores) - 1, len(ranked_scores) - 4, -1)
        ]

        self.score = kwargs.get("score")
        self.finalpercentage = kwargs.get("finalpercentage")


class FormResponse:
    def map_scores_args(self, raw_scores):
        args_for_scores = dict()
        for score in raw_scores:
            args_for_scores[score["key"]] = score["number"]
        return args_for_scores

    def __init__(self, raw_response):
        self.submitted_at = raw_response["submitted_at"]

        # Form response answers
        args_for_answers = dict()
        for answer in raw_response["answers"]:
            try:
                field_name = FieldIds(answer["field"]["id"]).name
                args_for_answers[field_name] = (
                    answer["text"] if answer["type"] == "text" else answer["email"]
                )
            except:
                continue
        self.answers = FormResponseAnswersFields(**args_for_answers)

        # Form response scores
        args_for_scores = self.map_scores_args(raw_response["variables"])
        self.scores = FormResponseScores(**args_for_scores)

    def parse_to_row(self):
        return {
            "submitted_at": self.submitted_at,
            "respondent": self.answers.respondent,
            "email": self.answers.email,
            "role": self.answers.role,
            "church": self.answers.church,
            "discipleship": self.scores.discipleship,
            "education": self.scores.education,
            "training": self.scores.training,
            "sending": self.scores.sending,
            "sending1": self.scores.sending1,
            "membercare": self.scores.membercare,
            "support": self.scores.support,
            "praying": self.scores.praying,
            "giving": self.scores.giving,
            "community": self.scores.community,
            "structure": self.scores.structure,
            "organisation": self.scores.organisation,
            "policies": self.scores.policies,
            "partnerships": self.scores.partnerships,
            "score": self.scores.score,
            "finalpercentage": self.scores.finalpercentage,
        }
