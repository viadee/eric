;Asking the why question without having made a prediciton
(defrule why-no-prediction
    ?w <- (input ui why)
    (list (name predictions) (content nil))
    =>
    (printout t "FIRED: " "why-no-prediction" crlf)
    (retract ?w)
    (assert (ui-state (text "Why what? You should make a prediction first. Type 'prediction' into the message field.")
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)

;Asking why if prediction available
(defrule why-prediction-available
    ?w <- (input ui why)
    (list (name predictions) (content ?head $?tail))
    (test(neq nil ?head))
    (not(exists(start why ?x)))
    (preference explanation ?first $?other)
    =>
    (printout t "FIRED: " "why-prediction-available" crlf)
    (retract ?w)
    (assert(input ui why-calc))
    (assert(start why ?first))
)

;Asking the why question and having made a prediciton
;Preference is rule
(defrule why-rule
    ?w <- (input ui why-calc)
    (list (name predictions) (content ?head $?tail))
    (preference explanation rule $?other)
    (test(neq nil ?head))
    =>
    (printout t "FIRED: " "why-rule" crlf)
    (retract ?w)
    (bind ?f (fact-slot-value ?head features))
    (bind ?prediction-values (transform-feature-values ?f))
    (bind ?t (anchors_connector ?prediction-values))
    (if (eq ?t TRUE)
    then (assert (ui-state (text (getExplanation))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type skip)
                        (skip "input ui feedback")))
    else (assert (ui-state (text "...")
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type skip)
                        (skip "input feedback-ask no")))
    )
    
    ;(assert (input active-rule ?rule))
)

;Asking the why question and having made a prediciton
;Preference is attribution
(defrule why-attribution
    ?w <- (input ui why-calc)
    (list (name predictions) (content ?head $?tail))
    (preference explanation attribution $?other)
    (test(neq nil ?head))
    => 
    (printout t "FIRED: " "why-attribution" crlf)
    (retract ?w)
    (bind ?f (fact-slot-value ?head features))
    (bind ?prediction-values (transform-feature-values ?f))
    (bind ?t (fact-slot-value ?head prediction-outcome))
    (bind ?t (shap_why_connector ?t ?prediction-values))
    (assert (ui-state (text (getExplanation))
                        (image-url ?t)
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type skip)
                        (skip "input ui feedback")))
)

;Asking the why question and having made a prediciton
;Preference is cf
(defrule why-counterfactual
    ?w <- (input ui why-calc)
    (list (name predictions) (content ?head $?tail))
    (preference explanation counterfactual $?other)
    (test(neq nil ?head))
    (foil ?first-foil $?other-foils)
    =>
    (printout t "FIRED: " "why-counterfactual" crlf)
    (retract ?w)
    (bind ?f (fact-slot-value ?head features))
    (bind ?p (fact-slot-value ?head prediction-outcome))
    (bind ?t nil)
    (bind ?prediction-values (transform-feature-values ?f))
    (if (eq (fact-slot-value ?head prediction-outcome) ?first-foil)
    then 
        (bind ?t (nth$ 1 ?other-foils))
    else 
        (bind ?t ?first-foil))
    (bind ?cf (cf_proto_why_connector ?t ?prediction-values))
    (if (neq ?cf nil)
    then (assert (ui-state (text ?cf)
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type skip)
                        (skip "input ui feedback")))
    else (assert (ui-state (text ?t)
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type skip)
                        (skip "input feedback-ask no")))
    )
    
    ;(assert (input active-rule ?rule))
)

;Feedback question
(defrule why-feedback
    ?f <- (input ui feedback)
    =>
    (printout t "FIRED: " "why-feedback" crlf)
    (retract ?f)
    (assert (ui-state (text (str-cat "If you haven't enough yet, I can generate another explanation for you. Shall I?") (str-cat "Do you want to see another explanation?") (str-cat "Shall I try a different explanation approach?"))
                        (valid-answers "{'type' : 'selection', 'value' : ['yes', 'no']}")
                        (clips-type "symbol")
                        (clipboard "''")
                        (fact-type "input feedback-ask ")))
)

;Reset system state if satisfied
(defrule why-feedback-no
    ?y <- (input feedback-ask no)
    ?s <- (start why ?x)
    => 
    (printout t "FIRED: " "why-feedback-no" crlf)
    (retract ?y)
    (retract ?s)
    (assert (ui-state (text (str-cat "All right &#128522;.") (str-cat "Okay &#128522;."))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)

;if there is no more to offer
(defrule why-feedback-yes-more-pref
    ?y <- (input feedback-ask yes)
    ?p1 <- (preference explanation ?z1 nil)
    ?s <- (start why ?x)
    => 
    (printout t "FIRED: " "why-feedback-yes-more-pref" crlf)
    (retract ?y)
    (retract ?s)
    (assert (ui-state (text (str-cat "Sorry, there is nothing more I can offer you. Maybe you can enter another question.") (str-cat "There is nothing more for the moment. Try another question."))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)

;if there is no more to offer if feedback loop is finished
(defrule why-feedback-loop-finished
    ?y <- (input feedback-ask yes)
    ?p1 <- (preference explanation ?z1 ?z2 $?other)
    ?s <- (start why ?x)
    (test(eq ?x ?z2))
    => 
    (printout t "FIRED: " "why-feedback-loop-finished" crlf)
    (retract ?y)
    (retract ?s)
    (assert (ui-state (text (str-cat "Sorry, there is nothing more I can offer you. Maybe you can enter a different question.") (str-cat "There is nothing more for the moment. Try a different question."))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)

;Changes the explanation type
(defrule why-feedback-alter-pred
    ?y <- (input feedback-ask yes)
    ?p1 <- (preference explanation ?z1 ?z2 $?other)
    ?s <- (start why ?x)
    (test(neq ?x ?z2))
    => 
    (printout t "FIRED: " "why-feedback-alter-pred" crlf)
    (retract ?y)
    (retract ?p1)
    (assert(preference explanation ?z2 ?other ?z1))
    (assert (ui-state (text "Okay, let me try something else &#129300." "Maybe I try this &#129300.")
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type skip)
                        (skip "input ui why-calc")))
)