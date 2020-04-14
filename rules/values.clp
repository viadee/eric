;Will trigger asking the user to provide values for each feature
;Condition: Request
;Result: Anouncement and require-facts for each feature
(defrule values-one-by-one
    ?o <- (input ui values-one-by-one)
    (not(exists(prediction (features $?f2) (prediction-outcome nil))))
    =>
    (retract ?o)
    (assert (ui-state (text "Ok, I will now ask you to provide a value for each feature one by one.." "Alright, I will need some values from you..")
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type skip)
                        (skip "input ui require"))) ;can be left blank! Will not assign any new fact then. Alternative: Allow skip to assign multiple facts or new rule that does assignment
)

;Will trigger asking the user to provide values for each feature
;Condition: Request + feature values were provided but no prediction was calculated
;Result: Anouncement and require-facts for each feature + will delete current feature values
(defrule values-one-by-one-overwrite
    ?o <- (input ui values-one-by-one)
    ?p <- (prediction (features $?f2) (prediction-outcome nil))
    =>
    (retract ?o)
    (retract ?p)
    (assert (ui-state (text "Ok, I will now ask you to provide a new value for each feature one by one.." "Alright, I will need some new values from you..")
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type skip)
                        (skip "input ui require"))) ;can be left blank! Will not assign any new fact then
)

(defrule require-feature-values
    ?r <- (input ui require)
    =>
    (retract ?r)
    (bind ?l nil)
    (do-for-all-facts ((?w feature-meta)) TRUE
        (if (eq ?l nil)
        then (bind ?l ?w:name)
        else (bind ?l ?w:name ?l)
        )
        ;(assert(input require ?w:name))
    )
    (loop-for-count (?cnt 1 (length$ ?l)) do
        (assert(input require (nth$ ?cnt ?l)))
    )
)

;Values one by one, if data record is already available, will overwrite (retract) existing record. 
;Will trigger a python method which inserts a fact per feature. Each of these facts will trigger an ui-state that asks for a feature value
; (defrule values-one-by-one-data-available
;     ?o <- (input ui values-one-by-one)
;     (not(exists(feature(value nil))))
;     =>
;     (retract ?o)
;     (do-for-all-facts ((?w feature)) TRUE
;                         (assert(input require ?w:name)))
;     (assert (ui-state (text "Ok, I will now ask you to provide a value for each feature one by one..test" "Alright, I will need some values from you..test")
;                         (valid-answers "''")
;                         (suggested-answers "")
;                         (clipboard "''")
;                         (fact-type skip)
;                         (skip "prediction-values-build")))
; )

;Triggers an ui-state that asks for a user input for a feature value
;Condition: Require fact issued
;Result: ui-state asking the user for value
(defrule single-feature-value
    ?v <- (input require ?x)
    =>
    (retract ?v)
    (assert (ui-state (text (str-cat "Please provide some value for " ?x ".") (str-cat "I need to know what value " ?x " takes.") (str-cat "What is the value for " ?x "?"))
                        (valid-answers (getValidAnswersForFeatureValues ?x))
                        (clips-type (get-data-type-for-feature ?x))
                        (clipboard "''")
                        (fact-type (str-cat "input user-value " ?x))))
)


; (defrule transform-single-prediction-values-no-data-available-no-prediction-outcome-available
;     (declare (salience ?*super-low-priority*))
;     ?f <- (input user-value ?x ?y)
;     ?f2 <- (feature (name ?x) (value ?z))
;     =>
;     (modify ?f2 (value ?y))
;     (retract ?f)
; )

;Transforms the user input into a feature instance. 
;Condition: user input
;Result: Feature instance
(defrule transform-single-user-values
    ?f <- (input user-value ?x ?y)
    =>
    (assert(feature-instance (name ?x) (value ?y)))
)

;Transforms the feature instances into a prediction
;Condition: no prediction exists
;Result: Create a prediction and insert first feature instance
;Salience: Must be lower than transform-single-user-values
(defrule transform-prediction-first-time
    ;(declare (salience ?*medium-low-priority*))
    ?f <- (input user-value ?x ?y)
    ?f1 <- (feature-instance (name ?x) (value ?y))
    (not(exists(prediction (features $?f2) (prediction-outcome nil))))
    =>
    ;(printout t "FFFFFFFFF" crlf) 
    (retract ?f)
    (assert(prediction (features ?f1) (prediction-outcome nil)))
)

;Transforms the feature instances into a prediction
;Condition: prediction exists already
;Result: Insert next feature instance or replace existing feature instance (for whatif)
;Salience: Must be lower than transform-single-user-values
(defrule transform-prediction
    ;(declare (salience ?*medium-low-priority*))
    ?f <- (input user-value ?x ?y)
    ?f1 <- (feature-instance (name ?x) (value ?y))
    ?p <- (prediction (features $?f2) (prediction-outcome nil))
    =>
    (retract ?f)
    (bind ?new-features ?f2)
    (bind ?replace FALSE)
    (loop-for-count (?cnt 1 (length$ ?f2)) do ;for whatif: will exchange values in features if double entries
        (if (eq (fact-slot-value (nth$ ?cnt ?f2) name) ?x)
            then 
                (bind ?new-features (replace$ ?new-features ?cnt ?cnt ?f1))
                ;(printout t "REPLACE" crlf)
                ;(printout t ?new-features crlf)
                (bind ?replace TRUE)
        )
    )
    (if (eq ?replace FALSE);wrong condition
        then 
            (bind ?new-features (insert$ ?new-features 1 ?f1))
            ;(printout t "INSERT" crlf)
    )
    ;(printout t ?new-features crlf)
    ;(printout t "FInished" crlf)
    (retract ?p)
    (assert(prediction (features ?new-features) (prediction-outcome nil)))
    ;(modify ?p (features ?new-features) (prediction-outcome nil))
    ;for whatif: if ?f1:name already exists in ?f2 --> exchange
)

; (defrule test
;     (declare (salience ?*super-low-priority*))
;     ?p <- (prediction (features $?f2) (prediction-outcome nil))
;     =>
;     (bind ?g (nth$ 1 (first$ ?f2)))
;     (printout t (fact-slot-value ?g name) crlf)
; )

;Takes the single user-value facts which represent the user input per feature and exchanges the present values. 
;Condition: 
; (defrule transform-single-prediction-values-one-prediction-outcome-available
;     ?f <- (input user-value ?x ?y)
;     ?f2 <- (feature (name ?x) (value ?z))
;     ?q <- (memory prediction-outcome ?p1)
;     (not(exists(memory previous-prediction-outcome ?p2)))
;     =>
;     (retract ?q)
;     (retract ?f)
;     (assert(memory previous-prediction-outcome ?p1))
;     (modify ?f2 (value ?y) (previous-value ?z))
;     (printout t "RULE2" crlf)
; )

; ;Takes the single user-value facts which represent the user input per feature and exchanges the present values. 
; ;Condition: 
; (defrule transform-single-prediction-values-data-available-two-prediction-outcome-available
;     ?f <- (input user-value ?x ?y)
;     ?f2 <- (feature (name ?x) (value ?z))
;     ?q1 <- (memory prediction-outcome ?p1)
;     ?q2 <- (memory previous-prediction-outcome ?p2)
;     =>
;     (retract ?q1)
;     (retract ?q2)
;     (retract ?f)
;     (assert(memory previous-prediction-outcome ?p1))
;     (modify ?f2 (value ?y) (previous-value ?z))
;     (printout t "RULE3" crlf)
; )

; (defrule transform-single-prediction-values-one-prediction-outcome-available
;     ?f <- (input user-value ?x ?y)
;     ?f2 <- (feature (name ?x) (value ?z))
;     (not(exists(memory prediction-outcome ?p1)))
;     ?q <- (memory prediction-outcome ?p2)
;     =>
;     (retract ?q)
;     (retract ?f)
;     (modify ?f2 (value ?y) (previous-value ?z))
;     (printout t "RULE4" crlf)
; )

;Transforms the intermediate variable "prediction-values-build" into "prediction-values" which is used in other rules.
; (defrule build-prediction-values
;     (declare (salience ?*low-priority*))
;     ?b <- (input prediction-values-build $?k)
;     =>
;     (retract ?b)
;     (assert (memory prediction-values $?k))
; )