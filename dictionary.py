#Punctuation in the key_sentences usually gets removed in preprocessing
cd = "#" #do not use ":" as it is already used by depparse for splitting passive/active deprel differentiation
reserved_placeholder_words = ["<outcome>", "<key>", "<value>", "<subject>"]

'''
Notes to self for enhancing the depparsing:
    mark optional tuples (as of now, i commented them out)
    make deprel "don't care" possible
    mark templates that have to match completely with no left over nodes in the input
    function "init" may work best without depparse or a modified version of it, as greetings can take virtually any form
    possibility to refer to previous tuple
    possibility to ignore root
    match usr_input directly to fuction id
overall notes:
    alternative words for "prediction" depending on model. search this file for the following comment: "#["person", "prediction"] would be ideal, but only for the titanic model"
'''
dictionary = [
    {   
        "id" : "predict",
        "keywords" : "predict predictions classify classifications",
        "key_sentences": [
            "Make a prediction for the current instance",
            "Make a prediction for the current data",
            "Can you please make me a prediction?", 
            "Make me a prediction", 
            "Make prediction",
            "prediction",
            "Can you predict something for me?",
            "predict for current instance",
            "predict for current data",
            "predict"
        ],
        "depparse": [
            [#0
                ("root", "root", "what"),
                ("what", "nsubj", "outcome"),
                ("outcome", "amod", ["predicted", "current"])
            ],
            [#1
                ("root", "root", "predict"),
                ("predict", "obj", "outcome")
            ],
            [#2
                ("root", "root", "predict"),
                ("predict", "obl", ["data", "person"])
            ],
            [#3
                ("root", "root", "predicted"),
                ("predicted", "nsubj:pass", f"upos{cd}NOUN")
            ],
            [#4
                ("root", "root", "predict"),
                ("predict", "obj", "something"),
                ("something", "nmod", f"upos{cd}PRON")#,
                #(f"upos{category_delimiter}PRON", "case", "for")
            ],
            [#5
                ("root", "root", "make"),
                ("make", "obj", "prediction")
            ],
            [#6
                ("root", "root", "happen"),
                ("happen", "nsubj", "what")
            ],
            [#7
                ("root", "root", "predict")
            ]
        ],
        "display" : "Make me a prediction.",
        "write" : "Can you please make me a prediction?",
        "execute" : "predict",
        "description": "The 'predict' command will allow you to infer a prediction from your data intance. In case you did not provide a data instance yet, ERIC will ask you to provide a value for each feature."
    },
    {
        "id": "whatif",
        "keywords" : "what if change",
        "key_sentences": [ 
            "What if <key> equals <value>?",
            "What happens if <key> equals <value>?",
            "What if you change <key> to <value>?",
            "What happens if you change <key> to <value>?",
            "What if you set <key> to <value>?",
            "What happens if you set <key> to <value>?",
            "What if <key> is changed to <value>?",
            "What happens if <key> is changed to <value>?",
            "What happens if <key> is <value>"
            "Change <key> to <value>",
            "Set <key> to <value>.",
            "Set <key> = <value>",
            "<key> = <value>",
            "set x = y"
        ],
        "depparse": [
            [#0
                ("root", "root", [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], ["obj", "advcl", "acl"], "<key>"),
                ("<key>", ["appos", "nummod", "obl", "obj", "nmod"], "<value>")
            ],
            [#1
                ("root", "root", f"lemma{cd}happen"),
                (f"lemma{cd}happen", ["advcl", "parataxis"], "<value>"),
                (f"lemma{cd}happen", "nsubj", "<key>")
            ],
            [#2
                ("root", "root", "what"),
                ("what", "advcl", [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], ["obj", "nsubj:pass"], "<key>"),
                ([f"lemma{cd}change", f"lemma{cd}set"], "obl", "<value>")
            ],
            [#3
                ("root", "root", "what"),
                ("what", "advcl", "<value>"),
                ("<value>", "nsubj", "<key>")
            ],
            [#4
                ("root", "root", f"lemma{cd}happen"),
                (f"lemma{cd}happen", "advcl", "<key>"),
                (f"lemma{cd}happen", ["advcl", "parataxis"], "<value>")
            ],
            [#5
                ("root", "root", "<key>"),
                ("<key>", "nsubj", [f"lemma{cd}change", f"lemma{cd}set"]),
                ("<key>", "obl", "<value>")
            ],
            [#6
                ("root", "root", [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], "obj", "<value>"),
                ("<value>", ["amod", "compound"], "<key>")
            ],
            [#7
                ("root", "root", f"lemma{cd}happen"),
                (f"lemma{cd}happen", "advcl", "<key>"),
                ("<key>", ["appos", "nummod"], "<value>")
            ],
            [#8
                ("root", "root", "<key>"),
                ("<key>", "punct", f"lemma{cd}="),
                ("<key>", ["parataxis", "appos"], "<value>")
            ],
            [#9
                ("root", "root", "what"),
                ("what", "advcl", "<key>"),
                ("what", "punct", f"lemma{cd}="),
                ("what", "appos", "<value>")
            ],
            [#10
                ("root", "root", [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], "obj", "<key>"),
                ([f"lemma{cd}change", f"lemma{cd}set"], "obl", "<value>")
            ],
            [#11
                ("root", "root", [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], "obj", "<key>"),
                ([f"lemma{cd}change", f"lemma{cd}set"], "punct", f"lemma{cd}="),
                ([f"lemma{cd}change", f"lemma{cd}set"], "parataxis", "<value>")
            ],
            [#12
                ("root", "root", "what"),
                ("what", "nsubj", "<key>"),
                ("<key>", "nummod", "<value>")
            ],
            [#13
                ("root", "root", "what"),
                ("what", "advcl", "<value>"),
                ("<value>", "mark", "if")
            ],
            [#14
                ("root", "root", [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], "obj", [f"upos{cd}NOUN", f"upos{cd}PROPN"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], ["obj", "obl"], [f"upos{cd}NOUN", f"upos{cd}PROPN"]),
                ([f"lemma{cd}change", f"lemma{cd}set", f"upos{cd}NOUN", f"upos{cd}PROPN"], "punct", "=")
            ],
            [#15
                ("root", "root", f"lemma{cd}happen"),
                (f"lemma{cd}happen", "advcl", "<key>"),
                #("<key>", "mark", "if"),
                (f"lemma{cd}happen", "nsubj", "what")
            ],
            [#16
                ("root", "root", "key"),
                ("key", "amod", [f"lemma{cd}change", f"lemma{cd}set"]),
                ("key", "appos", "value")
            ],
            [#17
                ("root", "root", f"upos{cd}NOUN"),
                (f"upos{cd}NOUN", "amod", [f"lemma{cd}change", f"lemma{cd}set"]),
                (f"upos{cd}NOUN", "nmod", f"upos{cd}NOUN")
            ],
            [#18
                ("root", "root", f"lemma{cd}happen"),
                (f"lemma{cd}happen", "nsubj", "what"),
                (f"lemma{cd}happen", "advcl", "<value>"),
                ("<value>", "nsubj", "<key>")
            ],
            [#19
                ("root", "root", [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], "obj", [f"upos{cd}NOUN", f"upos{cd}PROPN"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], "discourse", f"upos{cd}SYM")
            ],
            [
                ("root", "root", [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], "obj", [f"upos{cd}NOUN", f"upos{cd}PROPN"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], ["obj", "obl"], [f"upos{cd}NOUN", f"upos{cd}PROPN"])
            ]
        ],
        "display" : "What if X equals Z?",
        "write" : "What if X equals Z?",
        "execute" : "whatif",
        "description": "The 'what-if' command gives you the opportunity to alter the data instance that ERIC is talking about. There will be a new entry on the clipboard."
    },
    {
        "id": "whatif-gl",
        "keywords" : "what if greater less change",
        "key_sentences": [
            "What if <key> was greater or less?",
            "What if <key> was greater / less?",
            "What if <key> was over or under <value>?",
            "What if <key> was over / under <value>?",
            "What if <key> was higher or lower?",
            "What if <key> was higher / lower?",
            "Change <key> to greater / less <value>",
            "Change <key> to over / under <value>",
            "Change <key> to higher / lower <value>"
        ],
        "depparse": [
            [#0
                ("root", "root", "what"),
                ("what", "advcl", ["lower", "higher", "greater", "more"]),
                (["lower", "higher", "greater", "more", "less"], "nsubj", "<key>"),
                (["lower", "higher", "greater", "more", "less"], "obl", "<value>")#,
                #(["lower", "higher", "greater", "more", "less"], "mark", "if")
            ],
            [#1
                ("root", "root", "what"),
                ("what", "advcl", ["lower", "higher", "greater", "more", "less"]),
                (["lower", "higher", "greater", "more", "less"], "nsubj", "<key>")
            ],
            [#2
                ("root", "root", "what"),
                ("what", ["nsubj", "advcl"], "<value>"),
                ("<value>", "nsubj", "<key>"),
                #("<value>", "mark", "if"),
                ("<value>", ["advmod", "case"], ["less", "over", "under", "below", "above"])
            ],
            [#3
                ("root", "root", ["set", "change"]),
                (["set", "change"], "obj", "<key>"),
                ("<key>", "amod", ["lower", "higher", "over", "under", "below", "above"])
            ],
            [#4
                ("root", "root", "<key>"),
                ("<key>", "appos", "<value>"),
                ("<key>", "punct", [f"lemma{cd}<", f"lemma{cd}>"])
            ],
            [#5
                ("root", "root", [f"lemma{cd}set", f"lemma{cd}change"]),
                ([f"lemma{cd}set", f"lemma{cd}change"], "obj", "<key>"),
                ([f"lemma{cd}set", f"lemma{cd}change"], "obl:tmod", "<value>"),
                ("<value>", "amod", ["higher", "lower", "greater"])
            ],
            [#6
                ("root", "root", [f"lemma{cd}set", f"lemma{cd}change"]),
                ([f"lemma{cd}set", f"lemma{cd}change"], "obj", "<key>"),
                ([f"lemma{cd}set", f"lemma{cd}change"], ["nmod", "obl"], "<value>"),
                ("<value>", "case", ["under", "over", "below", "above"])
            ],
            [#7
                ("root", "root", [f"lemma{cd}set", f"lemma{cd}change", f"lemma{cd}make"]),
                ([f"lemma{cd}set", f"lemma{cd}change", f"lemma{cd}make"], "obj", "<key>"),
                ([f"lemma{cd}set", f"lemma{cd}change", f"lemma{cd}make"], ["obj", "xcomp", "parataxis"], ["lower", "higher", "greater", "less"])
            ],
            [#8
                ("root", "root", "set"),
                ("set", "obj", "<key>"),
                ("<key>", "nmod", "<value>"),
                ("<value>", "case", ["under", "over"])
            ],
            [#9
                ("root", "root", "what"),
                ("what", "advcl", "<key>"),
                #("<key>", "mark", "if"),
                ("<key>", "appos", "<value>"),
                ("<value>", "punct", [f"lemma{cd}<", f"lemma{cd}>"])
            ],
            # [#10 This does not work. I found this in my notes and saw, that i didn't write down the last deprel. I wasn't able to recreate a sentence that matched this tree to correct it
            #     ("root", "root", "how"),
            #     ("how", "nsubj", [f"lemma{cd}change", f"lemma{cd}differ"]),
            #     ([f"lemma{cd}change", f"lemma{cd}differ"], "compound", ["value", "outcome", "result", "class", "prediction"]),
            #     ([f"lemma{cd}change", f"lemma{cd}differ"], "nmod", [f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"]),
            #     ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], "amod", ["lower", "higher", "greater"]),
            #     ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], "", "<key>")
            # ],
            [#11
                ("root", "root", "how"),
                ("how", "nsubj", ["change", "differ"]),
                (["change", "differ"], ["nsubj", "compound"], ["value", "outcome", "result", "class", "prediction"]),
                (["change", "differ"], ["nmod", "obl"], [f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], "nmod", "<key>"),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], "amod", ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#12
                ("root", "root", f"lemma{cd}happen"),
                (f"lemma{cd}value", "nsubj", "what"),
                (f"lemma{cd}value", "advcl", ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#13
                ("root", "root", [f"lemma{cd}predict", f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}predict", f"lemma{cd}change", f"lemma{cd}set"], "obj", f"upos{cd}NOUN"),
                ([f"lemma{cd}predict", f"lemma{cd}change", f"lemma{cd}set"], "obl", ["lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#14
                ("root", "root", f"lemma{cd}predict"),
                (f"lemma{cd}predict", "obj", f"upos{cd}NOUN"),
                (f"lemma{cd}predict", "obl", [f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], "amod", ["lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#15
                ("root", "root", f"lemma{cd}predict"),
                (f"lemma{cd}predict", "obj", f"upos{cd}NOUN"),
                (f"upos{cd}NOUN", "nmod", ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#16
                ("root", "root", "predict"),
                ("predict", "obl", ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#17
                ("root", "root", "predict"),
                ("predict", "obl", [f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], "amod", ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#18
                ("root", "root", ["set", "change"]),
                (["set", "change"], "obj", f"upos{cd}NOUN"),
                (["set", "change"], "obl", [f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], "amod", ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#19
                ("root", "root", ["set", "change"]),
                (["set", "change"], "obl", [f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], "case", f"upos{cd}NOUN"),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], "amod", ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#20
                ("root", "root", "what"),
                ("what", "advcl", [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], "nsubj:pass", f"upos{cd}NOUN"),
                ([f"lemma{cd}change", f"lemma{cd}set"], "obl", [f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], "amod", ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#21
                ("root", "root", "predict"),
                ("predict", "obj", f"upos{cd}NOUN"),
                (f"upos{cd}NOUN", "obl", [f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], "amod", ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#22
                ("root", "root", [f"lemma{cd}change", f"lemma{cd}differ"]),
                ([f"lemma{cd}change", f"lemma{cd}differ"], "advmod", "how"),
                ([f"lemma{cd}change", f"lemma{cd}differ"], "nsubj", ["value", "outcome", "result", "class", "prediction"]),
                ([f"lemma{cd}change", f"lemma{cd}differ"], ["advcl", "obl"], "<value>"),
                ("<value>", "nsubj", "<key>"),
                ("<value>", "advmod", ["below", "above", "under", "over", "less"])
            ],
            [#23
                ("root", "root", [f"lemma{cd}change", f"lemma{cd}differ"]),
                ([f"lemma{cd}change", f"lemma{cd}differ"], "advmod", "how"),
                ([f"lemma{cd}change", f"lemma{cd}differ"], "advcl", ["lower", "higher", "greater", "bigger", "smaller"]),
                ([f"lemma{cd}change", f"lemma{cd}differ"], "nsubj", ["value", "outcome", "result", "class", "prediction"]),
                (["lower", "higher", "greater", "bigger", "smaller"], "nsubj", "<key>"),
                (["lower", "higher", "greater", "bigger", "smaller"], "obl", "<value>")
            ],
            [#24
                ("root", "root", [f"lemma{cd}change", f"lemma{cd}differ"]),
                ([f"lemma{cd}change", f"lemma{cd}differ"], "advmod", "how"),
                ([f"lemma{cd}change", f"lemma{cd}differ"], "nsubj", ["value", "outcome", "result", "class", "prediction"]),
                ([f"lemma{cd}change", f"lemma{cd}differ"], "obl", "<value>"),
                ("<value>", "advmod", "more"),
                ("more", "nsubj", "<key>")
            ],
            [#25
                ([f"lemma{cd}increase", f"lemma{cd}decrease", "lower", "higher", "greater", "bigger", "smaller"], ["obj", "nsubj:pass", "nsubj"], "<key>")
            ],
            [#26
                 ("<key>", ["xcomp", "advmod", "amod", "compound"], [f"lemma{cd}increase", f"lemma{cd}decrease", "lower", "higher", "greater", "bigger", "smaller", "more"])
            ],
            [#27
                ("root", "root", [f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], "compound", [f"lemma{cd}increase", f"lemma{cd}decrease", "lower", "higher", "greater", "bigger", "smaller"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], "nmod", "<key>")
            ]
        ],
        "display" : "What if X was greater/less?",
        "write" : "What if X was greater/less?",
        "execute" : "whatif-gl",
        "description": "The 'what-if-greater-less' command fixes the values of all but one features and pertubates the values of this one feature. A graph will show you how the prediction changes."
    },
    {
        "id": "why",
        "keywords" : "why",
        "key_sentences": [ 
            "Why did you predict <outcome>?",
            "Why did you predict that?",
            "why do you think that?",
            "Why <outcome>?",
            "Why",
            "Explain <outcome>",
            "Explain the prediction",
            "Explain the result.",
            "Explain the outcome",
            "Please give an explanation.",
            "Explanation"
        ],
        "depparse": [
            [#0
                ("root", "root", ["likely", "probable"]),
                (["likely", "probable"], "advmod", "why"),
                (["likely", "probable"], "ccomp", "<outcome>")
            ],
            [#1
                ("root", "root", f"lemma{cd}predict"),
                (f"lemma{cd}predict", "advmod", "why"),
                (f"lemma{cd}predict", ["advcl", "xcomp"], "<outcome>")
            ],
            [#2
                ("root", "root", "<outcome>"),
                ("<outcome>", "advmod", "why"),
                ("<outcome>", "nsubj", f"upos{cd}NOUN")
            ],
            [#3
                ("root", "root", "<outcome>"),
                ("<outcome>", "advmod", "why")
            ],
            [#4
                ("root", "root", ["why", f"lemma{cd}explanation", f"lemma{cd}explain"])
            ]
        ],
        "display" : "Why did you predict X?",
        "write" : "Why did you predict X?",
        "execute" : "why",
        "description": "The 'why' command provides information about why the ERIC predicted a specific output. It will present you an explanation. Afterwards will ask you to provide feedback."
    },
    {
        "id": "why-not",
        "keywords" : "why not",
        "key_sentences": [
            "Why didn't you predict <outcome>?",
            "Why did you not predict <outcome>?",
            "Why not <outcome>?",
        ],
        "depparse": [
            [#0
                ("root", "root", "why"),
                ("why", "nsubj", ["value", "outcome", "result", "class", "prediction"]),
                (["value", "outcome", "result", "class", "prediction"], "advmod", f"lemma{cd}not"),
                (["value", "outcome", "result", "class", "prediction"], "acl", "<outcome>")
            ],
            [#1
                ("root", "root", "<outcome>"),
                ("<outcome>", "advmod", "why"),
                ("<outcome>", "advmod", f"lemma{cd}not")
            ],
            [#2
                ("root", "root", "why"),
                ("why", "advmod", f"lemma{cd}not"),
                ("why", "nsubj", ["value", "outcome", "result", "class", "prediction"]),
                (["value", "outcome", "result", "class", "prediction"], "acl", "<outcome>")
            ],
            [#3
                ("root", "root", "why"),
                ("why", "advmod", f"lemma{cd}not")
            ]
        ],
        "display" : "Why didn't you predict Z?",
        "write" : "Why didn't you predict Z?",
        "execute" : "why-not",
        "description": "The 'why-not' command provides information on why an alternative outcome was not predicted. It will present you an explanation. Afterwards will ask you to provide feedback."
    },
    {
        "id": "how-to",
        "keywords" : "how",
        "key_sentences": [
            "How do I get <outcome>?",
            "What has to change to get <outcome>?"
            "What has to change for <outcome>?"
        ],
        "depparse": [
            [#0
                ("root", "root", f"lemma{cd}have"),
                (f"lemma{cd}have", "nsubj", "what"),
                (f"lemma{cd}have", "xcomp", [f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"]),
                ([f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"], "mark", "to"),
                ([f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"], "ccomp", "<outcome>")
            ],
            [#1
                ("root", "root", [f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"]),
                ([f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"], "advmod", "how"),
                ([f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"], ["obl", "advcl"], "<outcome>")
            ],
            [#2
                ("root", "root", f"lemma{cd}have"),
                (f"lemma{cd}have", "nsubj", "what"),
                (f"lemma{cd}have", "xcomp", [f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"]),
                ([f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"], "mark", "to"),
                ([f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"], "advcl", "get"),
                ("get", "obj", "prediction"), #["person", "prediction"] would be ideal, but only for the titanic model
                ("prediction", "amod", "<outcome>") #["person", "prediction"] would be ideal, but only for the titanic model
            ],
            [#3
                ("root", "root", f"lemma{cd}have"),
                (f"lemma{cd}have", ["nsubj", "obj"], "what"),
                (f"lemma{cd}have", "xcomp", [f"lemma{cd}change", f"lemma{cd}modify", f"lemma{cd}alter", f"lemma{cd}adjust", f"lemma{cd}different"]),
                ([f"lemma{cd}change", f"lemma{cd}modify", f"lemma{cd}alter", f"lemma{cd}adjust", f"lemma{cd}different"], "advcl", "get"),
                ("get", "obj", [f"upos{cd}NOUN", f"upos{cd}PROPN"]),
                ([f"upos{cd}NOUN", f"upos{cd}PROPN"], "amod", "<outcome>")
            ]
        ],
        "display" : "How do I get Y?",
        "write" : "How do I get Y?",
        "execute" : "how-to",
        "description": "The 'how-to' command tells about the changes that must be done to get an alternative prediction outcome."
    },
    {
        "id": "when",
        "keywords" : "when",
        "key_sentences": [
            "When do you predict <outcome>?",
            "When do I get <outcome>?",
            "When is the outcome <outcome>?",
            "When is the result <outcome>?",
            "When is <subject> <outcome>?",
            "When are <subject> <outcome>?"
        ],
        "depparse": [
            [#0
                (f"lemma{cd}have", ["nsubj:pass", "obj"], f"lemma{cd}feature"),
                (f"lemma{cd}feature", "det", f"upos{cd}DET"),
                (f"lemma{cd}feature", "obl", "<outcome>")
            ],
            [#1
                ("root", "root", "when"),
                ("when", "nsubj", ["class", "outcome", "result"]),
                (["class", "outcome", "result"], "acl", "<outcome>"),
                ("<outcome>", "xcomp", ["likely", "probable"])
            ],
            [#2
                ("root", "root", "<outcome>"),
                ("<outcome>", ["mark", "advmod"], "when")
            ],
            [#3
                ("root", "root", ["likely", "probable"]),
                (["likely", "probable"], "advmod", "when"),
                (["likely", "probable"], "ccomp", "<outcome>")
            ],
            [#4
                ("root", "root", f"lemma{cd}need"),
                (f"lemma{cd}need", "obl", "<outcome>"),
                (f"lemma{cd}need", ["obj", "nsubj:pass"], f"lemma{cd}feature"),
                (f"lemma{cd}feature", "det", ["what", "which"])
            ],
            [#5
                ("root", "root", "when"),
                ("when", "appos", "<outcome>")
            ],
            [#6
                ("root", "root", "<outcome>"),
                ("when", ["advmod", "mark"], "when")
            ]
        ],
        "display" : "When do you predict Y?",
        "write" : "When do you predict Y?",
        "execute" : "when",
        "description": "The 'when' command tells you for what feature values the model produces a certain outcome most likely."
    },
    {   
        "id" : "certainty",
        "keywords" : "how certain uncertain are you sure",
        "key_sentences": [
            "How certain are you?",
            "How sure are you?",
            "How certain is the outcome?",
            "How certain is the prediction?",
            "Are you sure?",
            "Are you certain?"
        ],
        "depparse": [
            [#0
                ("root", "root", "what"),
                ("what", "nsubj", ["probability", "certainty", "likelihood"]),
                (["probability", "certainty", "likelihood"], "nmod", ["it", "that", "prediction", "result", "outcome"])
            ],
            [#1
                ("root", "root", ["certain", "likely", "probable"]),
                (["certain", "likely", "probable"], "advmod", "how"),
                (["certain", "likely", "probable"], ["ccomp", "acl:relcl"], "<outcome>")
            ],
            [#2
                ("root", "root", ["certain", "likely", "probable"]),
                (["certain", "likely", "probable"], "advmod", "how"),
                (["certain", "likely", "probable"], "nsubj", ["it", "that", "prediction", "result", "outcome"])
            ],
            [#3
                ("certainty", "obl", "what")
            ]
        ],
        "display" : "How certain are you?",
        "write" : "How certain are you?",
        "execute" : "certainty",
        "description": "The 'certainty' command will reveal the certainty of a previously presented claim."
    },
    {   
        "id" : "featureNames",
        "keywords" : "features names attributes input",
        "key_sentences": [
            "What is your input?",
            "What do you use as input?",
            "What are the input features?",
            "What features do you use?",
            "what are the names of the features?",
            "what are the features calles?",
            "what are the feature's names?",
            "what are the feature names?",
            "what are the features"
            "feature names"
            #"How do you predict?",
        ],
        "depparse": [
            [#0
                ("root", "root", f"lemma{cd}depend"),
                (f"lemma{cd}depend", "obj", ["what", "which"]),
                (f"lemma{cd}depend", "nsubj", ["it", "that", "prediction", "result", "outcome", "output"])
            ],
            [#1
                ("root", "root", [f"lemma{cd}use", f"lemma{cd}need", f"lemma{cd}have"]),
                ([f"lemma{cd}use", f"lemma{cd}need", f"lemma{cd}have"], "obl", ["it", "that", f"lemma{cd}prediction", f"lemma{cd}result", f"lemma{cd}outcome", f"lemma{cd}output"]),
                ([f"lemma{cd}use", f"lemma{cd}need", f"lemma{cd}have"], ["obj", "nsubj:pass"], f"lemma{cd}feature"),
                (f"lemma{cd}feature", "det", ["what", "which"])
            ],
            [#2
                ("root", "root", [f"lemma{cd}use", f"lemma{cd}need", f"lemma{cd}have"]),
                ([f"lemma{cd}use", f"lemma{cd}need", f"lemma{cd}have"], "nsubj:pass", f"lemma{cd}feature"),
                (f"lemma{cd}feature", "det", ["what", "which"])
            ],
            [#3
                ("root", "root", ["what", "which"]),
                (["what", "which"], "nsubj", ["input", "base", "basis"]),
                (["input", "base", "basis"], "nmod", ["it", "that", f"lemma{cd}prediction", f"lemma{cd}result", f"lemma{cd}outcome", f"lemma{cd}output"])
            ],
            [#4
                ("root", "root", ["input", "base", "basis"]),
                (["input", "base", "basis"], "det", ["what", "which"]),
                (["input", "base", "basis"], "nmod", ["it", "that", "prediction", "result", "outcome", "output"])
            ],
            [#5
                ("root", "root", ["what", "which"]),
                (["what", "which"], "nsubj", [f"lemma{cd}feature", f"lemma{cd}metric", f"lemma{cd}variable"])
                #([f"lemma{cd}feature", f"lemma{cd}metric", f"lemma{cd}variable"], "compound", ["prediction", "input"])
            ],
            [#6
                ("root", "root", f"lemma{cd}feature"),
                (f"lemma{cd}feature", ["det", "nsubj"], ["what", "which"])
            ]
        ],
        "display" : "What is your input?",
        "write" : "What do you use as an input?",
        "execute" : "featureNames",
        "description": "The 'input' command will tell about the input features the AI uses to make a prediction."
    },
    {   
        "id" : "preview",
        "keywords" : "features preview data sample",
        "key_sentences": [
            "Show me some sample data.",
            "Can you show me some sample data?",
            "Sample data",
            "Show sample data",
            "show training data",
            "Show some samples",
            "Show samples",
            "training data"
        ],
        "depparse": [
            [
                ("root", "root", ["give", "show"]),
                (["give", "show"], "obj", "data")
                #("data", "compound", ["sample", "training"])
            ],
            [
                ("root", "root", ["give", "show"]),
                (["give", "show"], "obj", "preview")
            ],
            [
                ("root", "root", "look"),
                ("look", "obj", "what"),
                ("look", "nsubj", "data")
                #("data", "compound", ["sample", "training"])
            ],
            [
                ("root", "root", ["give", "show"]),
                (["give", "show"], "obj", ["preview", "overview"])
                #(["preview", "overview"], "nmod", "data"),
                #("data", "compound", ["sample", "training"])
            ],
            [
                ("root", "root", "data"),
                ("data", "compound", ["sample", "training"])
            ]
        ],
        "display" : "Show me some sample data.",
        "write" : "Can you show me some sample data?",
        "execute" : "preview",
        "description": "The 'preview' command will give you a small preview of how training data instances look like."
    },
    {   
        "id" : "targetvalues",
        "keywords" : "what else target outcome predict output",
        "key_sentences": [
            "What outputs are possible?",
            "Which outputs are possible?",
            "What predictions are possible?",
            "Which predictions are possible?",
            "possible outputs?",
            "possible predictions?",
            "What is your output?",
            "What else can you predict?",
            "What can you predict?",
        ],
        "depparse": [
            [#0
                ("root", "root", [f"lemma{cd}exist", f"lemma{cd}possible"]),
                ([f"lemma{cd}exist", f"lemma{cd}possible"], "nsubj", [f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"]),
                ([f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"], "det", ["what", "which"])
            ],
            [#1
                ("root", "root", "what"),
                ("what", "nsubj", [f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"])
            ],
            [#2
                ("root", "root", f"lemma{cd}be"),
                (f"lemma{cd}be", "obj", "what"),
                (f"lemma{cd}be", "nsubj", [f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"])
            ],
            [#3
                ("root", "root", "what"),
                ("what", "nsubj", ["labels", "variables"]),
                (["labels", "variables"], "compound", ["class", "target"])
            ],
            [#4
                ("root", "root", [f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"]),
                ([f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"], "nsubj", ["which", "what"])
            ],
            [#5
                ("root", "root", [f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"]),
                ([f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"], "amod", "possible")
            ],
            [#6
                ("root", "root", "what"),
                ("what", "nsubj", [f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"]),
                ([f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"], "amod", "possible")
            ]
        ],
        "display" : "What is your output?",
        "write" : "What else can you predict?",
        "execute" : "targetvalues",
        "description": "The 'output' command will tell about the output the AI can generate."
    },
    {   
        "id" : "init",
        "keywords" : "start hello welcome hi",
        "key_sentences": [
            "Hi ERIC.",
            "Hello ERIC",
            "Hi BOT",
            "Hello",
            "Hi",
            "Hey",
            "Hey there",
            "hey ERIC",
            "Hi there.",
            "How are you?",
            "Hi, how are you?",
            "hey, how are you?",
            "hello, how are you?"
        ],
        "depparse": [
            [
                ("root", "root", f"upos{cd}INTJ"),
                (f"upos{cd}INTJ", ["vocative", "discourse", "advmod"], ["eric", "bot", "there"])
            ],
            [
                ("root", "root", ["eric", "bot", "there"]),
                (["eric", "bot", "there"], "discourse", f"upos{cd}INTJ")
            ],
            [
                ("root", "root", ["eric", "bot", "there"])
            ],
            [
                ("root", "root", f"upos{cd}INTJ")
            ],
            [
                ("root", "root", "how"),
                ("how", "cop", "are"),
                ("how", "nsubj", "you")
            ],
            [
                ("root", "root", "let"),
                ("let", "xcomp", [f"lemma{cd}start", f"lemma{cd}begin"]),
                ([f"lemma{cd}start", f"lemma{cd}begin"], "obj", [f"upos{cd}PROPN", f"upos{cd}PRON"])
            ]
        ],
        "display" : "Hi BOT.",
        "write" : "Hi BOT.",
        "execute" : "init",
        "description": ""
    }
]

