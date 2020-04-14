;Predict me something without having a data record. It will trigger the question if the user wants to provide some data
;Condition: prediction command + no predictions in prediction list + there is no new prediction
;Result: Question if values should be queried
(defrule predict-without-data-available
    ?p <- (input ui predict)
    (list (name predictions) (content nil))
    (not(exists(prediction (features $?f2) (prediction-outcome nil))))
    => 
    ;(retract ?p)
    (assert (ui-state (text (str-cat "I can do that for you. But first I need some information from you."))
                        (valid-answers "{'type' : 'selection', 'value' : ['yes', 'no']}")
                        (clips-type "symbol")
                        (clipboard "''")
                        (fact-type "input predict-ask ")))
)

;Will trigger asking for values and later calculation of prediction
;Condition: predict-without-data-available was answered with yes
;Result: values-one-by-one and calculation prediction
(defrule predict-without-data-available-ask-yes
    ?a <- (input predict-ask yes)
    =>
    (retract ?a)
    (assert(input ui values-one-by-one))
    (assert(input ui calc-predict))
)

;Will cancel and go back to ui
;Condition: predict-without-data-available was answered with no
;Result: Will cancel and go back to ui (bottom catcher)
(defrule predict-without-data-available-ask-no
    ?a <- (input predict-ask no)
    ?p <- (input ui predict)
    =>
    (retract ?p)
    (retract ?a)
)

;Directly output a prediction if any data is available
;Condition: Predict command + There is prediction in predictions list +(OR) prediction where no outcome exists yet
;Result: Calculation is triggered
(defrule predict-with-data-available
    ?p <- (input ui predict)
    (or (not(exists(list (name predictions) (content nil))))
        (exists(prediction (features $?f2) (prediction-outcome nil)))
    )
    =>
    (retract ?p)
    (assert(input ui calc-predict))
)

;Prediction when new data is available and its the first time something is predicted. Will hint for new node and wont calculate difference.
;Condition: Calculation command (data available) + a prediction with no outcome is available + no entry in prediction list
;Result: a prediction is calculated + prediction is modified + skip to ui node
;Salience: Important because otherwise would calculate with missing data
(defrule calculate-prediction-new-data-first-time
    (declare (salience ?*low-priority*))
    ?i <- (input ui calc-predict)
    ?p <- (prediction (features $?f2) (prediction-outcome nil))
    ?l <- (list (name predictions) (content $?c))
    (test(member$ nil ?c))
    =>
    (retract ?i)
    (bind ?prediction-values (transform-feature-values ?f2))
    (bind ?prediction (predict_connector ?prediction-values))
    (modify ?p (prediction-outcome ?prediction))
    (assert (ui-state (text (str-cat "I predicted a value for you: <big>" ?prediction "</big>.")
                        (str-cat "The value I predicted for you is: <big>" ?prediction "</big>."))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard (str-cat "{'id' : 'prediction', 'value' : '" (get-feature-values-for-clipboard ?f2) " Prediction: " ?prediction"'}"))
                        (fact-type skip)
                        (skip "input ui node")))
)

;Prediction when new data is available it requires a new calculation
;Condition: Calculation command (data available) + a prediction with no outcome is available + there is an entry in the prediction list
;Result: a prediction is calculated + prediction is modified + skip to difference hint
;Salience: Important because otherwise would calculate with missing data
(defrule calculate-prediction-new-data
    (declare (salience ?*low-priority*))
    ?i <- (input ui calc-predict)
    ?p <- (prediction (features $?f2) (prediction-outcome nil))
    ?l <- (list (name predictions) (content $?c))
    (not(test(member$ nil ?c)))
    =>
    (retract ?i)
    (bind ?prediction-values (transform-feature-values ?f2))
    (bind ?prediction (predict_connector ?prediction-values))
    (modify ?p (prediction-outcome ?prediction))
    (assert (ui-state (text (str-cat "I predicted a value for you: <big>" ?prediction "</big>.")
                        (str-cat "The value I predicted for you is: <big>" ?prediction "</big>."))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard (str-cat "{'id' : 'prediction', 'value' : '" (get-feature-values-for-clipboard ?f2) " Prediction: " ?prediction"'}"))
                        (fact-type skip)
                        (skip "input ui hint-new-prediction")))
)

;Prediction when no new data is available
;Condition: Calculation command + There is no prediction with no prediction outcome + There is at least one entry in prediction list
;Result: Latest prediction outcome presented
;Salience: Important because otherwise would calculate with missing data
(defrule calculate-prediction-no-new-data
    (declare (salience ?*low-priority*))
    ?i <- (input ui calc-predict)
    (not(exists(prediction (features $?f2) (prediction-outcome nil))))
    ?l <- (list (name predictions) (content $?c))
    (not(test(member$ nil ?c)))
    =>
    (retract ?i)
    (bind ?latest (nth$ 1 ?c))
    (assert (ui-state (text (str-cat "The prediction is still: <big>" (fact-slot-value ?latest prediction-outcome) "</big>.")
                            (str-cat "You didn't change any values: <big>" (fact-slot-value ?latest prediction-outcome) "</big>."))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)

;Archive a new prediction
;Condition: prediction with prediction-outcome + prediction not already archived (in list)
;Result: modifies prediction list
;Salience: Most important that it get archived
(defrule archive-prediction
    (declare (salience ?*super-high-priority*))
    ?p <- (prediction (features $?f) (prediction-outcome ?o&~nil))      
    ?l <- (list (name predictions) (content $?c)) 
    (not(test(member$ ?p ?c))) ;p darf nicht in content sein
    =>
    ;(assert (input ui hint-new-prediction))
    (if (eq (nth$ 1 ?c) nil)
        then 
            (modify ?l (content ?p))
        else 
            (modify ?l (content ?p ?c)))
)

;Hint if there was a difference
;Condition: hint command
;Result: Comparing outcomes and giving answer
(defrule hint-new-prediction-difference
    ?i <- (input ui hint-new-prediction)
    ?l <- (list (name predictions) (content $?c))
    =>
    (retract ?i)
    (bind ?f (nth$ 1 ?c))
    (bind ?s (nth$ 2 ?c))
    (printout t (fact-slot-value ?f prediction-outcome) crlf)
    (printout t (fact-slot-value ?s prediction-outcome) crlf)
    (if (eq (fact-slot-value ?f prediction-outcome) (fact-slot-value ?s prediction-outcome))
        then (assert (ui-state (text (str-cat "There is no change in the prediction."))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
        else (assert (ui-state (text (str-cat "There is a change in the prediction."))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
    )
)


; (defrule hint-new-prediction-difference
;     (declare (salience ?*high-priority*))
;     ?i <- (input ui hint-new-prediction)
;     (memory prediction-outcome ?q)
;     (memory previous-prediction-outcome ?p)
;     =>
;     (retract ?i)
;     (assert (ui-state (text (str-cat "Check out the following: This prediction is different from the previous one after you changed <big>" "(getDifferencePredictionValues ?s1 ?s2)" "</big>."))
;                         (valid-answers "''")
;                         (suggested-answers "")
;                         (clipboard "''")
;                         (fact-type ui)))
; )

; ;Calculate the first prediction
; ;Conditions: Calculation request + values for all features are available + no prediction outcome available + no previous prediction outcome availabe
; ;Return: Prediction and new node on clipboard
; (defrule calculate-prediction
;     ?i <- (input ui calc-predict)
;     (not(exists(feature(value nil))))
;     (not(exists(memory prediction-outcome ?o1)))
;     (not(exists(memory previous-prediction-outcome ?o2)))
;     =>
;     (retract ?i)
;     (bind ?prediction-values (transform-feature-values))    
;     (bind ?prediction (custom_predict ?prediction-values))
;     (assert(memory prediction-outcome ?prediction))
;     (assert (ui-state (text (str-cat "I predicted a value for you: <big>" ?prediction "</big>.")
;                             (str-cat "The value I predicted for you is: <big>" ?prediction "</big>."))
;                         (valid-answers "''")
;                         (suggested-answers "")
;                         (clipboard (str-cat "{'id' : 'prediction', 'value' : '" (createPrettyFeatureValuesforClipboard ?prediction-values) " Prediction:" ?prediction"'}"))
;                         (fact-type skip)
;                         (skip "ui node")))
; )

; ;Calculate prediction after no new values were entered
; ;Conditions: Calculation request + prediction outcome exists (then no new values were entered, otherwise it would be shifted to previous)
; ;Result: Hint that prediction is still the same as before
; (defrule calculate-prediction-no-changes-in-values
;     ;(declare (salience ?*medium-high-priority*)) ;because first need to collect new data
;     ?i <- (input ui calc-predict)
;     (memory prediction-outcome ?o)
;     =>
;     (retract ?i)
;     (assert (ui-state (text (str-cat "The prediction is still: <big>" ?o "</big>.")
;                             (str-cat "You didn't change any values: <big>" ?o "</big>."))
;                         (valid-answers "''")
;                         (suggested-answers "")
;                         (clipboard "''")
;                         (fact-type ui)))
; )

; ;Calculate a prediction if there was made a prediction before
; ;Conditions: Calculation request + there exists a previous prediction value + there is new data (no prediction outcome exists)
; ;Return: Prediction and skip to hint comparing to previous prediction
; (defrule calculate-prediciton-one-outcome-available
;     ?i <- (input ui calc-predict)
;     ?q <- (memory previous-prediction-outcome ?p)
;     (not(exists(memory prediction-outcome ?o)))
;     =>
;     (retract ?i)
;     (bind ?prediction-values (transform-feature-values))    
;     (bind ?prediction (custom_predict ?prediction-values))
;     (assert(memory prediction-outcome ?prediction))
;     (assert (ui-state (text (str-cat "I predicted a value for you: <big>" ?prediction "</big>.")
;                             (str-cat "The value I predicted for you is: <big>" ?prediction "</big>."))
;                         (valid-answers "''")
;                         (suggested-answers "")
;                         (clipboard (str-cat "{'id' : 'prediction', 'value' : '" (createPrettyFeatureValuesforClipboard ?prediction-values) " Prediction:" ?prediction"'}"))
;                         (fact-type skip)
;                         (skip "ui hint-new-prediction")))
; )

; ;Calculate a prediction if there was made two predictions before. Overwrite value in memory
; ; (defrule calculate-prediciton-two-outcome-available
; ;     (declare (salience ?*super-low-priority*))
; ;     ?i <- (input ui calc-predict)
; ;     ?q1 <- (memory prediction-outcome ?p1)
; ;     ?q2 <- (memory previous-prediction-outcome ?p2)
; ;     =>
; ;     (retract ?i)
; ;     (retract ?q1)
; ;     (retract ?q2)
; ;     (bind ?prediction-values (transform-feature-values))    
; ;     (bind ?prediction (custom_predict ?prediction-values))
; ;     (assert(memory prediction-outcome ?prediction))
; ;     (assert(memory previous-prediction-outcome ?p1))
; ;     (assert (ui-state (text (str-cat "I predicted a value for you: <big>" ?prediction "</big>.")
; ;                             (str-cat "The value I predicted for you is: <big>" ?prediction "</big>."))
; ;                         (valid-answers "''")
; ;                         (suggested-answers "")
; ;                         (clipboard (str-cat "{'id' : 'prediction', 'value' : '" (createPrettyFeatureValuesforClipboard ?prediction-values) " Prediction:" ?prediction"'}"))
; ;                         (fact-type skip)
; ;                         (skip "ui hint-new-prediction")))
; ; )



; ;Calculate a prediction for whatif
; (defrule calculate-prediciton-whatif
;     (memory whatif-values $?s)
;     =>
;     (bind ?prediction (custom_predict ?s))
;     (assert (ui-state (text (str-cat "If it was as you told me, the prediction is: " ?prediction "."))
;                         (valid-answers "''")
;                         (suggested-answers "")
;                         (fact-type ui)))
; )