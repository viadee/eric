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
        "regex": "(\\d+)(\\.\\d+)?",
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

data = pd.read_csv('titanic.csv')
data.rename(columns={'Survived': 'class'}, inplace=True)
data['Sex'] = data['Sex'].map({'male':'Male','female':'Female'})
data['Embarked'] = data['Embarked'].map({'S':'Southampton','C':'Cherbourg','Q':'Queenstown'})
data['Pclass'] = data['Pclass'].map({1:'First', 2:'Second', 3:'Third'})
data['Relatives'] = data['SibSp'] + data['Parch']

data = data.drop(['PassengerId', 'Name','Ticket','Cabin', 'SibSp', 'Parch'], axis=1)
data = data.dropna()

f = ['Pclass', 'Sex', 'Age', 'Fare', 'Embarked', 'Relatives']

features = data.drop('class', axis=1)

X_train, X_test, Y_train, Y_test = \
    train_test_split(features, data['class'].values, random_state=2)

#MODEL
numeric_features = ['Age', 'Fare', 'Relatives']
numeric_transformer = Pipeline(steps=[
    ('scaler', MinMaxScaler())])

categorical_features = ['Pclass', 'Sex', 'Embarked']
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