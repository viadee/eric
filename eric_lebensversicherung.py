from server import ERIC
from sklearn.model_selection import train_test_split # Import train_test_split function
from sklearn.pipeline import Pipeline
import pandas as pd 
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn import svm
from sklearn.metrics import accuracy_score
from mlobject import *
from extension import *

#DATA
d = {
    "class": {
        "feature-type": "categorical",
        "values": {
            0: "Abgelehnt", #abgelehnt
            1: "Angenommen" #angenommen
        },
        "data-type": "string"
    },
    "Gesundheitsrisiko": { #Gesundheitsrisiko
        "feature-type": "categorical",
        "values": {
            0: "Niedrig", #niedrig
            1: "Mittel", #mittel
            2: "Hoch" #hoch
        },
        "data-type": "string"
    },
    "Geschlecht": {
        "feature-type": "categorical",
        "values": {
            0: "Männlich", #weiblich
            1: "Weiblich" #männlich
        },
        "data-type": "string"
    },
    "Alter": {
        "feature-type": "continuous",
        "regex": "(\\d+)",
        "values": {"min": 0, "max": 90},
        "data-type": "integer"
    },
    "Stand": { #Familienstand/Berufsausbildung
        "feature-type": "categorical",
        "values": {
            0: "Verheiratet",
            1: "Geschieden",
            2: "Ledig"
            },
        "data-type": "string"
    },
    "Kinder": { #Anzahl Kinder
        "feature-type": "continuous",
        "regex": "(\\d+)",
        "values": {"min": 0, "max": 10},
        "data-type": "integer"
    }
}

data = pd.read_csv('titanic.csv')
data.rename(columns={'Survived': 'class'}, inplace=True)
data.rename(columns={'Pclass': 'Gesundheitsrisiko'}, inplace=True)
data.rename(columns={'Sex': 'Geschlecht'}, inplace=True)
data.rename(columns={'Age': 'Alter'}, inplace=True)
data.rename(columns={'Embarked': 'Stand'}, inplace=True)
data.rename(columns={'Survived': 'class'}, inplace=True)
data['Geschlecht'] = data['Geschlecht'].map({'male':'Männlich','female':'Weiblich'})
data['Stand'] = data['Stand'].map({'S':'Verheiratet','C':'Geschieden','Q':'Ledig'})
data['Gesundheitsrisiko'] = data['Gesundheitsrisiko'].map({1:'Niedrig', 2:'Mittel', 3:'Hoch'})
data['Kinder'] = data['SibSp'] + data['Parch']

data = data.drop(['PassengerId', 'Name','Ticket','Cabin', 'SibSp', 'Parch', 'Fare'], axis=1)
data = data.dropna()

f = ['Gesundheitsrisiko', 'Geschlecht', 'Alter', 'Stand', 'Kinder']

features = data.drop('class', axis=1)

X_train, X_test, Y_train, Y_test = \
    train_test_split(features, data['class'].values, random_state=2)

#MODEL
numeric_features = ['Alter', 'Kinder']
numeric_transformer = Pipeline(steps=[
    ('scaler', MinMaxScaler())])

categorical_features = ['Gesundheitsrisiko', 'Geschlecht', 'Stand']
categorical_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore'))])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)])

model = Pipeline(steps=[('preprocessor', preprocessor),
('classifier', svm.SVC(probability=True))])

model.fit(X_train, Y_train)

print("SVM {}".format(accuracy_score(Y_test, model.predict(X_test))))

m = mlObject(X_train, X_test, Y_train, Y_test, f, d, model)

#RUN
eric = ERIC(m)
eric.registerExtension(featureImportance)
eric.registerExtension(getNthLargest)
eric.registerExtension(getFeatureValue)
eric.registerExtension(addition)
eric.start()