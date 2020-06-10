;What if gl in case there is no prediction yet
(defrule whatif-gl-no-prediction
    ?w <- (input ui whatif-gl)
    (list (name predictions) (content nil))
    =>
    (retract ?w)
    (assert (ui-state (text "What if what? You should make a prediction first. Type 'prediction' in the messeage field.")
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)

;What if gl in case there is a prediction
(defrule whatif-gl
    ?w <- (input ui whatif-gl)
    (list (name predictions) (content ?head $?tail))
    (test(neq nil ?head))
    =>
    (retract ?w)
    (assert (ui-state (text "I need you to select X:")
                        (valid-answers (get-valid-answers-for-features))
                        (clips-type "symbol")
                        (clipboard "''")
                        (fact-type "whatifgl ")))
)

;What if gl in case user provided parameters but there is no prediction yet
(defrule whatif-gl-no-prediction
    ?w <- (input ui whatif-gl $?usrinput)
    (list (name predictions) (content nil))
    =>
    (retract ?w)
    (assert (ui-state (text "What if what? You should make a prediction first. Type 'prediction' in the messeage field.")
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)

;What if gl in case there is a prediction and user provided parameters
(defrule whatif-gl
    ?w <- (input ui whatif-gl $?usrinput)
    (list (name predictions) (content ?head $?tail))
    (test(neq nil ?head))
    =>
    (retract ?w)
    (assert (whatifgl (nth$ 1 ?usrinput)))
)

;What if gl creates a plot as image
(defrule whatif-gl-ceterisParibus
    ?w <- (whatifgl ?g)
    (list (name predictions) (content ?head $?tail))
    (test(neq nil ?head))
    =>
    (retract ?w)
    (bind ?f (fact-slot-value ?head features))
    (bind ?prediction-values (transform-feature-values ?f))
    (bind ?t (ceterisParibus_connector ?g ?prediction-values))
    (assert (ui-state (text (str-cat "Look what I created for you. The graph shows the effect on the prediction value when the value for " ?g " is altered. The closer the value on the y-axis is to 1, the more likely is survived. The boundary is 0.5."))
                        (image-url ?t)
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)
 