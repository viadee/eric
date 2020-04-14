;why not if prediction not available
(defrule why-not-no-prediction
    ?w <- (input ui why-not)
    (list (name predictions) (content nil))
    =>
    (retract ?w)
    (assert (ui-state (text "Why not what? You should make a prediction first. Type 'prediction' into the message field.")
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)

;why not if prediction is available
(defrule why-not
    ?w <- (input ui why-not)
    (list (name predictions) (content ?head $?tail))
    (test(neq nil ?head))
    =>
    (retract ?w)
    (assert (ui-state (text "I need you to select Z:")
                        (valid-answers (str-cat "{'type' : 'selection', 'value' : [" (get-target-values-as-string) "]}"))
                        (clips-type "symbol")
                        (clipboard "''")
                        (fact-type "whynot ")))
)

;why not - generates cf
(defrule why-not-cf
    ?w <- (whynot ?h)
    (list (name predictions) (content ?head $?tail))
    (test(neq nil ?head))
    =>
    (retract ?w)
    (bind ?f (fact-slot-value ?head features))
    (bind ?prediction-values (transform-feature-values ?f))
    (bind ?cf (cf_proto_how_connector ?h ?prediction-values))
    (if (neq ?cf nil)
    then (assert (ui-state (text (str-cat "There is sufficient evidence that " ?h " was not predicted because of the following features: <br> " ?cf))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
    else (assert (ui-state (text "I could not find a reason. Try to alter the data instance and retry.")
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
    )
)
 