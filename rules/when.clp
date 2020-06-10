;When type asking for prediction outcome
(defrule when
    ?o <- (input ui when)
    =>
    (retract ?o)
    (assert (text-rule 1))
    (assert (ui-state (text "What outcome are you interested in?" "What value should the outcome be?")
                        (valid-answers (get-valid-answers-for-target))
                        (clips-type "symbol")
                        (clipboard "''")
                        (fact-type "input when-value ")))
)

;When type asking for prediction outcome with passed parameters
(defrule when-with-user-input-available
    ?o <- (input ui when $?usrinput)
    =>
    (retract ?o)
    (assert (text-rule 1))
    ; (printout t "XXXXXXXXXX (assert (input when-value " (nth$ 1 ?usrinput) "))" crlf)
    (assert (input when-value (nth$ 1 ?usrinput)))
)

;Extracts rule that leads to prediction outcome
(defrule when-value-text
    ?v <- (input when-value ?h)
    ?t <- (text-rule ?n)
    =>  
    (bind ?r (getSurrogateRule ?h ?n))
    (retract ?v)
    (retract ?t)
    (if (neq ?r nil)
    then 
        (assert(text-rule (+ ?n 1)))
        (assert(when-value ?h))
        (assert (ui-state (text (str-cat "There is an increased chance for <big>" ?h "</big> if: <br>" ?r))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type skip)
                        (skip "input when feedback-first")))
    else (
        assert (ui-state (text "That's it.")
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
    )
)

;Ask for feedback: another rule, visualize, nothing
(defrule when-feedback-first-time
    ?w <- (input when feedback-first)
    =>
    (retract ?w)
    (assert (ui-state (text (str-cat "I can either show another rule or display a visualization."))
                        (valid-answers "{'type' : 'selection', 'value' : ['rule', 'visualize', 'nothing']}")
                        (clips-type "symbol")
                        (clipboard "''")
                        (fact-type "input when-ask ")))
)

;Reset system state
(defrule when-ask-rule-nothing
    ?w <- (input when-ask nothing)
    ?t <- (text-rule ?n)
    ?v <- (when-value ?h)
    =>
    (retract ?w)
    (retract ?t)
    (retract ?v)
)

;Visualize tree
(defrule when-ask-rule-visualize
    ?w <- (input when-ask visualize)
    ?t <- (text-rule ?n)
    ?v <- (when-value ?h)
    =>
    (retract ?w)
    (retract ?t)
    (retract ?v)
    (printout t "VISUALIZE W: " ?w crlf)
    (printout t "VISUALIZE T: " ?t crlf)
    (printout t "VISUALIZE V: " ?v crlf)
    (bind ?url (getSurrogateVisualization))
    (printout t "VISUALIZE URL: " ?url crlf)
    (assert (ui-state (text "This is a decision tree whose branches are the rules that approximate the model's behaviour. The darker the color of the nodes, the more important was the condition when applying it on sample data.")
                        (image-url ?url)
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)

;Show another rule
(defrule when-ask-rule
    ?r <- (input when-ask rule)
    ?t <- (text-rule ?n)
    ?v <- (when-value ?h)
    =>
    (retract ?r)
    (retract ?t)
    (bind ?r (getSurrogateRule ?h ?n))
    (if (neq ?r nil)
    then 
        (assert(text-rule (+ ?n 1)))
        (assert(when-value ?h))
        (assert (ui-state (text (str-cat "There is an increased chance for <big>" ?h "</big> if: <br>" ?r))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type skip)
                        (skip "input when feedback")))
    else (
        assert (ui-state (text "That's it.")
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
    )
)

;Ask if another rule
(defrule when-feedback-rule
    ?w <- (input when feedback)
    =>
    (retract ?w)
    (assert (ui-state (text (str-cat "Do you want to see another rule?"))
                        (valid-answers "{'type' : 'selection', 'value' : ['yes', 'no']}")
                        (clips-type "symbol")
                        (clipboard "''")
                        (fact-type "input when-ask-rule ")))
)

;Yes another rule
(defrule when-ask-rule-yes
    ?w <- (input when-ask-rule yes)
    =>
    (retract ?w)
    (assert(input when-ask rule))
)

;No rule, reset system state
(defrule when-ask-rule-no
    ?w <- (input when-ask-rule no)
    ?t <- (text-rule ?n)
    ?v <- (when-value ?h)
    =>
    (retract ?w)
    (retract ?t)
    (retract ?v)
)