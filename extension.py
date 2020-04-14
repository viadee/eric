#Extension object that generates dialogue rules automatically
class ERICExtension:
    def __init__(self, name, keywords, display, write, description, output_type, arguments, function):
        self.name = name
        self.keywords = keywords
        self.display = display
        self.write = write
        self.description = description
        self.output_type = output_type #text or image
        self.arguments = arguments #dict: {x: Integer, y: Integer}. Can be Integer, Feature, Target, Prediction
        self.function = function

    def valid_answers_dict(self, argument):
        switcher = {
            "Integer": """ "{'type' : 'regex', 'value' : '(\\\\d+)'}" """,
            "Feature": "(get-valid-answers-for-features)",
            "Target": "(get-valid-answers-for-target)"
        }
        return switcher.get(argument)
    
    def generateRules(self):

        rules =[]
        prediction_value = False

        #extract prediction argument
        if "Prediction" in self.arguments.values():
            def getKey(target):
                for i in self.arguments:
                    if self.arguments[i] == target:
                        return(i)
            del self.arguments[getKey("Prediction")]
            prediction_value = True

        #add prediction value available check
        if prediction_value:
            available_check = """(defrule {name}-no-prediction
                    (declare (salience 100))
                    ?w <- (input ui {name})
                    (list (name predictions) (content nil))
                    =>
                    (retract ?w)
                    (assert (ui-state (text "You should make a prediction first. Type 'prediction' into the message field.")
                                        (valid-answers "''")
                                        (clips-type "''")
                                        (clipboard "''")
                                        (fact-type "input ui"))))""".format(name=self.name)
            rules.append(available_check)

        #if there are arguments
        if len(self.arguments) > 0:

            initializer = " ".join(["""(assert({} require {}))""".format(self.name, i) for i in list(self.arguments.keys())[::-1]])     

            entry = """(defrule {name}
                            ?o <- (input ui {name})
                            =>
                            (retract ?o)
                            {initializer}
                        )""".format(name=self.name, initializer=initializer)
            
            rules.append(entry)

            for i in self.arguments.keys():
    
                valid = self.valid_answers_dict(self.arguments[i])

                require =  """(defrule {name}-{parameter_name}
                                        ?a <- ({name} require {parameter_name})
                                        => 
                                        (retract ?a)
                                        (assert (ui-state (text (str-cat "Please provide some value for {parameter_name}."))
                                                                (valid-answers {valid})
                                                                (clips-type "''")
                                                                (clipboard "''")
                                                                (fact-type (str-cat "{name} user-value {parameter_name}"))))
                                        )""".format(name=self.name, parameter_name=i, valid=valid)
                rules.append(require)
            
            arguments = " ".join(["""?{}f <- ({} user-value {} ?{})""".format(i, self.name, i, i) for i in list(self.arguments.keys())])
            single_arguments = " ".join(["?{}".format(i) for i in list(self.arguments.keys())])                

            if prediction_value:
                bind = """  (bind ?f (fact-slot-value ?head features))
                            (bind ?prediction-values (transform-feature-values ?f))
                            (bind ?r ({name} {single_arguments} ?prediction-values))""".format(name=self.name, single_arguments=single_arguments)
                arguments = arguments + """ (list (name predictions) (content ?head $?tail)) (test(neq nil ?head))"""
            else:
                bind = """(bind ?r ({name} {single_arguments}))""".format(name=self.name, single_arguments=single_arguments)
            retract = " ".join(["(retract ?{}f)".format(i) for i in list(self.arguments.keys())])

            if self.output_type == "text":
                complete = """(defrule {name}-complete
                            {arguments}
                            =>
                            {retract}
                            {bind}
                            (assert (ui-state (text (str-cat "The answer is: " ?r))
                                            (valid-answers "''")
                                            (clips-type "''")
                                            (clipboard "''")
                                            (fact-type "input ui"))))""".format(name=self.name, arguments=arguments, parameter_name=i, valid=valid, bind=bind, retract=retract)
            elif self.output_type == "image":
                complete = """(defrule {name}-complete
                                            {arguments}
                                            =>
                                            {retract}
                                            {bind}
                                            (assert (ui-state (text (str-cat "Look what I created for you."))
                                                            (image-url ?r)
                                                            (valid-answers "''")
                                                            (clips-type "''")
                                                            (clipboard "''")
                                                            (fact-type "input ui"))))""".format(name=self.name, arguments=arguments, parameter_name=i, valid=valid, bind=bind, retract=retract)

            rules.append(complete)
        #if there are no arguments
        else:
            if prediction_value:
                bind = """  (bind ?f (fact-slot-value ?head features))
                            (bind ?prediction-values (transform-feature-values ?f))
                            (bind ?r ({name} ?prediction-values))""".format(name=self.name)
                condition = """ ?o <- (input ui {name})
                                (list (name predictions) (content ?head $?tail))
                                (test(neq nil ?head))""".format(name=self.name)

            else:
                bind = """(bind ?r ({name}))""".format(name=self.name)
                condition = """?o <- (input ui {name})""".format(name=self.name)
                

            if self.output_type == "text":
                complete = """(defrule {name}-complete
                            {condition}
                            =>
                            (retract ?o)
                            {bind}
                            (assert (ui-state (text (str-cat "The answer is: " ?r))
                                            (valid-answers "''")
                                            (clips-type "''")
                                            (clipboard "''")
                                            (fact-type "input ui"))))""".format(name=self.name, bind=bind, condition=condition)
            elif self.output_type == "image":
                complete = """(defrule {name}-complete
                            {condition}
                            =>
                            (retract ?o)
                            {bind}
                            (assert (ui-state (text (str-cat "Look what I created for you."))
                                            (image-url ?r)
                                            (valid-answers "''")
                                            (clips-type "''")
                                            (clipboard "''")
                                            (fact-type "input ui"))))""".format(name=self.name, bind=bind, condition=condition)
            rules.append(complete)
        return rules

#Examples of extensions
def getFeatureImportance(self):
    import pandas as pd
    import shap
    import matplotlib.pyplot as plt
    import numpy as np
    import os

    self.certainty = "The computation is based on perturbation with " + str(self.X_train.shape[0]) + " data samples."

    if not os.path.exists('temp/imp.png'):

        def adapter(n):
            d = pd.DataFrame(data=n, columns = self.featureNames)
            categories = self.getCategoricalFeatures()
            for c in categories:
                d[c] = d[c].map(self.dictionary[c]["values"])
            return d
            
            #Input: Pandas df. Output: Numpy. Turns categories into numbers.
        def reverse_adapter(p):
            d = p.copy()
            categories = self.getCategoricalFeatures()
            for c in categories:
                d[c] = d[c].map({v: k for k, v in self.dictionary[c]["values"].items()})
            return(d)  

        shap_training = reverse_adapter(self.X_train)
        shap_test = reverse_adapter(self.X_test)

        predict_fn = lambda x: self.model.predict_proba(adapter(x))

        # use Kernel SHAP to explain test set predictions
        explainer = shap.KernelExplainer(predict_fn, shap_training, link='logit')

        shap_values = explainer.shap_values(shap_test, nsamples=100)

        k = []
        for i in list(self.dictionary["class"]["values"].keys()):
            if len(k) > 0:
                k = k + (np.mean(np.absolute(shap_values[i]),axis=0))
            else:
                k = (np.mean(np.absolute(shap_values[i]),axis=0))

        percentage = []
        for p in k:
            percentage.append(round(p/sum(k),2)*100)

        objects = self.featureNames
        y_pos = np.arange(len(objects))
        performance = percentage

        plt.barh(y_pos, performance, align='center', alpha=0.5, color="#0084FF")
        plt.yticks(y_pos, objects)
        plt.xlabel('Relative importance in %')
        plt.savefig('temp/imp.png', transparent=False, bbox_inches = "tight")
        plt.clf()
        return('temp/imp.png')
    else:
        return('temp/imp.png')

featureImportance = ERICExtension(
                            name = "getImportance", 
                            keywords = "how important importance influence impact",
                            display = "How important are the features?",
                            write = "How important are the features?",
                            description = "This command calculates the overall feature importance.",
                            output_type = "image", 
                            arguments = {}, 
                            function = getFeatureImportance)

def nthLargest(self, feature, nth, *arg):
    import pandas
    if feature in self.getContinuousFeatures():
        unique_values = self.X_train[feature].unique()
        unique_values.sort()
        return(str(unique_values[-1*nth]))
    else:
        return("NLargest cannot be calculated for categorical features.")

getNthLargest = ERICExtension(
    name = "getNLargest", 
    keywords = "nth largest large get",
    display = "What is the nth-largest value?",
    write = "What is the nth-largest value of feature Z?",
    description = "This command computes the nth-largest value for a given column.",
    output_type = "text", 
    arguments = {"feature": "Feature", "nth": "Integer"}, 
    function = nthLargest)

def getFeatureValue(self, feature, *y):
    query_instance = dict(s.split(':') for s in y)
    print(query_instance)
    return(str(query_instance[feature]))

getFeatureValue = ERICExtension(
    name = "getFeatureValue", 
    keywords = "get feature value",
    display = "What is the feature value of X?",
    write = "What is the feature value of X?",
    description = "Returns the feature value of feature X.",
    output_type = "text", 
    arguments = {"X": "Feature", "y": "Prediction"}, 
    function = getFeatureValue)    

def addition(self, x, y):
    return(str(x+y))

addition = ERICExtension(
    name = "addition", 
    keywords = "add addition",
    display = "Add x and y.",
    write = "Add x and y.",
    description = "This command adds two numbers.",
    output_type = "text", 
    arguments = {"x": "Integer", "y": "Integer"}, 
    function = addition)  

