;Display feature names
(defrule featureNames-first-time
    ?f <- (input ui featureNames)
    ?n <- (input features-asked)
    =>
    (retract ?f)
    (resetCertainty)
    (assert (ui-state (text (str-cat "The features are: " (get-feature-names-as-string)) (str-cat "I use the following features: " (get-feature-names-as-string)))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)

;Display feature names and ask for data preview
(defrule featureNames
    ?f <- (input ui featureNames)
    (not(exists(input features-asked)))
    =>
    (retract ?f)
    (resetCertainty)
    (assert (ui-state (text (str-cat "The features are: " (get-feature-names-as-string)) (str-cat "I use the following features: " (get-feature-names-as-string)))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type skip)
                        (skip "input ui ask-preview")))
)

;Ask for data preview
(defrule ask-data-preview
    ?p <- (input ui ask-preview)
    =>
    (retract ?p)
    (assert (ui-state (text "Do you want to see some sample data instances?" "Shall I show you some sample data?")
                        (valid-answers "{'type' : 'selection', 'value' : ['yes', 'no']}")
                        (clips-type "symbol")
                        (clipboard "''")
                        (fact-type "input preview-ask ")))
)

;If data preview is desired
(defrule ask-data-preview-yes
    ?y <- (input preview-ask yes)
    =>
    (retract ?y)
    (assert(input features-asked))
    (assert(input ui preview))
)

;If data preview is not desired
(defrule ask-data-preview-no
    ?n <- (input preview-ask no)
    =>
    (retract ?n)
    (assert(input features-asked))
)

;Generate data preview as image
(defrule data-preview
    ?p <- (input ui preview)
    =>
    (retract ?p)
    (assert (input features-asked))
    (bind ?url (getDataPreview))
    (assert (ui-state (text "Here are some data instances." "Look, I selected some data instances for you.")
                        (image-url ?url)
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)