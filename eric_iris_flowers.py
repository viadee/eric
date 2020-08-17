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
            0: "Iris-setosa",
            1: "Iris-versicolor",
            2: "Iris-virginica"
        },
        "data-type": "string"
    },
    "sepal_length": {
        "feature-type": "continuous",
        "regex": "(\\d+)(\\.\\d+)?",
        "values": {"min": 0, "max": 10},
        "data-type": "float"
    },
    "sepal_width": {
        "feature-type": "continuous",
        "regex": "(\\d+)(\\.\\d+)?",
        "values": {"min": 0, "max": 10},
        "data-type": "float"
    },
    "petal_length": {
        "feature-type": "continuous",
        "regex": "(\\d+)(\\.\\d+)?",
        "values": {"min": 0, "max": 10},
        "data-type": "float"
    },
    "petal_width": {
        "feature-type": "continuous",
        "regex": "(\\d+)(\\.\\d+)?",
        "values": {"min": 0, "max": 10},
        "data-type": "float"
    }
}

data = pd.read_csv("data\\datasets\\iris_flowers.csv")
data.rename(columns={'species': 'class'}, inplace=True)

data = data.dropna()

f = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']

features = data.drop('class', axis=1)

X_train, X_test, Y_train, Y_test = \
    train_test_split(features, data['class'].values, random_state=2)

#MODEL
numeric_features = f
numeric_transformer = Pipeline(steps=[
    ('scaler', MinMaxScaler())])

categorical_features = []
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