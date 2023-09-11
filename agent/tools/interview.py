import json
import requests
from iteration_utilities import deepflatten
from typing import List, Optional, Type, Union
from pydantic import BaseModel
from langchain.tools import BaseTool


class BlawxCategory(BaseModel):
    """
    The data structure for a fact about membership in a category.
    """

    from_ontology: bool
    type: str
    category: str
    object: str

class BlawxAttributeBinary(BaseModel):
    """
    The data structure for a binary attribute.
    """

    from_ontology: bool
    type: str
    attribute: str
    object: str
    value: str

class BlawxAttributeUnary(BaseModel):
    """
    The data structure for a unary attribute.
    """

    from_ontology: bool
    type: str
    attribute: str
    object: str

class BlawxRelationship(BaseModel):
    """
    The data structure for a relationship fact.
    """

    from_ontology: bool
    type: str
    relationship: str
    parameter1: str
    parameter2: str
    parameter3: str
    # This would need to be extended later.

BlawxFact = Union[BlawxCategory, BlawxRelationship, BlawxAttributeBinary, BlawxAttributeUnary]

class BlawxFacts(BaseModel):
    """
    This documents the data structure used by the interview and run endpoints.
    """
    facts: List[BlawxFact]

class RPSInterview(BaseTool):
    name = "get_winner_of_rps_game"
    description = """
Useful for finding out who won games of rock paper scissors.

Requires you to know the ontology first.

The "type" of each fact should be the string "true", and the "from_ontology" value should be set to boolean false.

Games and players must be defined in category facts before they are used in attribute and relationship facts.

All values should be strings that start with lowercase letters and do not contain spaces.

The facts must only use the category names "game" and "player", the attribute name "participant", and the relationship "throw", which accepts player, sign and game in that order.
The facts must include statements of what games each player participated in, in addition to statements of what signs they threw in those games.

"""

    def _run(self, facts):
        return interview({"facts": facts})

    def _arun(self, input):
        raise NotImplementedError("The get_winner_of_rps_game tool does not support asynchronous requests.")

    args_schema: Optional[Type[BaseModel]] = BlawxFacts

def interview(input):
  response = requests.post('https://dev.blawx.com/jason/rock-paper-scissors-act/test/who_wins/run/',json=input)
  package = json.loads(response.text)
  if len(package['Answers']):
    return "The winner is " + package['Answers'][0]['Variables']['Player'] + " because " + ''.join(list(deepflatten(package['Answers'][0]['Models'][0]['Tree'])))
  else:
    return "There is no answer."
  
  class BlawxFacts(BaseModel):
    """
    This documents the data structure used by the interview and run endpoints.
    """
    facts: List[BlawxFact]

class PIInterview(BaseTool):
    name = "get_pi_for_purposes"
    description = """
Useful for finding out whether information is personal information for the purposes of section 19 of the
Access to Information Act.

Requires you to know the ontology first.

The "type" of each fact should be the string "true", and the "from_ontology" value should be set to boolean false.

Pieces of information and individuals must be defined in category facts before they are used in attribute and relationship facts.

All values should be strings that start with lowercase letters and do not contain spaces.

The facts must use exclusively the category predicates "individual" and "information", and the attribute predicates
"about", "recorded", "about_identifiable_individual", "relates_to_race_of", and "date_of_death".

"about_identifiable_individual" is a unary predicate for which a value should not be provided.

"""

    def _run(self, facts):
        return privacy_interview({"facts": facts})

    def _arun(self, input):
        raise NotImplementedError("The get_pi_for_purposes tool does not support asynchronous requests.")

    args_schema: Optional[Type[BaseModel]] = BlawxFacts

# Try: I have a written record that identifies bob barker as caucasian. Is that private information for the purposes of the Access to Information Act, section 19?
def privacy_interview(input):
  response = requests.post('http://localhost:8000/jason/privacy-act/test/pi_for_purposes/run/',json=input)
  #print(response.text)
  package = json.loads(response.text)
  if len(package['Answers']):
    return "I should use only the following information to answer the question: " + package['Answers'][0]['Variables']['A'] + " is personally identifying information for the purposes of section 19 of the AITA because " + ''.join(list(deepflatten(package['Answers'][0]['Models'][0]['Tree'])))
  else:
    return "I should use only the following information to answer the question: There is no evidence based on these facts to conclude that anything is personally identifying information for the purposes of section 19 of the AITA."