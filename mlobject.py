import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_graphviz
import json
from alibi.explainers import AnchorTabular
from ceteris_paribus.profiles import individual_variable_profile
from ceteris_paribus.explainer import explain
import imgkit
from alibi.explainers import CounterFactualProto
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
import matplotlib
import matplotlib.pyplot as plt
from pandas.plotting import table
import os
import re
import networkx as nx
from networkx.drawing import nx_agraph
import pygraphviz
import shap
from graphviz import Source

#target must be "class" and all the data must be factorized
class mlObject:
    def __init__(self, X_train, X_test, Y_train, Y_test, featureNames, dictionary, model):
        self.X_train = X_train
        self.X_test = X_test
        self.Y_train = Y_train
        self.Y_test = Y_test
        self.featureNames = featureNames
        self.dictionary = dictionary
        self.model = model
        self.surrogate_dt = None
        self.explanation = None
        self.certainty = None

    #resets the certainty value to None
    def resetCertainty(self):
        self.certainty = None

    #returns the certainty value
    def getCertainty(self):
        return(self.certainty)
    
    #returns the explanation value
    def getExplanation(self):
        return(self.explanation)

    #receives a data instance and returns a prediction label
    def predict_connector(self, *arg):
        #print(arg)
        query_instance = dict(s.split(':') for s in arg)
        prediction_proba = self.model.predict_proba(pd.DataFrame([query_instance]))[0]
        prediction = np.where(prediction_proba == np.amax(prediction_proba))[0][0]
        print(prediction)
        self.certainty = "The probability for this particular instance for <big>" + str(self.dictionary["class"]["values"][prediction]) + "</big> is " + str(round(prediction_proba[prediction],2)) + "."
        return(self.dictionary["class"]["values"][prediction])

    #runs anchors algorithm and returns a rule explanation
    def anchors_connector(self, *arg):
        query_instance = dict(s.split(':') for s in arg)
        
        #anchor instance to model instance. Input: Numpy. Output: Pandas df. Turns numbers into categories.
        def adapter(n):
            d = pd.DataFrame(data=n, columns = self.featureNames)
            categories = self.getCategoricalFeatures()
            for c in categories:
                d[c] = d[c].map(self.dictionary[c]["values"])
            #d['Sex'] = d['Sex'].map({0:'Male', 1: 'Female'})
            #d['Embarked'] = d['Embarked'].map({0: 'Southampton', 1: 'Cherbourg', 2: 'Queenstown'})
            #d['Pclass'] = d['Pclass'].map({0: 'First', 1: 'Second', 2: 'Third'})
            return d
        
        #model instance to anchor instance. Input: Pandas df. Output: Numpy. Turns categories into numbers.
        def reverse_adapter(p):
            d = p.copy()
            categories = self.getCategoricalFeatures()
            for c in categories:
                d[c] = d[c].map({v: k for k, v in self.dictionary[c]["values"].items()})
            #d['Sex'] = d['Sex'].map({'Male': 0, 'Female': 1})
            #d['Embarked'] = d['Embarked'].map({'Southampton': 0, 'Cherbourg': 1, 'Queenstown': 2})
            #d['Pclass'] = d['Pclass'].map({'First': 0, 'Second': 1, 'Third': 2})
            n = d.to_numpy().astype(np.float)
            return(n)

        
        predict_fn = lambda x: self.model.predict(adapter(x))

        #create the category map
        categories = self.getCategoricalFeatures()
        category_map = {}
        for i in range(len(self.featureNames)):
            if self.featureNames[i] in categories:
                category_map[i] = [str(k) for k in list(self.dictionary[self.featureNames[i]]["values"].values())]
        #category_map = {0: ['First', 'Second', 'Third'], 1: ['Male','Female'], 4: ['Southampton', 'Cherbourg', 'Queenstown']}

        print("-------")
        print(query_instance)
        print(reverse_adapter(pd.DataFrame([query_instance])))

        #sort query_instance
        sorted_query_instance = {}
        for f in self.featureNames:
            sorted_query_instance[f] = query_instance[f]

        print(sorted_query_instance)
        print(reverse_adapter(pd.DataFrame([sorted_query_instance])))

        explainer = AnchorTabular(predict_fn, feature_names = self.featureNames, categorical_names = category_map)
        anchor_training = reverse_adapter(self.X_train)
        explainer.fit(anchor_training, disc_perc=[25, 50, 75])
        explanation = explainer.explain(reverse_adapter(pd.DataFrame([sorted_query_instance])), threshold=0.90, max_anchor_size=3, batch_size=2000)
        print('Anchor: %s' % (' AND '.join(explanation['data']['anchor'])))
        print('Precision: %.2f' % explanation['precision'])
        print('Coverage: %.2f' % explanation['coverage'])

        #build rule
        rule = ""
        names = explanation['data']['anchor']
        precision = np.asarray(explanation['raw']['precision'])
        precision[1:] -= precision[:-1].copy()
        precision = [ round(elem, 2) for elem in precision.tolist() ] 
        for i in range(0, len(names)):
            rule = rule + names[i]
            #importance = round(precision[i]/sum(precision)*100,2)

            #rule = rule + " (" + str(importance) + "%)"
            if (i < len(names)-1):
                rule = rule + " AND "

        self.explanation = 'I generated the following rule for you. It describes the boundaries under which the current prediction remains stable: <br> <br> <big>' + rule + '</big>. <br> <br> Each rule condition has an importance score which shows how critical the condition is for the prediction outcome to stay stable.'
        self.certainty = 'I tested the rule on many sample data instances. The condition applies on %.2f' % explanation['coverage'] + ' of the instances. In these cases, the rule was accurate in %.2f' % explanation['precision'] + ' of the cases.'
        return(True)

    #generates dt visualization
    def getSurrogateVisualization(self):

        self.certainty = "You can see how the tree performed on sample data when looking at the square brackets of each node."

        if not os.path.exists("temp/head.jpg"):
            if self.surrogate_dt is None:
                self.buildSurrogateDecisiontree()
            
            dot_data = export_graphviz(self.surrogate_dt, out_file=None, 
                                    feature_names=self.featureNames,  
                                    impurity=False,
                                    label='none',
                                    filled=True,
                                    rotate=True,
                                    class_names=["died","survived"])
            
            def categorize_dot(dot):
                new_dot = dot
                feature_list = self.getCategoricalFeatures()
                print(new_dot)

                for fe in feature_list: 
                    m = re.findall('label="'+ fe +'(.+?)\\\\n', new_dot)
                    print(m)
                    if m != []:
                        for k in m:
                            if '<=' in m[0]:
                                number = float(re.findall("\\d+\\.\\d+", k)[0])
                                instances = dict(filter(lambda elem: elem[0] <= number, self.dictionary[fe]["values"].items()))
                                print(number)
                                print(instances)
                            else: 
                                number = float(re.findall("\\d+\\.\\d+", k)[0])
                                instances = dict(filter(lambda elem: elem[0] > number, self.dictionary[fe]["values"].items()))
                                print(number)
                                print(instances)
                            print(list(instances.values()))
                            new_dot = new_dot.replace(fe+k, fe+ " in " +str(list(instances.values())))
                        # replace fe+k by fe+instances.values()
                return(new_dot)

            c = categorize_dot(dot_data)
            path = "temp/tree.png"
            s = Source(c, filename="temp/tree", format="png")
            s.render()
            #p.write_png("temp/tree.png")
            return(path)
        else:
            return(path)

    #returns the kth surrogate rule for a specified target
    def getSurrogateRule(self, target, kth):
        target_key = self.getKey("class", target)
        
        if self.surrogate_dt is None:
            self.buildSurrogateDecisiontree()
        
        def tree_to_rules(tree, feature_names):
            left = tree.tree_.children_left
            right = tree.tree_.children_right
            threshold = tree.tree_.threshold
            features = [feature_names[i] for i in tree.tree_.feature]
            value = tree.tree_.value
            global rules 
            rules = []

            def recurse(left, right, threshold, features, node, depth=0, k = []):
                if (threshold[node] != -2):
                    if(left[node] != -1):
                        z = k.copy() 
                        if(self.dictionary[features[node]]["feature-type"] == "categorical"):
                            instances = dict(filter(lambda elem: elem[0] <= threshold[node], self.dictionary[features[node]]["values"].items()))
                            c = []  
                            c.append(str(features[node]))
                            c.append("in")
                            c.append(list(instances.values()))
                            z.append(c)
                        else:
                            c = []
                            c.append(str(features[node]))
                            c.append("<=")
                            c.append(str(threshold[node]))
                            z.append(c)
                        recurse(left, right, threshold, features, left[node], depth+1, z)   
                    if(right[node] != -1):
                        z = k.copy() 
                        if(self.dictionary[features[node]]["feature-type"] == "categorical"):
                            instances = dict(filter(lambda elem: elem[0] > threshold[node], self.dictionary[features[node]]["values"].items()))
                            c = []
                            c.append(str(features[node]))
                            c.append("in")
                            c.append(list(instances.values()))
                            z.append(c)
                        else:
                            c = []
                            c.append(str(features[node]))
                            c.append(">")
                            c.append(str(threshold[node]))
                            z.append(c)
                        recurse(left, right, threshold, features, right[node], depth+1, z)
                else:
                    rules.append((k, value[node]))
            
            recurse(left, right, threshold, features, node = 0)
            return(rules)
        
        def getSortedRules(rules):
            def getScore(rule):
                bigger = [i for i, j in enumerate(rule[1][0]) if j == max(rule[1][0])]
                return((rule[1][0][bigger])/(sum(rule[1][0])+1))
            return(sorted(rules, key=getScore)[::-1])

        def getKthTargetRule(rules, target, k):
            counter = 1
            for r in rules:
                rule_target = [i for i, j in enumerate(r[1][0]) if j == max(r[1][0])][0]
                if counter == k and target == rule_target:
                    return r
                elif counter != k and target == rule_target:
                    counter = counter + 1
            return None

        def getPrettyRule(rule):
            string = ""
            for r in rule:
                if string != "":
                    string = string + " AND "
                if type(r[2]) == list:
                    string = string +  r[0] + " " + r[1] + " " +  "( " + ', '.join(r[2]) + " )"
                else:
                    string = string + r[0] + " " + r[1] + " " + r[2]
            return(string)
        
        rules = tree_to_rules(self.surrogate_dt,self.featureNames)
        sorted_rules = getSortedRules(rules)
        #print(sorted_rules)

        target_rule = getKthTargetRule(sorted_rules, target_key, kth)
        
        if target_rule is not None:
            self.certainty = "Among " + str(int(np.sum(target_rule[1][0]))) + " sample data instances that are covered by this rule, there was a split of " + ' / '.join(map(str,map(int, (target_rule[1]).tolist()[0]))) + " between the potential classes for this particular rule."
            return (getPrettyRule(target_rule[0]))
        else:
            return None

    #builds a surrogate decision tree
    def buildSurrogateDecisiontree(self):

        y_prediction = self.model.predict(self.X_train)
        
        def reverse_adapter(p):
            d = p.copy()
            categories = self.getCategoricalFeatures()
            for c in categories:
                d[c] = d[c].map({v: k for k, v in self.dictionary[c]["values"].items()})
            #d['Sex'] = d['Sex'].map({'Male': 0, 'Female': 1})
            #d['Embarked'] = d['Embarked'].map({'Southampton': 0, 'Cherbourg': 1, 'Queenstown': 2})
            #d['Pclass'] = d['Pclass'].map({'First': 0, 'Second': 1, 'Third': 2})
            n = d.to_numpy().astype(np.float)
            return(n)
        
        tree_train = reverse_adapter(self.X_train)

        self.surrogate_dt = DecisionTreeClassifier(max_depth = 3)
        self.surrogate_dt.fit(tree_train, y_prediction)
        
        return True 

    #computes ceterisParibus plot   
    def ceterisParibus_connector(self, feature, *arg):
        from ceteris_paribus.plots.plots import plot

        query_instance = dict(s.split(':') for s in arg)

        #print(feature)

        #prepare data instance (nparray)
        categories = self.getCategoricalFeatures()
        np_instance = []
        for f in self.featureNames:
            if f in categories:
                np_instance.append(query_instance[f])
            else:
                np_instance.append(float(query_instance[f]))
        #print(np_instance)

        prediction_proba = self.model.predict_proba(pd.DataFrame([query_instance]))[0]
        prediction = np.where(prediction_proba == np.amax(prediction_proba))[0][0]
        #print(prediction)

        explainer = explain(self.model, variable_names=self.featureNames, data=self.X_train, y=self.Y_train, label='Model', predict_function=lambda x: self.model.predict_proba(x)[::, 1])

        i = individual_variable_profile(explainer, np.array(np_instance), np.array([prediction]))

        p = plot(i, selected_variables=[feature], width=700, height=800, size=4)

        options = {
            'height' : '500',
            'width' : '600'
        }

        imgkit.from_file('_plot_files/plots' + p + '.html', 'temp/plots' + p + '.jpg', options=options)

        self.certainty = "I am 100 percent sure about the graph."
        return("temp/plots" + str(p) + ".jpg")

    #counterfactual explanations for how-type
    def cf_proto_how_connector(self, target, *arg):
        target_key = self.getKey("class", target)
        query_instance = dict(s.split(':') for s in arg)
        categories = self.getCategoricalFeatures()
        continuous = self.getContinuousFeatures()
        for f in self.featureNames:
            if f in continuous:
                query_instance[f] =  float(query_instance[f])
        

        new_instance = self.cf_proto_connector(target_key, query_instance)

        if new_instance is not None:

            difference = ""
            for f in self.featureNames:
                if f in categories:
                    if new_instance[f] != query_instance[f]:
                        difference = difference + f + ": " + query_instance[f] + " -> " + new_instance[f] + " <br> "
                elif f in continuous:
                    if ((new_instance[f] - query_instance[f]) != 0):
                        difference = difference + f + ": " + str(query_instance[f]) + " -> " + str(new_instance[f]) + " <br> "
                
            print(new_instance)
            print(difference)
            self.certainty = "I am pretty sure about that. You can try it out. Type 'what if'."
            return(difference)

        else:
            self.certainty = None
            print("Not found")
            return(None)

    #counterfactual explanations for why-type
    def cf_proto_why_connector(self, target, *arg):
        target_key = self.getKey("class", target)
        query_instance = dict(s.split(':') for s in arg)
        categories = self.getCategoricalFeatures()
        continuous = self.getContinuousFeatures()
        for f in self.featureNames:
            if f in continuous:
                query_instance[f] =  float(query_instance[f])
        

        new_instance = self.cf_proto_connector(target_key, query_instance)

        if new_instance is not None:

            difference = "There is sufficient evidence that the following features contributed heavily to the prediction: "
            temp = []
            for f in self.featureNames:
                if f in categories:
                    if new_instance[f] != query_instance[f]:
                        difference = (difference + " " + f + " ")
                        temp.append(str(" ( " + f + ": " + query_instance[f] + " -> " + new_instance[f] + " ) <br>"))
                elif f in continuous:
                    if ((new_instance[f] - query_instance[f]) != 0):
                        difference = (difference + " " + f + " ")
                        temp.append(str(" ( " + f + ": " + str(query_instance[f]) + " -> " + str(new_instance[f]) + " ) <br>"))
            difference = difference + ". <br> Try to apply the following changes and the prediction outcome will switch: <br>"
            for t in temp:
                difference = difference + t + "<br>"
                
            print(new_instance)
            print(difference)
            self.certainty = "I am pretty sure about that. You can try it out. Type 'what if'."
            return(difference)

        else:
            self.certainty = None
            print("Not found")
            return(None)

    #generates shap values for a data instance
    def shap_why_connector(self, target, *arg):
        #Input: Numpy. Output: Pandas df. Turns numbers into categories.
        def adapter(n):
            d = pd.DataFrame(data=n, columns = self.featureNames)
            categories = self.getCategoricalFeatures()
            for c in categories:
                d[c] = d[c].map(self.dictionary[c]["values"])
            #d['Sex'] = d['Sex'].map({0:'Male', 1: 'Female'})
            #d['Embarked'] = d['Embarked'].map({0: 'Southampton', 1: 'Cherbourg', 2: 'Queenstown'})
            #d['Pclass'] = d['Pclass'].map({0: 'First', 1: 'Second', 2: 'Third'})
            return d
        
        #Input: Pandas df. Output: Numpy. Turns categories into numbers.
        def reverse_adapter(p):
            d = p.copy()
            categories = self.getCategoricalFeatures()
            for c in categories:
                d[c] = d[c].map({v: k for k, v in self.dictionary[c]["values"].items()})
            #d['Sex'] = d['Sex'].map({'Male': 0, 'Female': 1})
            #d['Embarked'] = d['Embarked'].map({'Southampton': 0, 'Cherbourg': 1, 'Queenstown': 2})
            #d['Pclass'] = d['Pclass'].map({'First': 0, 'Second': 1, 'Third': 2})
            return(d)        

        query_instance = dict(s.split(':') for s in arg) 

        sorted_query_instance = {}
        for f in self.featureNames:
            sorted_query_instance[f] = query_instance[f]
        
        original_instance = pd.DataFrame([sorted_query_instance])
        print(original_instance.iloc[0,:])
        shap_instance = reverse_adapter(pd.DataFrame([sorted_query_instance]))
        print(shap_instance.iloc[0,:])
        shap_training = reverse_adapter(self.X_train)
        predict_fn = lambda x: self.model.predict_proba(adapter(x))

        shap.initjs()
        explainer = shap.KernelExplainer(predict_fn, shap_training, link='logit')
        single_shap = explainer.shap_values(shap_instance.iloc[0,:].astype("int64"), nsamples=100)
        print(single_shap)

        fig = shap.force_plot(explainer.expected_value[0], single_shap[0], original_instance, out_names=["Chance of died","survived"], link="logit", matplotlib = True, show=False, text_rotation=90)
        fig.savefig('temp/shap.png', bbox_inches = "tight")

        first_target = self.dictionary["class"]["values"][0]
        self.explanation = "The plot shows what feature values influenced the prediction to become <big>" + str(target) + "</big>." + " Particularly, the plot shows the forces that affect the decision to predict " + first_target +". Red forces increase the chance of " + first_target +". Blue forces decrease the chance of " + first_target +". The forces push the average chance of " + first_target + " (base value) up or down. The boundary where the prediction outcome switches is 0.5."
        self.certainty = "That is hard to tell. The computation is based on perturbation with " + str(self.X_train.shape[0]) + " data samples."
        plt.clf()
        return(str('temp/shap.png'))
    
    #computes counterfactual explanation
    def cf_proto_connector(self, target, query_instance):
      
        predict_fn = lambda x: self.model['classifier'].predict_proba(x)

        preprocessed_instance = self.model['preprocessor'].transform(pd.DataFrame([query_instance]))

        categories = self.getCategoricalFeatures()
        continuous = self.getContinuousFeatures()
        print(categories)
        print(continuous)

        new_instance = {}

        cat_vars = {}
        start = len(continuous) #number of continuous features
        for f in categories:
            numbers_features = len(np.unique(self.X_train[f]))
            cat_vars[start] = numbers_features
            start = start + numbers_features

        transformed_training = self.model['preprocessor'].transform(self.X_train)

        cf = CounterFactualProto(predict_fn,
                         shape=np.shape(preprocessed_instance),
                         beta=0.1,
                         cat_vars=cat_vars,
                         ohe=True,
                         max_iterations=2000,
                         feature_range= (np.zeros((1,len(self.featureNames))), np.ones((1,len(self.featureNames)))),
                         #feature_range= (np.array([[-1, -1, -1, -1, -1, -1]]), np.array([[1, 1, 1, 1, 1, 1]])),
                         c_init=1.,
                         c_steps=5,
                         eps=(.1, .1)  # perturbation size for numerical gradients
                        )
        
        cf.fit(transformed_training, d_type='abdm', disc_perc=[25, 50, 75])

        explanation = cf.explain(X=preprocessed_instance, target_class=[target])

        if explanation['cf'] != None:

            one_hot_training = self.X_train[categories].to_numpy()
            one = OneHotEncoder(handle_unknown='ignore')
            one.fit(one_hot_training)
            inverse_one_hot = one.inverse_transform([explanation['cf']['X'][0][len(categories):]])

            scaler_training = self.X_train[continuous].to_numpy()
            scaler = MinMaxScaler()
            scaler.fit(scaler_training)
            inverse_scale = scaler.inverse_transform([explanation['cf']['X'][0][0:len(continuous)]])

            for i in range(len(categories)):
                new_instance[categories[i]] = inverse_one_hot[0][i]

            for i in range(len(continuous)):
                new_instance[continuous[i]] = round(inverse_scale[0][i],2)

            return new_instance
        else:
            return None

    #computes visualization of sample data
    def getDataPreview(self):

        def createSampleDataImg():
            data = self.X_train.sample(n=20)
 
            css = """
                <style type=\"text/css\">
                table {
                color: #333;
                font-family: Helvetica, Arial, sans-serif;
                width: 640px;
                border-collapse:
                collapse; 
                border-spacing: 0;
                }
                td, th {
                border: 1px solid transparent; /* No more visible border */
                height: 30px;
                }
                th {
                background: #DFDFDF; /* Darken header a bit */
                font-weight: bold;
                }
                td {
                background: #FAFAFA;
                text-align: center;
                }
                table tr:nth-child(odd) td{
                background-color: white;
                }
                </style>
                """

            text_file = open("temp/head.html", "a")
            # write the CSS
            text_file.write(css)
            # write the HTML-ized Pandas DataFrame
            text_file.write(data.to_html())
            text_file.close()

            imgkitoptions = {"format": "jpg", 'width' : '600'}
            imgkit.from_file("temp/head.html", "temp/head.jpg", options=imgkitoptions)

            return("temp/head.jpg")

        self.certainty = None

        if not os.path.exists("temp/head.jpg"):
            return (createSampleDataImg())
        else: 
            os.remove("temp/head.jpg")
            os.remove("temp/head.html")
            return (createSampleDataImg())

    #returns the categorial features as array        
    def getCategoricalFeatures(self):
        features = []
        for f in self.featureNames:
                if self.dictionary[f]["feature-type"] == "categorical" and f != "class":
                    features.append(f)
        return features

    #return the continuous features as array
    def getContinuousFeatures(self):
        features = []
        for f in self.featureNames:
                if self.dictionary[f]["feature-type"] == "continuous" and f != "class":
                    features.append(f)
        return features

    #helper: returns key of dictionary
    def getKey(self, feature, target):
        for i in self.dictionary[feature]["values"]:
            if self.dictionary[feature]["values"][i] == target:
                return(i)
    

    