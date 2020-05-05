dictionary = [
    {   
        "id" : "predict",
        "keywords" : "predict predictions classify classifications",
        "key_sentences": ["Make me a prediction", "Can you please make me a prediction?", "Can you predict something for me?", "predict", "prediction", "Make prediction", "Make me a prediction"],
        "display" : "Make me a prediction.",
        "write" : "Can you please make me a prediction?",
        "execute" : "predict",
        "description": "The 'predict' command will allow you to infer a prediction from your data intance. In case you did not provide a data instance yet, ERIC will ask you to provide a value for each feature."
    },
    {
        "id": "whatif",
        "keywords" : "what if change",
        "key_sentences": ["What if <key> equals <value>?", "What if you change <key> to <value>?"],
        "display" : "What if X equals Z?",
        "write" : "What if X equals Z?",
        "execute" : "whatif",
        "description": "The 'what-if' command gives you the opportunity to alter the data instance that ERIC is talking about. There will be a new entry on the clipboard."
    },
    {
        "id": "whatif-gl",
        "keywords" : "what if greater less change",
        "key_sentences": ["What if <key> was greater or less?", "What if <key> was greater / less?"],
        "display" : "What if X was greater/less?",
        "write" : "What if X was greater/less?",
        "execute" : "whatif-gl",
        "description": "The 'what-if-greater-less' command fixes the values of all but one features and pertubates the values of this one feature. A graph will show you how the prediction changes."
    },
    {
        "id": "why",
        "keywords" : "why",
        "key_sentences": ["Why did you predict <outcome>?", "Why did you predict that?"],
        "display" : "Why did you predict X?",
        "write" : "Why did you predict X?",
        "execute" : "why",
        "description": "The 'why' command provides information about why the ERIC predicted a specific output. It will present you an explanation. Afterwards will ask you to provide feedback."
    },
    {
        "id": "why-not",
        "keywords" : "why not",
        "key_sentences": ["Why didn't you predict <outcome>?", "Why did you not predict <outcome>?"],
        "display" : "Why didn't you predict Z?",
        "write" : "Why didn't you predict Z?",
        "execute" : "why-not",
        "description": "The 'why-not' command provides information on why an alternative outcome was not predicted. It will present you an explanation. Afterwards will ask you to provide feedback."
    },
    {
        "id": "how-to",
        "keywords" : "how",
        "key_sentences": ["How do I get <outcome>?"],
        "display" : "How do I get Y?",
        "write" : "How do I get Y?",
        "execute" : "how-to",
        "description": "The 'how-to' command tells about the changes that must be done to get an alternative prediction outcome."
    },
    {
        "id": "when",
        "keywords" : "when",
        "key_sentences": ["When do you predict <outcome>?", "When do I get Y?"],
        "display" : "When do you predict Y?",
        "write" : "When do you predict Y?",
        "execute" : "when",
        "description": "The 'when' command tells you for what feature values the model produces a certain outcome most likely."
    },
    {   
        "id" : "certainty",
        "keywords" : "how certain uncertain are you sure",
        "key_sentences": ["How certain are you?", "Are you sure?", "Are you certain?"],
        "display" : "How certain are you?",
        "write" : "How certain are you?",
        "execute" : "certainty",
        "description": "The 'certainty' command will reveal the certainty of a previously presented claim."
    },
    {   
        "id" : "featureNames",
        "keywords" : "features names attributes input",
        "key_sentences": ["What is your input?", "What do you use as input?"],
        "display" : "What is your input?",
        "write" : "What do you use as an input?",
        "execute" : "featureNames",
        "description": "The 'input' command will tell about the input features the AI uses to make a prediction."
    },
    {   
        "id" : "preview",
        "keywords" : "features preview data sample",
        "key_sentences": ["Show me some sample data.", "Can you show me some sample data?"],
        "display" : "Show me some sample data.",
        "write" : "Can you show me some sample data?",
        "execute" : "preview",
        "description": "The 'preview' command will give you a small preview of how training data instances look like."
    },
    {   
        "id" : "targetvalues",
        "keywords" : "what else target outcome predict output",
        "key_sentences": ["What is your output?", "What else can you predict?"],
        "display" : "What is your output?",
        "write" : "What else can you predict?",
        "execute" : "targetvalues",
        "description": "The 'output' command will tell about the output the AI can generate."
    },
    {   
        "id" : "init",
        "keywords" : "start hello welcome hi",
        "key_sentences": ["Hi ERIC.", "Hello ERIC", "Hi BOT", "Hello", "Hi", "Hey", "Hey there", "hey ERIC", "Hi there."],
        "display" : "Hi BOT.",
        "write" : "Hi BOT.",
        "execute" : "init",
        "description": ""
    }
]

