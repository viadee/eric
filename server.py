import clips
import time
import pandas as pd 
from sklearn.model_selection import train_test_split # Import train_test_split function
import numpy as geek
import random as random
import sys
from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
from twisted.python import log
from twisted.internet import reactor
import json 
from mlobject import *
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn import svm
from sklearn.metrics import accuracy_score
import base64
import shutil
import os.path
from os import path
from extension import *
from dictionary import dictionary

class ruleEnvironment:
    def __init__(self, mlObject):
        self.env = clips.Environment()
        self.mlObject = mlObject
        self.fact_type = "input ui"
        self.clips_type = "symbol"
        self.set_of_functions = dictionary

    def initEnvironment(self):
        self.env.define_function(self.mlObject.predict_connector, name="predict_connector")
        self.env.define_function(self.mlObject.anchors_connector, name="anchors_connector")
        self.env.define_function(self.mlObject.ceterisParibus_connector, name="ceterisParibus_connector")
        self.env.define_function(self.mlObject.cf_proto_how_connector, name="cf_proto_how_connector")
        self.env.define_function(self.mlObject.cf_proto_why_connector, name="cf_proto_why_connector")
        self.env.define_function(self.printFacts, name="printFacts")
        self.env.define_function(self.get_random_text_slot, name="get_random_text_slot")
        self.env.define_function(self.message_from_clips, name="message_from_clips")  
        self.env.define_function(self.getValidAnswersForFeatureValues, name="getValidAnswersForFeatureValues")
        self.env.define_function(self.getTimestamp, name="getTimestamp")
        self.env.define_function(self.mlObject.getExplanation, name="getExplanation")
        self.env.define_function(self.mlObject.getCertainty, name="getCertainty")
        self.env.define_function(self.mlObject.resetCertainty, name="resetCertainty")
        self.env.define_function(self.mlObject.getDataPreview, name="getDataPreview")
        self.env.define_function(self.mlObject.getSurrogateRule, name="getSurrogateRule")
        self.env.define_function(self.mlObject.getSurrogateVisualization, name="getSurrogateVisualization")
        self.env.define_function(self.mlObject.shap_why_connector, name="shap_why_connector")

        self.env.load('./rules/system.clp') 
        self.env.load('./rules/values.clp') 
        self.env.load('./rules/prediction.clp') 
        self.env.load('./rules/why.clp') 
        self.env.load('./rules/whatif.clp')
        self.env.load('./rules/how-to.clp')
        self.env.load('./rules/whatif-gtl.clp')
        self.env.load('./rules/input.clp')
        self.env.load('./rules/when.clp')
        self.env.load('./rules/why-not.clp')        

        self.assignInitialFeatureMeta()
        self.assignInitialPredictionList() #MUST BE ACTIVATED
        self.assignInitialTargetValues()
        self.assignUserPreferences()
        self.assignFoil()

        self.clearTemp()

    #Registers an ERIC extension object as a new command
    def registerCommand(self, command):
        self.set_of_functions.append({   
            "id" : command.name,
            "keywords" : command.keywords,
            "display" : command.display,
            "write" : command.write,
            "execute" : command.name,
            "description": command.description
        })
        setattr(mlObject, command.name, command.function)
        self.env.define_function(getattr(self.mlObject, command.name), name=command.name)
        rules = command.generateRules()
        for r in rules:
            self.env.build(r)
    
    #Clears the temp and plots folder which is used for images
    def clearTemp(self):
        if path.exists("temp"):
            shutil.rmtree("temp")
        os.makedirs("temp") 

        if path.exists("_plot_files"):
            shutil.rmtree("_plot_files")
        os.makedirs("_plot_files")

    #Assigns initial user preference
    def assignUserPreferences(self):
        self.env.assert_string('(preference explanation rule attribution counterfactual)')

    #Assigns the initial foil arrangement
    def assignFoil(self):
        self.env.assert_string('(foil ' +  ' '.join('"' + str(e) + '"' for e in self.mlObject.dictionary["class"]["values"].values()) + ')')
    
    #For timestamp in clips
    def getTimestamp(self):
        return(time.time())

    #Assigns the initial prediction list
    def assignInitialPredictionList(self):
        self.env.assert_string('(list(name predictions) (content nil))')

    #Assigns feature meta data to clips as facts
    def assignInitialFeatureMeta(self):
        for f in self.mlObject.featureNames:
            if self.mlObject.dictionary[f]["feature-type"] == "categorical":
                values = ' '.join('"' + str(e) + '"' for e in self.mlObject.dictionary[f]["values"].values())
                self.env.assert_string('(feature-meta(name ' + f + ')' + '(data-type ' + self.mlObject.dictionary[f]["data-type"] + ')' + '(feature-type ' + self.mlObject.dictionary[f]["feature-type"] + ')' + '(values ' + values + ')' + '(weight 1))')  
            else: 
                self.env.assert_string('(feature-meta(name ' + f + ')' + '(data-type ' + self.mlObject.dictionary[f]["data-type"] + ')' + '(feature-type ' + self.mlObject.dictionary[f]["feature-type"] + ')' + '(values ' + str(self.mlObject.dictionary[f]["values"]["min"]) + " " + str(self.mlObject.dictionary[f]["values"]["max"]) +  ')' + '(regex "' + self.mlObject.dictionary[f]["regex"] + '")' + '(weight 1))')  

    #Assigns target value meta data to clips as facts
    def assignInitialTargetValues(self):
        for t in self.mlObject.dictionary["class"]["values"].values():
            self.env.assert_string('(target-instance-meta(name "' + t + '")' + '(weight 1))')
        
    #Returns valid answer restriction for a feature
    def getValidAnswersForFeatureValues(self, feature):
        if self.mlObject.dictionary[feature]["feature-type"] == "categorical":
            valid_answers = {'type' : 'selection', 'value' : list(self.mlObject.dictionary[feature]["values"].values())}
        else:
            valid_answers = {'type' : 'regex', 'value' : self.mlObject.dictionary[feature]["regex"]}
        return(json.dumps(valid_answers))

    #Prints the currently existing facts into console
    def printFacts(self):
        print("----")
        for fact in self.env.facts():
            print(fact)
        print("----")

    #Returns a random number for selecting random text in clips
    def get_random_text_slot(self, min, max):
        return(random.randrange(min, max+1))

    #Connector between clips and Python server. Called from clips.
    def message_from_clips(self, text, image_url, valid_answers, clips_type, clipboard, fact_type, skip):
        image = ""
        if image_url != "''":
            with open(image_url, "rb") as image_file:
                image = base64.b64encode(image_file.read()).decode('utf-8')

        message = {'type':'message', 'text': str(text), 'image': image, 'valid-answers': eval(valid_answers), 'clipboard': eval(clipboard)}
        MyServerProtocol.broadcast_message(message)

        if(clips_type != "''"):
            self.clips_type = clips_type
        else:
            self.clips_type = "symbol"
            
        self.fact_type = str(fact_type)
        if str(fact_type) == 'skip':
            if str(skip) != "":
                self.message_to_clips(str(skip))
                print("Skipping and new fact")
            else:
                print("Skipping and no fact")
        
    #Connector between clips and Python server. Called from Python.
    def message_to_clips(self, message):
        print("Message to clips: " + message)
        print("fact type: " + self.fact_type)
        print("clips type: " + self.clips_type)
    
        if(self.fact_type == 'skip'):
            self.env.assert_string('(' + message + ')')
        else:
            if self.clips_type == 'string':
                self.env.assert_string('(' + self.fact_type + ' "' + message + '")')
            else:
                self.env.assert_string('(' + self.fact_type + ' ' + message + ')')
        self.env.run()

#Server infrastructure
class MyServerProtocol(WebSocketServerProtocol):
    connections = list()
    last_message = None

    def onConnect(self, request):
        self.connections.append(self)
        print("Client connecting: {0}".format(request.peer))

    #Sends the last message to the frontend when connection is opened
    def onOpen(self):
        print("WebSocket connection open.")
        payload_dictionary = json.dumps({"type":"init", "functions":dictionary}, ensure_ascii = False).encode('utf8')
        self.sendMessage(payload_dictionary)
        if self.last_message != None:
            payload_last_message = json.dumps(self.last_message, ensure_ascii = False).encode('utf8')
            self.sendMessage(payload_last_message)

    #Calls the clips connector when new message from frontend arrives
    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            message = payload.decode('utf8')
            print("Text message received: {0}".format(payload.decode('utf8')))
            self.factory.ruleEnvironment.message_to_clips(json.loads(message)['answer']) # pylint: disable=no-member     

    def onClose(self, wasClean, code, reason):
        self.connections.remove(self)
        print("WebSocket connection closed: {0}".format(reason))

    #only for calls from outside MyServerProtocol class
    @classmethod
    def broadcast_message(cls, data):
        cls.last_message = data
        payload = json.dumps(data, ensure_ascii = False).encode('utf8')
        for c in set(cls.connections):
            reactor.callFromThread(cls.sendMessage, c, payload) # pylint: disable=no-member

#Server infrastructure
class MyServerFactory(WebSocketServerFactory):

    protocol = None

    def __init__(self, url, ruleEnvironment):
        WebSocketServerFactory.__init__(self, url)
        self.ruleEnvironment = ruleEnvironment

###RUN###

#Data
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

#Model

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

r = ruleEnvironment(m)
r.initEnvironment()
r.registerCommand(featureImportance)
r.registerCommand(getNthLargest)
r.registerCommand(getFeatureValue)
r.registerCommand(addition)

log.startLogging(sys.stdout)
factory = MyServerFactory(u"ws://127.0.0.1:9000", r)
factory.protocol = MyServerProtocol
reactor.listenTCP(9000, factory)# pylint: disable=no-member
reactor.run()# pylint: disable=no-member
