###
# DOMAIN SPECIFIC VARIABLES
###

domain_columns_capitalized = True
float_regex = "(\\d+)(\\.\\d+)?"


#d of eric_titanic.py not referencable so it's copied here
eric_model_columns = {
    "class": {
        "feature-type": "categorical",
        "values": {
            0: "died",
            1: "survived"
        },
        "data-type": "string"
    },
    "Pclass": {
        "feature-type": "categorical",
        "values": {
            0: "First",
            1: "Second",
            2: "Third"
        },
        "data-type": "string"
    },
    "Sex": {
        "feature-type": "categorical",
        "values": {
            0: "Male",
            1: "Female"
        },
        "data-type": "string"
    },
    "Age": {
        "feature-type": "continuous",
        "regex": "(\\d+)",
        "values": {"min": 0, "max": 90},
        "data-type": "integer"
    },
    "Fare": {
        "feature-type": "continuous",
        "regex": float_regex,
        "values": {"min": 0, "max": 512},
        "data-type": "float"
    },
    "Embarked": {
        "feature-type": "categorical",
        "values": {
            0: "Southampton",
            1: "Cherbourg",
            2: "Queenstown"
            },
        "data-type": "string"
    },
    "Relatives": {
        "feature-type": "continuous",
        "regex": "(\\d+)",
        "values": {"min": 0, "max": 10},
        "data-type": "integer"
    }
}

#phrasings of the target variables
domain_specific_phrasings = {
  "died": ["die", "dies", "dead", "passed away", "perish", "perished", "dying"],
  "survived": ["survive", "survives", "live", "lives", "alive", "living"]
}
#lemmas of the target variables
domain_specific_lemmas = {
  "died": "die",
  "survived": "survive"
}

#phrasings of the "subject" to which the outcome applies to. With titanic for example these are persons for which the outcome can be "died" or "survived"
domain_specific_subject_phrasings = [
  "the person",
  "a person",
  "person",
  "the passenger",
  "a passenger",
  "passenger",
  "someone",
  "they",
  "them"
]

#general phrasings that are used in a given domain
domain_specific_replacements = {
      "first class": "first pclass",
      "second class": "second pclass",
      "third class": "third pclass",
      " class": " pclass", #if there is no space, "pclass" from input will become "ppclass"
      "1st": "first",
      "2nd": "second",
      "3rd": "third",
      "person x": "person",
      "boarded": "embarked",
      "board": "embarked",
      "embark": "embarked",
      "younger": "Age",
      "older": "Age",
      "old": "Age",
      "young": "Age",
      "ticket": "Fare"
    }