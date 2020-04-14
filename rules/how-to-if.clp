;support equal, equal-bigger, bigger, equal-smaller, smaller, set
(defrule how-to-if-no-prediction-available
    ?o <- (input ui how-to-if)
    (list (name predictions) (content nil))
    =>
    (retract ?o)
    (do-for-all-facts ((?w feature-meta)) TRUE
        (assert(input user-value ?w:name (nth$ 1 ?w:values)))
    ) 
    (assert (ui-state (text "What value should the prediction take? Select the 'Y'.")
                        (valid-answers (str-cat "{'type' : 'selection', 'value' : [" (get-target-values-as-string) "]}"))
                        (clips-type "string")
                        (clipboard "''")
                        (fact-type "input howto-value ")))
    (assert(input ui how-to-select))
)

(defrule how-to-if-prediction-available
    ?o <- (input ui how-to-if)
    (list (name predictions) (content ?head $?tail))
    (test(neq nil ?head))
    =>
    (retract ?o)
    (bind ?features-first (fact-slot-value ?head features))
    (loop-for-count (?cnt 1 (length$ ?features-first)) do 
        (assert(input user-value (fact-slot-value (nth$ ?cnt ?features-first) name) (fact-slot-value (nth$ ?cnt ?features-first) value) ))
    )
    (assert (ui-state (text "What value should the prediction take? Select the 'Y'.")
                        (valid-answers (str-cat "{'type' : 'selection', 'value' : [" (get-target-values-as-string) "]}"))
                        (clips-type "string")
                        (clipboard "''")
                        (fact-type "input howto-value ")))
    (assert(input ui how-to-select))
)

(defrule how-to-values-select-feature
    (declare (salience ?*low-priority*))
    ?v <- (input ui how-to-select)
    =>
    (retract ?v)
    (assert(input how-to anymore))
    (assert (ui-state (text "I need you to select a feature. Select the 'X'.")
                        (valid-answers (getValidAnswersForFeatures))
                        (clips-type "symbol")
                        (clipboard "''")
                        (fact-type "input require-howto ")))
)

(defrule single-feature-value-how-to
    ?v <- (input require-howto ?x)
    (not(exists(input fixate $?k)))
    =>
    (retract ?v)
    (assert(input fixate ?x))
    (assert (ui-state (text (str-cat "Please provide some value for " ?x ".") (str-cat "I need to know what value " ?x " takes.") (str-cat "What is the value for " ?x "?"))
                        (valid-answers (getValidAnswersForFeatureValues ?x))
                        (clips-type (getDataTypeForFeature ?x))
                        (clipboard "''")
                        (fact-type (str-cat "input user-value " ?x))))
)

(defrule single-feature-value-how-to-fixate
    ?v <- (input require-howto ?x)
    ?f <- (input fixate $?k)
    =>
    (retract ?v)
    (retract ?f)
    (assert(input fixate ?k ?x))
    (assert (ui-state (text (str-cat "Please provide some value for " ?x ".") (str-cat "I need to know what value " ?x " takes.") (str-cat "What is the value for " ?x "?"))
                        (valid-answers (getValidAnswersForFeatureValues ?x))
                        (clips-type (getDataTypeForFeature ?x))
                        (clipboard "''")
                        (fact-type (str-cat "input user-value " ?x))))
)

(defrule how-to-values-anymore
    ?a <- (input how-to anymore)
    =>
    (retract ?a)
    (assert (ui-state (text "Any more feature you want to fixate?")
                        (valid-answers "{'type' : 'selection', 'value' : ['yes', 'no']}")
                        (clips-type "symbol")
                        (clipboard "''")
                        (fact-type "input how-to-asked")))
)

(defrule how-to-values-ask-yes
    ?a <- (input how-to-asked yes)
    =>
    (retract ?a)
    (assert(input ui how-to-select))
)

(defrule how-to-values-ask-no
    ?a <- (input how-to-asked no)
    =>
    (retract ?a)
    (assert(input ui calc-counterfactual))
)

(defrule calculate-counterfactual-how-to-if
    ?c <- (input ui calc-counterfactual)
    ?p <- (prediction (features $?f2) (prediction-outcome nil))
    ?h <- (input howto-value ?f1)
    ?f <- (input fixate $?x)
    =>
    (retract ?c)
    (retract ?h)
    (retract ?f)
    (bind ?prediction-values (transform-feature-values ?f2))
    (bind ?fixated-values (transform-fixated-values ?x))
    (printout t ?prediction-values crlf)
    (printout t ?fixated-values crlf)
    (bind ?counterfactual (getCounterfactual ?f1 ?prediction-values ?fixated-values))
    (printout t ?counterfactual crlf)

    (bind ?counter 1)
    (while (< ?counter (length$ ?counterfactual))
        
        (printout t (nth$ ?counter ?counterfactual) crlf)
        (printout t (nth$ (+ ?counter 1) ?counterfactual) crlf)
        (assert(input user-value (sym-cat (nth$ ?counter ?counterfactual)) (nth$ (+ ?counter 1) ?counterfactual)))

        (bind ?counter (+ ?counter 2))
    )
    (assert(input ui calc-counter))
)

(defrule calculate-counterfactual
    (declare (salience ?*low-priority*))
    ?i <- (input ui calc-counter)
    ?p <- (prediction (features $?f2) (prediction-outcome nil))
    ?l <- (list (name predictions) (content $?c))
    =>
    (retract ?i)
    (bind ?prediction-values (transform-feature-values ?f2))
    (bind ?prediction (custom_predict ?prediction-values))
    (modify ?p (prediction-outcome ?prediction))
    (assert (ui-state (text (str-cat "I predict <big>" ?prediction "</big> if the values were the following: "))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard (str-cat "{'id' : 'prediction', 'value' : '" (get-feature-values-for-clipboard ?f2) " Prediction: " ?prediction"'}"))
                        (fact-type "input ui")))
)
