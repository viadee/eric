cd = "#" #category delimiter to acces different attributes of a word (e.g. lemma instead of text: f"lemma{cd}predict"). Do not use ":" as it is already used by depparse for splitting passive/active deprel differentiation and such

#placeholders (prefix "ph_") to replace in preprocessing
ph_outcome = "<outcome>"
ph_key = "<key>"
ph_value = "<value>"
ph_dvalue = "<dupvalue>"
ph_subject = "<subject>"
reserved_placeholder_words = [ph_outcome, ph_key, ph_value, ph_dvalue, ph_subject]

#dependency relations (prefix "dep_"). used in variables to avoid misspelling somewhere in the program
dep_acl = "acl" #adjectival clause
dep_acl_recl = "acl:relcl" #adjectival/relative clause
dep_advcl = "advcl" #adverbial clause
dep_advmod = "advmod" #adverbial modifier
dep_amod = "amod" #adjectival modifier
dep_appos = "appos" #appositional modifier
dep_aux = "aux" #auxiliary
dep_case = "case" #case marking
dep_ccomp = "ccomp" #causal complement
dep_compound = "compound" #compound
dep_cop = "cop" #copula
dep_csubj = "csubj" #clausal subject
dep_det = "det" #determiner
dep_discourse = "discourse" #discourse element (interjectionis, emoticons, discourse particles)
dep_mark = "mark" #marker (marking a clause as subordinal to another clause)
dep_nmod = "nmod" #nominal modifier
dep_nsubj = "nsubj" #nominal subject
dep_nsubj_pass = "nsubj:pass" #nominal subject in passive
dep_nummod = "nummod" #numeric modifier
dep_obj = "obj" #object
dep_obl = "obl" #oblique nominal (non-core argument or adjunct)
dep_obl_tmod = "obl:tmod" #temporal oblique
dep_parataxis = "parataxis" #relation between word and other elements, e.g. senential paranthetical or clause after : or ;
dep_punct = "punct" #punctuation
dep_root = "root" #root dependency from root. only once per sentence
dep_vocative = "vocative" #used to mark an addressed dialogue participant
dep_xcomp = "xcomp" #open clausal complement

dictionary = [
    {   
        "id" : "predict",
        "keywords" : "predict predictions classify classifications",
        "display" : "Make me a prediction.",
        "write" : "Can you please make me a prediction?",
        "execute" : "predict",
        "description": "The 'predict' command will allow you to infer a prediction from your data intance. In case you did not provide a data instance yet, ERIC will ask you to provide a value for each feature."
    },
    {
        "id": "whatif",
        "keywords" : "what if change",
        "display" : "What if X equals Z?",
        "write" : "What if X equals Z?",
        "execute" : "whatif",
        "description": "The 'what-if' command gives you the opportunity to alter the data instance that ERIC is talking about. There will be a new entry on the clipboard."
    },
    {
        "id": "whatif-gl",
        "keywords" : "what if greater less change",
        "display" : "What if X was greater/less?",
        "write" : "What if X was greater/less?",
        "execute" : "whatif-gl",
        "description": "The 'what-if-greater-less' command fixes the values of all but one features and pertubates the values of this one feature. A graph will show you how the prediction changes."
    },
    {
        "id": "why",
        "keywords" : "why",
        "display" : "Why did you predict X?",
        "write" : "Why did you predict X?",
        "execute" : "why",
        "description": "The 'why' command provides information about why the ERIC predicted a specific output. It will present you an explanation. Afterwards will ask you to provide feedback."
    },
    {
        "id": "why-not",
        "keywords" : "why not",
        "display" : "Why didn't you predict Z?",
        "write" : "Why didn't you predict Z?",
        "execute" : "why-not",
        "description": "The 'why-not' command provides information on why an alternative outcome was not predicted. It will present you an explanation. Afterwards will ask you to provide feedback."
    },
    {
        "id": "how-to",
        "keywords" : "how",
        "display" : "How do I get Y?",
        "write" : "How do I get Y?",
        "execute" : "how-to",
        "description": "The 'how-to' command tells about the changes that must be done to get an alternative prediction outcome."
    },
    {
        "id": "when",
        "keywords" : "when",
        "display" : "When do you predict Y?",
        "write" : "When do you predict Y?",
        "execute" : "when",
        "description": "The 'when' command tells you for what feature values the model produces a certain outcome most likely."
    },
    {   
        "id" : "certainty",
        "keywords" : "how certain uncertain are you sure",
        "display" : "How certain are you?",
        "write" : "How certain are you?",
        "execute" : "certainty",
        "description": "The 'certainty' command will reveal the certainty of a previously presented claim."
    },
    {   
        "id" : "featureNames",
        "keywords" : "features names attributes input",
        "display" : "What is your input?",
        "write" : "What do you use as an input?",
        "execute" : "featureNames",
        "description": "The 'input' command will tell about the input features the AI uses to make a prediction."
    },
    {   
        "id" : "preview",
        "keywords" : "features preview data sample",
        "display" : "Show me some sample data.",
        "write" : "Can you show me some sample data?",
        "execute" : "preview",
        "description": "The 'preview' command will give you a small preview of how training data instances look like."
    },
    {   
        "id" : "targetvalues",
        "keywords" : "what else target outcome outcome predict output",
        "display" : "What is your output?",
        "write" : "What else can you predict?",
        "execute" : "targetvalues",
        "description": "The 'output' command will tell about the output the AI can generate."
    },
    {   
        "id" : "init",
        "keywords" : "start hello welcome hi",
        "display" : "Hi BOT.",
        "write" : "Hi BOT.",
        "execute" : "init",
        "description": ""
    }
]

#Punctuation in the key_sentences usually gets removed in preprocessing
nlp_dictionary = [
    {   
        "id" : "predict",
        "key_sentences": [
            "predict",
            f"would {ph_subject} presumably {ph_outcome}?",
            f"is {ph_subject} likely to {ph_outcome}?",
            f"is <subject> {ph_outcome}?",
            f"is it foreseeable that {ph_subject} is {ph_outcome}?",
            f"would {ph_subject} {ph_outcome}?",
            "Make a prediction for the current instance",
            "Make a prediction for the current data",
            "Can you please make me a prediction?", 
            "Make me a prediction", 
            "Make prediction",
            "prediction",
            "Can you predict something for me?",
            "Can you project something for me?",
            f"Can you project if {ph_subject} is {ph_outcome}?",
            f"Can you predict if {ph_subject} is {ph_outcome}?",
            f"Can you calculate if {ph_subject} is {ph_outcome}?",
            f"Can you anticipate if {ph_subject} is {ph_outcome}?",
            f"Can you guess if {ph_subject} is {ph_outcome}?",
            f"Can you foresee if {ph_subject} is {ph_outcome}?",
            "predict for current instance",
            "predict for current data",
            "Tell me what happens",
            "Tell us what happens",
            "Show us what happens",
            "Show me what happens"
        ],
        "depparse": [
            [#0
                ("root", dep_root, "what"),
                ("what", dep_nsubj, "outcome"),
                ("outcome", dep_amod, ["predicted", "current"])
            ],
            [#1
                ("root", dep_root, "predict"),
                ("predict", dep_obj, "outcome")
            ],
            [#2
                ("root", dep_root, "predict"),
                ("predict", dep_obl, ["data", "person"])
            ],
            [#3
                ("root", dep_root, "predicted"),
                ("predicted", dep_nsubj_pass, f"upos{cd}NOUN")
            ],
            [#4
                ("root", dep_root, "predict"),
                ("predict", dep_obj, "something"),
                ("something", dep_nmod, f"upos{cd}PRON")#,
                #(f"upos{category_delimiter}PRON", dep_case, "for")
            ],
            [#5
                ("root", dep_root, "make"),
                ("make", dep_obj, "prediction")
            ],
            [#6
                ("root", dep_root, "happen"),
                ("happen", dep_nsubj, "what")
            ],
            [#7
                ("root", dep_root, "predict")
            ],
            [#8
                ("root", dep_root, "foreseeable"),
                ("foreseeable", dep_nsubj, ph_subject),
                (ph_subject, dep_ccomp, ph_outcome)
            ],
            [#9
                ("root", dep_root, [f"lemma{cd}forecast", f"lemma{cd}predict", f"lemma{cd}project", f"lemma{cd}anticipate"]),
                ([f"lemma{cd}forecast", f"lemma{cd}predict", f"lemma{cd}project", f"lemma{cd}anticipate"], dep_advcl, ph_outcome),
                (ph_outcome, dep_nsubj, ph_subject)
            ]
        ]
    },
    {
        "id": "whatif",
        "key_sentences": [
            "whatif",
            # f"What if {subject} have {value} of {key}",
            f"What if {ph_key} was {ph_value}?",
            f"What if {ph_key} = {ph_value}?",
            f"What if {ph_key} equals {ph_value}?",
            f"What if {ph_key} is {ph_value} and {ph_key} is {ph_value}?",
            f"What happens if {ph_key} equals {ph_value}?",
            f"What if you change {ph_key} to {ph_value}?",
            f"What happens if you change {ph_key} to {ph_value}?",
            f"What if you set {ph_key} to {ph_value}?",
            f"What happens if you set {ph_key} to {ph_value}?",
            f"What if {ph_key} is changed to {ph_value}?",
            f"What happens if {ph_key} is changed to {ph_value}?",
            f"What happens if {ph_key} is {ph_value}",
            f"Change {ph_key} to {ph_value}",
            f"Set {ph_key} to {ph_value}.",
            f"Set {ph_key} = {ph_value}",
            f"{ph_key} = {ph_value}",
            "set x = y"
        ],
        "depparse": [
            [#0
                ("root", dep_root, [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], [dep_obj, dep_advcl, dep_acl], ph_key),
                (ph_key, [dep_appos, dep_nummod, dep_obl, dep_obj, dep_nmod], ph_value)
            ],
            [#1
                ("root", dep_root, f"lemma{cd}happen"),
                (f"lemma{cd}happen", [dep_advcl, dep_parataxis], ph_value),
                (f"lemma{cd}happen", [dep_advcl, dep_nsubj], ph_key)
            ],
            [#2
                ("root", dep_root, "what"),
                ("what", dep_advcl, [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], [dep_obj, dep_nsubj_pass], ph_key),
                ([f"lemma{cd}change", f"lemma{cd}set"], dep_obl, ph_value)
            ],
            [#3
                ("root", dep_root, "what"),
                ("what", [dep_advcl, dep_nsubj], ph_value),
                (ph_value, dep_nsubj, ph_key)
            ],
            [#4
                ("root", dep_root, f"lemma{cd}happen"),
                (f"lemma{cd}happen", dep_advcl, ph_key),
                (f"lemma{cd}happen", [dep_advcl, dep_parataxis], ph_value)
            ],
            [#5
                ("root", dep_root, ph_key),
                (ph_key, dep_nsubj, [f"lemma{cd}change", f"lemma{cd}set"]),
                (ph_key, dep_obl, ph_value)
            ],
            [#6
                ("root", dep_root, [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], dep_obj, ph_value),
                (ph_value, [dep_amod, dep_compound], ph_key)
            ],
            [#7
                ("root", dep_root, f"lemma{cd}happen"),
                (f"lemma{cd}happen", dep_advcl, ph_key),
                (ph_key, [dep_appos, dep_nummod], ph_value)
            ],
            [#8
                ("root", dep_root, ph_key),
                (ph_key, dep_punct, f"lemma{cd}="),
                (ph_key, [dep_parataxis, dep_appos], ph_value)
            ],
            [#9
                ("root", dep_root, "what"),
                ("what", dep_advcl, ph_key),
                ("what", dep_appos, ph_value)
            ],
            [#10
                ("root", dep_root, [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], dep_obj, ph_key),
                ([f"lemma{cd}change", f"lemma{cd}set"], dep_obl, ph_value)
            ],
            [#11
                ("root", dep_root, [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], dep_obj, ph_key),
                ([f"lemma{cd}change", f"lemma{cd}set"], dep_punct, f"lemma{cd}="),
                ([f"lemma{cd}change", f"lemma{cd}set"], dep_parataxis, ph_value)
            ],
            [#12
                ("root", dep_root, "what"),
                ("what", dep_nsubj, ph_key),
                (ph_key, dep_nummod, ph_value)
            ],
            [#13
                ("root", dep_root, "what"),
                ("what", dep_advcl, ph_value),
                (ph_value, dep_mark, "if")
            ],
            [#14
                ("root", dep_root, [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], dep_obj, [f"upos{cd}NOUN", f"upos{cd}PROPN"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], [dep_obj, dep_obl], [f"upos{cd}NOUN", f"upos{cd}PROPN"]),
                ([f"lemma{cd}change", f"lemma{cd}set", f"upos{cd}NOUN", f"upos{cd}PROPN"], dep_punct, "=")
            ],
            [#15
                ("root", dep_root, f"lemma{cd}happen"),
                (f"lemma{cd}happen", dep_advcl, ph_key),
                #(ph_key, dep_mark, "if"),
                (f"lemma{cd}happen", dep_nsubj, "what")
            ],
            [#16
                ("root", dep_root, "key"),
                ("key", dep_amod, [f"lemma{cd}change", f"lemma{cd}set"]),
                ("key", dep_appos, "value")
            ],
            [#17
                ("root", dep_root, f"upos{cd}NOUN"),
                (f"upos{cd}NOUN", dep_amod, [f"lemma{cd}change", f"lemma{cd}set"]),
                (f"upos{cd}NOUN", dep_nmod, f"upos{cd}NOUN")
            ],
            [#18
                ("root", dep_root, f"lemma{cd}happen"),
                (f"lemma{cd}happen", dep_nsubj, "what"),
                (f"lemma{cd}happen", [dep_advcl, dep_parataxis], ph_value),
                (ph_value, dep_nsubj, ph_key)
            ],
            [#19
                ("root", dep_root, [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], dep_obj, [f"upos{cd}NOUN", f"upos{cd}PROPN"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], dep_discourse, f"upos{cd}SYM")
            ],
            [#20
                ("root", dep_root, [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], dep_obj, [f"upos{cd}NOUN", f"upos{cd}PROPN"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], [dep_obj, dep_obl], [f"upos{cd}NOUN", f"upos{cd}PROPN"])
            ],
            [#21
                ("root", dep_root, ph_key),
                (ph_key, dep_nsubj, "what"),
                (ph_key, dep_nummod, ph_value)
            ],
            [#22
                ("root", dep_root, ph_value),
                (ph_value, [dep_csubj, dep_advcl], ph_key)
            ],
            [#23
                ("root", dep_root, f"lemma{cd}happen"),
                (f"lemma{cd}happen", dep_advcl, [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], dep_obj, ph_key),
                (ph_key, dep_nmod, ph_value)
            ],
            [#24   it is obviously incorreect since change should be a verb but depparse classifies it as a nsubj dependency...
                ("root", dep_root, ph_key),
                (ph_key, dep_nsubj, [f"lemma{cd}change", f"lemma{cd}set"]),
                (ph_key, dep_obl, ph_value)
            ],
        ]
    },
    {
        "id": "whatif-gl",
        "key_sentences": [
            "whatif-gl",
            f"What happens if {ph_key} is increased?",
            f"What happens if {ph_key} is decreased?",
            f"What happens if {ph_key} is greater?",
            f"What happens if {ph_key} is higher?",
            f"What happens if {ph_key} is less?",
            f"What happens if {ph_key} is more?",
            f"What happens if {ph_key} is lower?",
            f"What happens if {ph_key} is fewer?",
            f"How many {ph_key} do i need to get <outcome>?",
            f"How much {ph_key} do i need to get <outcome>?",
            f"What difference would it have if I changed {ph_key}?",
            f"What difference does in make if you change {ph_key}?",
            f"What impact would it have if I changed {ph_key}?",
            f"What impact does in make if you change {ph_key}?",
            f"What if {ph_key} was greater or less?",
            f"What if {ph_key} was less?",
            f"What if {ph_key} was greater?",
            f"What if {ph_key} was greater / less?",
            f"What if {ph_key} was over or under <value>?",
            f"What if {ph_key} was over / under <value>?",
            f"What if {ph_key} was over <value>?",
            f"What if {ph_key} was under <value>?",
            f"What if {ph_key} was higher or lower?",
            f"What if {ph_key} was higher / lower?",
            f"What if {ph_key} was lower?",
            f"What if {ph_key} was higher?",
            f"Change {ph_key} to greater / less <value>",
            f"Change {ph_key} to over / under <value>",
            f"Change {ph_key} to higher / lower <value>",
            f"What if {ph_key} was between <value> and <dupvalue>",
            f"What if {ph_key} was different?",
            f"What if {ph_key} was higher?",
            f"What if {ph_key} was lower?",
            f"What if {ph_key} was greater?",
            f"What if {ph_key} was less?",
            f"What if {ph_subject} were {ph_key}?",
            f"What if {ph_subject} was {ph_key}?",
            f"predict for higher {ph_key}.",
            f"predict for lower {ph_key}.",
            f"predict for greater {ph_key}.",
            f"predict for different {ph_key}.",
            f"predict for smaller {ph_key}.",
            f"predict for fewer {ph_key}.",
            f"predict for less {ph_key}.",
            f"predict for more {ph_key}.",
            f"predict for {ph_key} with higher value",
            f"predict for {ph_key} with lower value",
            f"predict for {ph_key} with greater value",
            f"predict for {ph_key} with different value",
            f"predict for {ph_key} with smaller value",
            f"predict for {ph_key} with larger value",
            f"Does the outcome change with a lower number of {ph_key}?",
            f"Does the outcome change with a higher number of {ph_key}?",
            f"Does the result change with a lower number of {ph_key}?",
            f"Does the result change with a higher number of {ph_key}?",
            f"Does the prediction change with a lower number of {ph_key}?",
            f"Does the prediction change with a higher number of {ph_key}?",
        ],
        "depparse": [
            [#0
                ("root", dep_root, "what"),
                ("what", dep_advcl, ["lower", "higher", "greater", "more"]),
                (["lower", "higher", "greater", "more", "less"], dep_nsubj, ph_key),
                (["lower", "higher", "greater", "more", "less"], dep_obl, ph_value)#,
                #(["lower", "higher", "greater", "more", "less"], dep_mark, "if")
            ],
            [#1
                ("root", dep_root, "what"),
                ("what", dep_advcl, ["lower", "higher", "greater", "more", "less"]),
                (["lower", "higher", "greater", "more", "less"], dep_nsubj, ph_key)
            ],
            [#2
                ("root", dep_root, "what"),
                ("what", [dep_nsubj, dep_advcl], ph_value),
                (ph_value, dep_nsubj, ph_key),
                #(ph_value, dep_mark, "if"),
                (ph_value, [dep_advmod, dep_case], ["less", "over", "under", "below", "above"])
            ],
            [#3
                ("root", dep_root, ["set", "change"]),
                (["set", "change"], dep_obj, ph_key),
                (ph_key, dep_amod, ["lower", "higher", "over", "under", "below", "above"])
            ],
            [#4
                ("root", dep_root, ph_key),
                (ph_key, dep_appos, ph_value),
                (ph_key, dep_punct, [f"lemma{cd}<", f"lemma{cd}>"])
            ],
            [#5
                ("root", dep_root, [f"lemma{cd}set", f"lemma{cd}change"]),
                ([f"lemma{cd}set", f"lemma{cd}change"], dep_obj, ph_key),
                ([f"lemma{cd}set", f"lemma{cd}change"], dep_obl_tmod, ph_value),
                (ph_value, dep_amod, ["higher", "lower", "greater"])
            ],
            [#6
                ("root", dep_root, [f"lemma{cd}set", f"lemma{cd}change"]),
                ([f"lemma{cd}set", f"lemma{cd}change"], dep_obj, ph_key),
                ([f"lemma{cd}set", f"lemma{cd}change"], [dep_nmod, dep_obl], ph_value),
                (ph_value, dep_case, ["under", "over", "below", "above"])
            ],
            [#7
                ("root", dep_root, [f"lemma{cd}set", f"lemma{cd}change", f"lemma{cd}make"]),
                ([f"lemma{cd}set", f"lemma{cd}change", f"lemma{cd}make"], dep_obj, ph_key),
                ([f"lemma{cd}set", f"lemma{cd}change", f"lemma{cd}make"], [dep_obj, dep_xcomp, dep_parataxis], ["lower", "higher", "greater", "less"])
            ],
            [#8
                ("root", dep_root, "set"),
                ("set", dep_obj, ph_key),
                (ph_key, dep_nmod, ph_value),
                (ph_value, dep_case, ["under", "over"])
            ],
            [#9
                ("root", dep_root, "what"),
                ("what", dep_advcl, ph_key),
                #(ph_key, dep_mark, "if"),
                (ph_key, dep_appos, ph_value),
                (ph_value, dep_punct, [f"lemma{cd}<", f"lemma{cd}>"])
            ],
            [#10
                ([f"lemma{cd}increase", f"lemma{cd}decrease", f"lemma{cd}lower", f"lemma{cd}raise", f"lemma{cd}adjust"], dep_mark, "if")
            ],
            [#11
                ("root", dep_root, "how"),
                ("how", dep_nsubj, ["change", "differ"]),
                (["change", "differ"], [dep_nsubj, dep_compound], ["value", "outcome", "result", "class", "prediction"]),
                (["change", "differ"], [dep_nmod, dep_obl], [f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], dep_nmod, ph_key),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], dep_amod, ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#12
                ("root", dep_root, f"lemma{cd}happen"),
                (f"lemma{cd}value", dep_nsubj, "what"),
                (f"lemma{cd}value", dep_advcl, ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#13
                ("root", dep_root, [f"lemma{cd}predict", f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}predict", f"lemma{cd}change", f"lemma{cd}set"], dep_obj, f"upos{cd}NOUN"),
                ([f"lemma{cd}predict", f"lemma{cd}change", f"lemma{cd}set"], dep_obl, ["lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#14
                ("root", dep_root, f"lemma{cd}predict"),
                (f"lemma{cd}predict", dep_obj, f"upos{cd}NOUN"),
                (f"lemma{cd}predict", dep_obl, [f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], dep_amod, ["lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#15
                ("root", dep_root, f"lemma{cd}predict"),
                (f"lemma{cd}predict", dep_obj, f"upos{cd}NOUN"),
                (f"upos{cd}NOUN", dep_nmod, ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#16
                ("root", dep_root, "predict"),
                ("predict", dep_obl, ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#17
                ("root", dep_root, "predict"),
                ("predict", dep_obl, [f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], dep_amod, ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#18
                ("root", dep_root, ["set", "change"]),
                (["set", "change"], dep_obj, f"upos{cd}NOUN"),
                (["set", "change"], dep_obl, [f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], dep_amod, ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#19
                ("root", dep_root, ["set", "change"]),
                (["set", "change"], dep_obl, [f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], dep_case, f"upos{cd}NOUN"),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], dep_amod, ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#20
                ("root", dep_root, "what"),
                ("what", dep_advcl, [f"lemma{cd}change", f"lemma{cd}set"]),
                ([f"lemma{cd}change", f"lemma{cd}set"], dep_nsubj_pass, f"upos{cd}NOUN"),
                ([f"lemma{cd}change", f"lemma{cd}set"], dep_obl, [f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], dep_amod, ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#21
                ("root", dep_root, "predict"),
                ("predict", dep_obj, f"upos{cd}NOUN"),
                (f"upos{cd}NOUN", dep_obl, [f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], dep_amod, ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#22
                ("root", dep_root, [f"lemma{cd}change", f"lemma{cd}differ"]),
                ([f"lemma{cd}change", f"lemma{cd}differ"], dep_advmod, "how"),
                ([f"lemma{cd}change", f"lemma{cd}differ"], dep_nsubj, ["value", "outcome", "result", "class", "prediction"]),
                ([f"lemma{cd}change", f"lemma{cd}differ"], [dep_advcl, dep_obl], ph_value),
                (ph_value, dep_nsubj, ph_key),
                (ph_value, dep_advmod, ["below", "above", "under", "over", "less"])
            ],
            [#23
                ("root", dep_root, [f"lemma{cd}change", f"lemma{cd}differ"]),
                ([f"lemma{cd}change", f"lemma{cd}differ"], dep_advmod, "how"),
                ([f"lemma{cd}change", f"lemma{cd}differ"], dep_advcl, ["lower", "higher", "greater", "bigger", "smaller"]),
                ([f"lemma{cd}change", f"lemma{cd}differ"], dep_nsubj, ["value", "outcome", "result", "class", "prediction"]),
                (["lower", "higher", "greater", "bigger", "smaller"], dep_nsubj, ph_key),
                (["lower", "higher", "greater", "bigger", "smaller"], dep_obl, ph_value)
            ],
            [#24
                ("root", dep_root, [f"lemma{cd}change", f"lemma{cd}differ"]),
                ([f"lemma{cd}change", f"lemma{cd}differ"], dep_advmod, "how"),
                ([f"lemma{cd}change", f"lemma{cd}differ"], dep_nsubj, ["value", "outcome", "result", "class", "prediction"]),
                ([f"lemma{cd}change", f"lemma{cd}differ"], dep_obl, ph_value),
                (ph_value, dep_advmod, "more"),
                ("more", dep_nsubj, ph_key)
            ],
            [#25
                ([f"lemma{cd}increase", f"lemma{cd}decrease", "lower", "higher", "greater", "bigger", "smaller", "different"], [dep_acl, dep_obj, dep_nsubj_pass, dep_nsubj], ph_key)
            ],
            [#26
                 (ph_key, [dep_xcomp, dep_advmod, dep_amod, dep_compound], [f"lemma{cd}increase", f"lemma{cd}decrease", "lower", "higher", "greater", "bigger", "smaller", "more"])
            ],
            [#27
                ("root", dep_root, [f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], dep_compound, [f"lemma{cd}increase", f"lemma{cd}decrease", "lower", "higher", "greater", "bigger", "smaller"]),
                ([f"lemma{cd}value", f"lemma{cd}number", f"lemma{cd}amount", f"lemma{cd}degree"], dep_nmod, ph_key)
            ],
            [#28
                (f"lemma{cd}happen", dep_advcl, [f"lemma{cd}increase", f"lemma{cd}decrease", "lower", "higher", "greater", "bigger", "smaller"]),
                (f"lemma{cd}happen", dep_nsubj_pass, ph_key)
            ],
            [#29
                ("root", dep_root, [f"lemma{cd}affect", f"lemma{cd}influence", f"lemma{cd}change"]),
                ([f"lemma{cd}affect", f"lemma{cd}influence", f"lemma{cd}change"], dep_obj, ["value", "outcome", "result", "class", "prediction"]),
                ([f"lemma{cd}affect", f"lemma{cd}influence", f"lemma{cd}change"], dep_advcl, [f"lemma{cd}change", f"lemma{cd}differ", f"lemma{cd}decrease", f"lemma{cd}increase"]),
                ([f"lemma{cd}change", f"lemma{cd}differ", f"lemma{cd}decrease", f"lemma{cd}increase"], [dep_nsubj_pass, dep_advcl], ph_key)
            ],
            [#30
                ("root", dep_root, f"lemma{cd}happen"),
                (f"lemma{cd}happen", dep_advcl, [f"lemma{cd}increase", f"lemma{cd}decrease", "lower", "higher", "greater", "bigger", "smaller", "different"]),
                ([f"lemma{cd}increase", f"lemma{cd}decrease", "lower", "higher", "greater", "bigger", "smaller", "different"], [dep_acl, dep_obj, dep_nsubj_pass, dep_nsubj], ph_key)
            ],
            [#31
                ("root", dep_root, f"lemma{cd}predict"),
                (f"lemma{cd}predict", dep_obj, f"upos{cd}NOUN"),
                (f"upos{cd}NOUN", dep_nmod, ["value", "amount", "degree"]),
                (["value", "amount", "degree"], dep_nmod, ["decreased", "increased", "lower", "higher", "greater", "bigger", "smaller"])
            ],
            [#32
                ("root", dep_root, f"lemma{cd}change"),
                (f"lemma{cd}change", dep_advcl, [f"lemma{cd}change", f"lemma{cd}different", f"lemma{cd}alter", f"lemma{cd}adjust"]),
                ([f"lemma{cd}change", f"lemma{cd}different", f"lemma{cd}alter", f"lemma{cd}adjust"], [dep_nsubj_pass, dep_nsubj], ph_key)
            ]
        ]
    },
    {
        "id": "why",
        "key_sentences": [ 
            "why",
            f"Why did you predict {ph_outcome}?",
            "Why did you predict that?",
            "Why do you predict that?",
            f"Why do you predict {ph_outcome}?",
            "Why do you think that?",
            f"Why {ph_outcome}?",
            f"Explain {ph_outcome}",
            "Explain yourself.",
            "Explain the prediction",
            "Explain the result.",
            "Explain the outcome",
            "Please give an explanation.",
            "Explanation",
            "show me how you got that result",
            "show me how you got that outcome",
            f"show me how you got {ph_outcome}",
            "show me why you got that result",
            "show me why you got that outcome",
            f"show me why you got {ph_outcome}",
            "how did you get that result",
            "how did you get that outcome",
            f"how did you get {ph_outcome}",
            "why did you predict that result",
            "why did you predict that outcome",
            "why did you get that result",
            "why did you get that outcome",
            f"why did you get {ph_outcome}",
            f"why did you predict {ph_outcome}"
        ],
        "depparse": [
            [#0
                ("root", dep_root, ["likely", "probable"]),
                (["likely", "probable"], dep_advmod, "why"),
                (["likely", "probable"], dep_ccomp, ph_outcome)
            ],
            [#1
                ("root", dep_root, f"lemma{cd}predict"),
                (f"lemma{cd}predict", dep_advmod, "why"),
                (f"lemma{cd}predict", [dep_advcl, dep_xcomp], ph_outcome)
            ],
            [#2
                ("root", dep_root, ph_outcome),
                (ph_outcome, dep_advmod, "why"),
                (ph_outcome, dep_nsubj, f"upos{cd}NOUN")
            ],
            [#3
                ("root", dep_root, [ph_outcome, f"lemma{cd}predict"]),
                (ph_outcome, dep_advmod, "why")
            ],
            [#4
                ("root", dep_root, ["why", f"lemma{cd}explanation", f"lemma{cd}explain"])
            ]
        ]
    },
    {
        "id": "why-not",
        "key_sentences": [
            "why-not",
            f"Why didn't you predict {ph_outcome}?",
            f"Why did you not predict {ph_outcome}?",
            f"Why not {ph_outcome}?",
        ],
        "depparse": [
            [#0
                ("root", dep_root, "why"),
                ("why", dep_nsubj, ["value", "outcome", "result", "class", "prediction"]),
                (["value", "outcome", "result", "class", "prediction"], dep_advmod, f"lemma{cd}not"),
                (["value", "outcome", "result", "class", "prediction"], dep_acl, ph_outcome)
            ],
            [#1
                ("root", dep_root, ph_outcome),
                (ph_outcome, dep_advmod, "why"),
                (ph_outcome, dep_advmod, f"lemma{cd}not")
            ],
            [#2
                ("root", dep_root, "why"),
                ("why", dep_advmod, f"lemma{cd}not"),
                ("why", dep_nsubj, ["value", "outcome", "result", "class", "prediction"]),
                (["value", "outcome", "result", "class", "prediction"], dep_acl, ph_outcome)
            ],
            [#3
                ("root", dep_root, "why"),
                ("why", dep_advmod, f"lemma{cd}not")
            ]
        ]
    },
    {
        "id": "how-to",
        "key_sentences": [
            "how-to",
            f"How do I get {ph_outcome}?",
            f"How could {ph_subject} be {ph_outcome}",
            f"What has to change to get {ph_outcome}?",
            "What has to change for <outcome>?",
            "What factors do I need so that <subject> <outcome>?",
            "Under which conditions is <subject> <outcome>?",
            "Under which circumstances is <subject> <outcome>?",
            "Which conditions have to be fulfilled so that <subject> is <outcome>",
            "Wchich conditions have to be fulfilled for a <outcome> result?",
            "how do i get <subject> to <outcome>?"
        ],
        "depparse": [
            [#0
                ("root", dep_root, f"lemma{cd}have"),
                (f"lemma{cd}have", dep_nsubj, "what"),
                (f"lemma{cd}have", dep_xcomp, [f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"]),
                ([f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"], dep_mark, "to"),
                ([f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"], dep_ccomp, ph_outcome)
            ],
            [#1
                ("root", dep_root, [f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"]),
                ([f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"], dep_advmod, "how"),
                ([f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"], [dep_obl, dep_advcl], ph_outcome)
            ],
            [#2
                ("root", dep_root, f"lemma{cd}have"),
                (f"lemma{cd}have", dep_nsubj, "what"),
                (f"lemma{cd}have", dep_xcomp, [f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"]),
                ([f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"], dep_mark, "to"),
                ([f"lemma{cd}change", f"lemma{cd}alter", f"lemma{cd}differ", f"lemma{cd}modify"], dep_advcl, "get"),
                ("get", dep_obj, "prediction"), #["person", "prediction"] would be ideal, but only for the titanic model
                ("prediction", dep_amod, ph_outcome) #["person", "prediction"] would be ideal, but only for the titanic model
            ],
            [#3
                ("root", dep_root, f"lemma{cd}have"),
                (f"lemma{cd}have", [dep_nsubj, dep_obj], "what"),
                (f"lemma{cd}have", dep_xcomp, [f"lemma{cd}change", f"lemma{cd}modify", f"lemma{cd}alter", f"lemma{cd}adjust", f"lemma{cd}different"]),
                ([f"lemma{cd}change", f"lemma{cd}modify", f"lemma{cd}alter", f"lemma{cd}adjust", f"lemma{cd}different"], dep_advcl, "get"),
                ("get", dep_obj, [f"upos{cd}NOUN", f"upos{cd}PROPN"]),
                ([f"upos{cd}NOUN", f"upos{cd}PROPN"], dep_amod, ph_outcome)
            ]
        ]
    },
    {
        "id": "when",
        "key_sentences": [
            "when",
            f"When do you predict {ph_outcome}?",
            f"When do I get {ph_outcome}?",
            f"When is the outcome {ph_outcome}?",
            f"When is the result {ph_outcome}?",
            f"When is {ph_subject} {ph_outcome}?",
            f"When are {ph_subject} {ph_outcome}?",
            f"Which parameters lead to a {ph_outcome} result?",
            f"Which parameters lead to a {ph_outcome} outcome?",
            f"Which values lead to a {ph_outcome} result?",
            f"Which values lead to a {ph_outcome} outcome?",
            f"Which circumstances lead to a {ph_outcome} result?",
            f"Which circumstances lead to a {ph_outcome} outcome?",
            f"Which circumstances lead to a {ph_outcome} prediction?",
            f"Which conditions lead to a {ph_outcome} result?",
            f"Which conditions lead to a {ph_outcome} outcome?",
            f"Which conditions lead to a {ph_outcome} prediction?",
        ],
        "depparse": [
            [#0
                (f"lemma{cd}have", [dep_nsubj_pass, dep_obj], f"lemma{cd}feature"),
                (f"lemma{cd}feature", dep_det, f"upos{cd}DET"),
                (f"lemma{cd}feature", dep_obl, ph_outcome)
            ],
            [#1
                ("root", dep_root, "when"),
                ("when", dep_nsubj, ["class", "outcome", "result"]),
                (["class", "outcome", "result"], dep_acl, ph_outcome),
                (ph_outcome, dep_xcomp, ["likely", "probable"])
            ],
            [#2
                ("root", dep_root, ph_outcome),
                (ph_outcome, [dep_mark, dep_advmod], "when")
            ],
            [#3
                ("root", dep_root, ["likely", "probable"]),
                (["likely", "probable"], dep_advmod, "when"),
                (["likely", "probable"], dep_ccomp, ph_outcome)
            ],
            [#4
                ("root", dep_root, f"lemma{cd}need"),
                (f"lemma{cd}need", dep_obl, ph_outcome),
                (f"lemma{cd}need", [dep_obj, dep_nsubj_pass], f"lemma{cd}feature"),
                (f"lemma{cd}feature", dep_det, ["what", "which"])
            ],
            [#5
                ("root", dep_root, "when"),
                ("when", dep_appos, ph_outcome)
            ],
            [#6
                ("root", dep_root, ph_outcome),
                ("when", [dep_advmod, dep_mark], "when")
            ],
            [#7
                ("root", dep_root, f"lemma{cd}predict"),
                (f"lemma{cd}predict", [dep_obj, dep_xcomp], ph_outcome)
            ]
        ]
    },
    {   
        "id" : "certainty",
        "key_sentences": [
            "certainty",
            "How certain are you?",
            "How sure are you?",
            "How certain are you about the result?",
            "How sure are you about the result?",
            "How certain are you about the outcome?",
            "How sure are you about the outcome?",
            "How certain are you about the prediction?",
            "How sure are you about the prediction?",
            "How certain is the calculation?",
            "How certain is the prediction?",
            "How certain is the result?",
            "How certain is the outcome?",
            "How are the chances for {ph_outcome}?",
            "What are the changes of {ph_outcome}?",
            "What’s the probability of error of this calculation?",
            "What’s the probability of error of this prediction?",
            "What’s the probability of error of this result?",
            "What’s the probability of error of this outcome?",
            "Are you sure?",
            "Are you certain?"
        ],
        "depparse": [
            [#0
                ("root", dep_root, "what"),
                ("what", dep_nsubj, ["probability", "certainty", "likelihood"]),
                (["probability", "certainty", "likelihood"], dep_nmod, ["it", "that", f"lemma{cd}prediction", f"lemma{cd}result", f"lemma{cd}outcome"])
            ],
            [#1
                ("root", dep_root, ["certain", "likely", "probable", "save", "safe"]),
                (["certain", "likely", "probable", "save", "safe"], dep_advmod, "how"),
                (["certain", "likely", "probable", "save", "safe"], [dep_ccomp, dep_acl_recl], ph_outcome)
            ],
            [#2
                ("root", dep_root, ["certain", "likely", "probable", "save", "safe"]),
                (["certain", "likely", "probable", "save", "safe"], dep_advmod, "how"),
                (["certain", "likely", "probable", "save", "safe"], dep_nsubj, ["it", "that", f"lemma{cd}prediction", f"lemma{cd}result", f"lemma{cd}outcome"])
            ],
            [#3
                (["certainty", f"lemma{cd}chance", "likelihood"], [dep_nsubj, dep_obl], "what")
            ],
            [#4
                (["it", "that", f"lemma{cd}prediction", f"lemma{cd}result", f"lemma{cd}outcome"], dep_acl, ["certain", "likely", "probable", "save", "safe"])
            ],
            [#5
                (["certain", "likely", "probable", "save", "safe"], dep_aux, f"lemma{cd}be"),
                (["certain", "likely", "probable", "save", "safe"], dep_nsubj, f"upos{cd}PRON"),
                (["certain", "likely", "probable", "save", "safe"], dep_ccomp, f"lemma{cd}happen")
            ],
            [#6
                (ph_outcome, dep_advmod, ["presumably", "likely", "probably", "foreseeably"])
            ],
            [#7
                (["significant", "certain", "meaningful", "probable", "likely", "save", "safe"], dep_nsubj, ["it", "that", f"lemma{cd}prediction", f"lemma{cd}result", f"lemma{cd}outcome"])
            ],
            [#8
                ("root", dep_root, "what"),
                ("what", dep_nsubj, [f"lemma{cd}chance", f"lemma{cd}likelihood", f"lemma{cd}probability", f"lemma{cd}certainty"]),
                ([f"lemma{cd}chance", f"lemma{cd}likelihood", f"lemma{cd}probability", f"lemma{cd}certainty"], dep_acl, ph_outcome)
            ]
        ]
    },
    {   
        "id" : "featureNames",
        "key_sentences": [
            "featureNames",
            "How do you work out the prediction?",
            "What is your input?",
            "What do you use as input?",
            "What are the input features?",
            "What features do you use?",
            "what are the names of the features?",
            "what are the features calles?",
            "what are the feature's names?",
            "what are the feature names?",
            "what are the features",
            "What parameters do you use?",
            "What features do you use?",
            "What input do you use?",
            "What kind of features do you use?",
            "What factors do you use?",
            "feature names",
            "Show me your features",
            "show me your input",
            "Show me your feature names",
            "show me your input values"
            #"How do you predict?",
        ],
        "depparse": [
            [#0
                ("root", dep_root, f"lemma{cd}depend"),
                (f"lemma{cd}depend", dep_obj, ["what", "which"]),
                (f"lemma{cd}depend", dep_nsubj, ["it", "that", "prediction", "result", "outcome", "output"])
            ],
            [#1
                ("root", dep_root, [f"lemma{cd}use", f"lemma{cd}need", f"lemma{cd}have"]),
                ([f"lemma{cd}use", f"lemma{cd}need", f"lemma{cd}have"], dep_obl, ["it", "that", f"lemma{cd}prediction", f"lemma{cd}result", f"lemma{cd}outcome", f"lemma{cd}output"]),
                ([f"lemma{cd}use", f"lemma{cd}need", f"lemma{cd}have"], [dep_obj, dep_nsubj_pass], f"lemma{cd}feature"),
                (f"lemma{cd}feature", dep_det, ["what", "which"])
            ],
            [#2
                ("root", dep_root, [f"lemma{cd}use", f"lemma{cd}need", f"lemma{cd}have"]),
                ([f"lemma{cd}use", f"lemma{cd}need", f"lemma{cd}have"], dep_nsubj_pass, f"lemma{cd}feature"),
                (f"lemma{cd}feature", dep_det, ["what", "which"])
            ],
            [#3
                ("root", dep_root, ["what", "which"]),
                (["what", "which"], dep_nsubj, ["input", "base", "basis"]),
                (["input", "base", "basis"], dep_nmod, ["it", "that", f"lemma{cd}prediction", f"lemma{cd}result", f"lemma{cd}outcome", f"lemma{cd}output"])
            ],
            [#4
                ("root", dep_root, ["input", "base", "basis"]),
                (["input", "base", "basis"], dep_det, ["what", "which"]),
                (["input", "base", "basis"], dep_nmod, ["it", "that", "prediction", "result", "outcome", "output"])
            ],
            [#5
                ("root", dep_root, ["what", "which"]),
                (["what", "which"], dep_nsubj, [f"lemma{cd}feature", f"lemma{cd}metric", f"lemma{cd}variable"])
                #([f"lemma{cd}feature", f"lemma{cd}metric", f"lemma{cd}variable"], dep_compound, ["prediction", "input"])
            ],
            [#6
                ("root", dep_root, f"lemma{cd}feature"),
                (f"lemma{cd}feature", [dep_det, dep_nsubj], ["what", "which"])
            ]
        ]
    },
    {   
        "id" : "preview",
        "key_sentences": [
            "preview",
            "preview the data",
            "preview the sample data",
            "preview the samples",
            "Show me some preview data",
            "show me a data preview",
            "Show me some sample data.",
            "What kind of data do you use?",
            "Can you show me some sample data?",
            "show me how you do things",
            "show me how you make a prediction",
            "show me how you calculate things",
            "Sample data",
            "Show sample data",
            "show training data",
            "Show some samples",
            "Show samples",
            "training data"
        ],
        "depparse": [
            [
                ("root", dep_root, ["give", "show"]),
                (["give", "show"], dep_obj, "data")
            ],
            [
                ("root", dep_root, ["give", "show"]),
                (["give", "show"], dep_obj, "preview")
            ],
            [
                ("root", dep_root, "look"),
                ("look", dep_obj, "what"),
                ("look", dep_nsubj, "data")
            ],
            [
                ("root", dep_root, ["give", "show"]),
                (["give", "show"], dep_obj, ["preview", "overview"])
            ],
            [
                ("root", dep_root, "data"),
                ("data", dep_compound, ["sample", "training"])
            ]
        ]
    },
    {   
        "id" : "targetvalues",
        "key_sentences": [
            "targetvalues",
            "what could happen?",
            "What outputs are possible?",
            "Which outputs are possible?",
            "What predictions are possible?",
            "Which predictions are possible?",
            "possible outputs?",
            "possible predictions?",
            "what are the outcomes?",
            "what are the possible outcomes?",
            "What is your output?",
            "What else can you predict?",
            "What can you predict?",
            "What can the outcome be?",
            "What form can the outcome take?",
            "What can the result be?",
            "What form can the result take?"
        ],
        "depparse": [
            [#0
                ("root", dep_root, [f"lemma{cd}exist", f"lemma{cd}possible"]),
                ([f"lemma{cd}exist", f"lemma{cd}possible"], dep_nsubj, [f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"]),
                ([f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"], dep_det, ["what", "which"])
            ],
            [#1
                ("root", dep_root, ["what", "which"]),
                ("what", dep_nsubj, [f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"])
            ],
            [#2
                ("root", dep_root, f"lemma{cd}be"),
                (f"lemma{cd}be", dep_obj, "what"),
                (f"lemma{cd}be", dep_nsubj, [f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"])
            ],
            [#3
                ("root", dep_root, "what"),
                ("what", dep_nsubj, ["labels", "variables"]),
                (["labels", "variables"], dep_compound, ["class", "target"])
            ],
            # [#4
            #     ("root", dep_root, [f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"]),
            #     ([f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"], dep_nsubj, ["which", "what"])
            # ],
            [#5
                ("root", dep_root, [f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"]),
                ([f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"], dep_amod, "possible")
            ],
            [#6
                ("root", dep_root, "what"),
                ("what", dep_nsubj, [f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"]),
                ([f"lemma{cd}outcome", f"lemma{cd}result", f"lemma{cd}class", f"lemma{cd}output", f"lemma{cd}prediction"], dep_amod, "possible")
            ],
            [#7
                ("root", dep_root, "what"),
                ("what", dep_cop, f"lemma{cd}be"),
                ("what", dep_nsubj, f"lemma{cd}label")
            ]
        ]
    },
    {   
        "id" : "init",
        "key_sentences": [
            "init",
            "Listen",
            "what's up?",
            "whats up?",
            "Hi ERIC.",
            "Hello ERIC",
            "Hi BOT",
            "Hello",
            "Hi",
            "Hey",
            "Hello",
            "Heya",
            "Greetings",
            "Salutations",
            "Ave",
            "Ave, ERIC",
            "Hey there",
            "hey ERIC",
            "Hi there.",
            "How are you?",
            "Hi, how are you?",
            "hey, how are you?",
            "hello, how are you?",
            "Good morning",
            "G'day",
            "good evening", 
            "good afternoon",
            "good morning, Eric",
            "good evening, Eric", 
            "good afternoon, Eric",
        ],
        "depparse": [
            [
                ("root", dep_root, f"upos{cd}INTJ"),
                (f"upos{cd}INTJ", [dep_vocative, dep_discourse, dep_advmod], ["eric", "bot", "there"])
            ],
            [
                ("root", dep_root, ["eric", "bot", "there", f"upos{cd}NOUN"]),
                (["eric", "bot", "there"], dep_discourse, f"upos{cd}INTJ")
            ],
            [
                ("root", dep_root, ["eric", "bot", "there"])
            ],
            [
                ("root", dep_root, f"upos{cd}INTJ")
            ],
            [
                ("root", dep_root, "how"),
                ("how", dep_cop, "are"),
                ("how", dep_nsubj, "you")
            ],
            [
                ("root", dep_root, "let"),
                ("let", dep_xcomp, [f"lemma{cd}start", f"lemma{cd}begin"]),
                ([f"lemma{cd}start", f"lemma{cd}begin"], dep_obj, [f"upos{cd}PROPN", f"upos{cd}PRON"])
            ]
        ]
    },
    {
        'id': 'getImportance',
        'key_sentences': [
            "getImportance"
        ],
        'depparse': [

        ]
    },
    {
        'id': 'getNLargest',
        'keywords': 'nth largest large get',
        'key_sentences': [
            "getNLargest"
        ],
        'depparse': [

        ]
    },
    {
        'id': 'getFeatureValue',
        'key_sentences': [
            "getFeatureValue"
        ],
        'depparse': [],
    },
    {
        'id': 'addition',
        'key_sentences': [
            "addition"
        ],
        'depparse': [],
    },
]
