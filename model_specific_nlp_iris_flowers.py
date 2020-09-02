###
# DOMAIN SPECIFIC VARIABLES
###

domain_columns_capitalized = False
float_regex = "(\\d+)(\\.\\d+)?"

#d of eric_titanic.py not referencable so it's copied here
eric_model_columns = {
    "class": {
        "feature-type": "categorical",
        "values": {
            0: "Iris-setosa",
            1: "Iris-versicolor",
            2: "Iris-virginica"
        },
        "data-type": "string"
    },
    "sepal_length": {
        "feature-type": "continuous",
        "regex": float_regex,
        "values": {"min": 0, "max": 10},
        "data-type": "float"
    },
    "sepal_width": {
        "feature-type": "continuous",
        "regex": float_regex,
        "values": {"min": 0, "max": 10},
        "data-type": "float"
    },
    "petal_length": {
        "feature-type": "continuous",
        "regex": float_regex,
        "values": {"min": 0, "max": 10},
        "data-type": "float"
    },
    "petal_width": {
        "feature-type": "continuous",
        "regex": float_regex,
        "values": {"min": 0, "max": 10},
        "data-type": "float"
    }
}

#phrasings of the target variables
domain_specific_phrasings = {
  "Iris-setosa": ["iris-setosa", "iris setosa", "bristle-pointed iris", "bristle pointed iris", "bristle-pointed", "bristle pointed", "setosa"],
  "Iris-versicolor": ["iris-versicolor", "iris versicolor", "blue flag", "harlequin", "harlequin blueflag", "poison flag", "versicolor"],
  "Iris-virginica": ["iris-virginica", "iris virginica", "virginica iris", "iris-virginia", "iris virginia", "virginia iris", "virginica", "virginia"]
}
#lemmas of the target variables
domain_specific_lemmas = {
  "Iris-setosa": "setosa",
  "Iris-versicolor": "versicolor",
  "Iris-virginica": "virginica"
}

#phrasings of the "subject" to which the outcome applies to. With titanic for example these are persons for which the outcome can be "died" or "survived"
domain_specific_subject_phrasings = [
  "the flower",
  "a flower",
  "flower",
  "the plant",
  "a plant",
  "plant",
  "it"
]

#general phrasings that are used in a given domain
domain_specific_replacements = {
  "lengths": "length",
  "widths": "width",
  "petals": "petal",
  "sepals": "sepal",
  "petal length": "petal_length",
  "petal width": "petal_width",
  "sepal length": "sepal_length",
  "sepal width": "sepal_width",
  "length of the petal": "petal_length",
  "width of the petal": "petal_width",
  "length of the sepal": "sepal_length",
  "width of the sepal": "sepal_width"
}