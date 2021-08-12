import random
from abc import abstractmethod


class BaseSearchString:
    SYSTEM = {
        "land": [
            "working lands", "managed lands", "AFOLU",
            "land use sector", "land-use sector", "LULC"
        ],
        "agriculture": [
            "agricultur", "agroforestry", "graz", "crop", "farm", "agroecolog"
        ],
        "forest": [
            "forestry", "reforestation", "forest management"
        ]
    }

    INTERVENTION = {
        "carbon markets": [
            "carbon market", "carbon offset", "carbon offsetting", "carbon credit",
            "carbon credits",
            "carbon accounting", "greenhouse gas accounting", "GHG accounting",
            "environmental credit", "environmental credits", "environmental crediting"
        ],
        "climate change": [
            "climate change action", "climate change mitigation", "climate action",
            "climate mitigation", "climate actions", "carbon project", "carbon projects",
            "carbon-project", "carbon-projects", "carbon intervention",
            "emissions reduction scheme",
            "ERS", "emissions trading scheme", "ETS", "emissions trading schemes",
            "climate change policy",
            "climate mitigation policy", "climate change mitigation policy",
            "climate change action policy",
            "climate action policy"
        ]
    }

    OUTCOME = {
        "co-benefits": [
            "co-benefit", "cobenefit", "added value", "ecosystem services"
        ],
        "ESG": [
            "SDG", "sustainable development goals", "ESG",
            "environmental, social and corporate governance",
            "CSR", "corporate social responsibility"
        ],
        "biodiversity": [
            "biodiversity", "species richness", "wildlife", "pollinator", "flora", "fauna",
            "environmental protection", "protected area", "conservation", "habitat"
        ],
        "development": [
            "livelihoods", "financial", "econom", "employment", "profit", "poverty", "inequalit"
        ],
        "ecosystem services": [
            "payment for ecosystem services", "PES", "environmental service",
            "payments for ecosystem services"
        ],
        "resources": [
            "food security", "water security", "water access", "energy security",
            "water rights", "water quality", "pollution"],
    }

    def __init__(self):
        self.name = None
        self.pub_year_filter = None
        self.system_kw, self.intervention_kw, self.outcome_kw = self._get_search_string_terms()

    @classmethod
    def _get_search_string_terms(cls):
        tpl = tuple([
            random.sample(bucket[random.choice(list(bucket.keys()))], k=3)
            for bucket in [cls.SYSTEM, cls.INTERVENTION, cls.OUTCOME]
        ])
        return tpl

    @property
    @abstractmethod
    def API_URL(self):
        raise NotImplementedError('Class should have this attribute.')

    @abstractmethod
    def generate_search_string(self):
        raise NotImplementedError('Method should be implemented')

    @abstractmethod
    def get_query_from_search_string(self):
        raise NotImplementedError('Method should be implemented')

    def JSON(self) -> dict:
        return {
            'name': self.name,
            'system_keywords': ', '.join(self.system_kw) if self.system_kw else None,
            'intervention_keywords': ', '.join(self.intervention_kw) if self.intervention_kw else None,
            'outcome_keywords': ', '.join(self.outcome_kw) if self.outcome_kw else None,
            'pub_year_filter': self.pub_year_filter
        }

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name is not None and other.name is not None and self.name == other.name
        else:
            return False

    def __str__(self):
        return self.name
