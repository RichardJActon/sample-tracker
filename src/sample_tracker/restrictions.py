from sample_tracker.datamodel import (
    Restriction,
    RestrictionDefinition
)
import json

def read_config(path):
    with open(path, "r") as file:
        data = json.load(file)
    return data

HTA = RestrictionDefinition(
    name = Restriction.HTA, # "HTA",
    description = "Human Tissue Act Relevent Samples",
    # based loosly on Open Survey format - modified to fit this project's needs
    # https://youropinion.is/en/docs/survey-format
    requirements = read_config('./config/hta-requirements.json')
)


BSL2 = RestrictionDefinition(
    name = Restriction.BSL2,
    description = "Biosafety Level 2 Samples",
    # requirements = read_config('./config/bsl2-requirements.json')
)

Radiation = RestrictionDefinition(
    name = Restriction.Radiation, # "HTA",
    description = "Samples with radiological protection considerations",
    # requirements = read_config('./config/radiation-requirements.json')
)
