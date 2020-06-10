;how-to ask if no prediction, don't care if user parameters were passed or not
(defrule how-to-no-prediction
    ?o <- (input ui how-to $?usrinput)
    (list (name predictions) (content nil))
    =>
    (retract ?o)
    (assert (ui-state (text "You should make a prediction first. Type 'prediction' into the message field.")
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)

;how-to ask for foil
(defrule how-to
    ?o <- (input ui how-to)
    (list (name predictions) (content ?head $?tail))
    (test(neq nil ?head))
    =>
    (retract ?o)
    (assert (ui-state (text "What value should the prediction take?" "What value should the outcome be?" "What alternative value should the outcome take?")
                        (valid-answers (get-valid-answers-for-target))
                        (clips-type "symbol")
                        (clipboard "''")
                        (fact-type "input how-to-value ")))
)

;how-to ask for foil if parameters were passed
(defrule how-to-usrinput-available
    ?o <- (input ui how-to $?usrinput)
    (list (name predictions) (content ?head $?tail))
    (test(neq nil ?head))
    =>
    (retract ?o)
    (assert (input how-to-value (nth$ 1 ?usrinput)))
)

;creates a counterfactual; if not found: apologize
(defrule how-to-value
    ?v <- (input how-to-value ?h)
    (list (name predictions) (content ?head $?tail))
    (test(neq nil ?head))
    =>
    (retract ?v)
    (bind ?f (fact-slot-value ?head features))
    (bind ?prediction-values (transform-feature-values ?f))
    (bind ?cf (cf_proto_how_connector ?h ?prediction-values))
    (if (neq ?cf nil)
    then (assert (ui-state (text (str-cat "Try to do the following changes to your data instance: <br>"  ?cf)
                            (str-cat "May try to alter the following values: <br>"  ?cf))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
    else (assert (ui-state (text (str-cat "I am sorry.. I could not find a data instance in a reasonable amount of time. Try to change your data instance and retry."))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
    )
    
)