;what if in case there are no prediction values in prediction list
;Condition: whatif command + no prediction in prediction list
;Result: require values and calc request
(defrule whatif-no-data
    ?o <- (input ui whatif)
    ?l <- (list (name predictions) (content $?c))
    (test(member$ nil ?c))
    =>
    ; (printout t "FIRED: " "whatif-no-data" crlf)
    (retract ?o)
    (assert(input ui require))
    (assert(input ui calc-predict))
)

;what if in case there is a prediction in list. Will simulate user input of feature values equal to the last prediction. Values are then later exchanged.
;Condition: whatif command + a prediction in prediction list
;Result: Simulating user input over all feature values of the latest prediction + switch to select
(defrule whatif-data-available
    ?o <- (input ui whatif)
    ?l <- (list (name predictions) (content $?c))
    (test(not(member$ nil ?c)))
    =>
    ; (printout t "FIRED: " "whatif-data-available" crlf)
    (retract ?o)
    (bind ?features-first (fact-slot-value (nth$ 1 ?c) features))
    (loop-for-count (?cnt 1 (length$ ?features-first)) do
        (assert(input user-value (fact-slot-value (nth$ ?cnt ?features-first) name) (fact-slot-value (nth$ ?cnt ?features-first) value) ))
    )
    (assert(input ui select))
)

;what if in case user provided parameters but there are no prediction values in prediction list
;Condition: whatif command with parameters + no prediction in prediction list
;Result: predict is fired which will ask user to provide data first
(defrule whatif-usr-input-available-no-data
    ?o <- (input ui whatif $?usrinput)
    ?l <- (list (name predictions) (content $?c))
    (test(member$ nil ?c))
    (test(not(member$ nil ?usrinput)))
    =>
    ; (printout t "FIRED: " "whatif-data-available" crlf)
    (retract ?o)
    (assert(input ui predict))
)

;what if in case there is a prediction in list and user provided parameters. Will simulate user input of feature values equal to the last prediction. Values are then later exchanged.
;Condition: whatif command with parameters + a prediction in prediction list
;Result: Simulating user input over all feature values of the latest prediction + switch to select
(defrule whatif-usr-input-available
    ?o <- (input ui whatif $?usrinput)
    ?l <- (list (name predictions) (content $?c))
    (test(not(member$ nil ?c)))
    (test(not(member$ nil ?usrinput)))
    =>
    ; (printout t "FIRED: " "whatif-data-available" crlf)
    (retract ?o)
    (bind ?features-first (fact-slot-value (nth$ 1 ?c) features))
    (loop-for-count (?cnt 1 (/ (length$ ?usrinput) 2)) do 
        (bind ?usrkey (nth$ (- (* ?cnt 2) 1) ?usrinput))
        (bind ?usrval (nth$ (* ?cnt 2) ?usrinput))
        (printout t "asserting (" ?cnt "/" (/ (length$ ?usrinput) 2) "): input user-value " ?usrkey " " ?usrval)
        (assert(input user-value ?usrkey ?usrval))
        (printout t " was asserted" crlf)
    )
    (loop-for-count (?cnt 1 (length$ ?features-first)) do
        (assert(input user-value (fact-slot-value (nth$ ?cnt ?features-first) name) (fact-slot-value (nth$ ?cnt ?features-first) value) ))
    )
    (assert(input whatif anymore))
)


;Asks to select a feature to change
;Condition: select command
;Result: Asking and switch to anymore
;Salience: Must be lower than transform-prediction, because otherwise replace wouldnt work
(defrule whatif-values-select-feature
    (declare (salience ?*low-priority*))
    ?o <- (input ui select)
    =>
    ; (printout t "FIRED: " "whatif-data-available" crlf)
    (retract ?o)
    (assert(input whatif anymore))
    (assert (ui-state (text "I need you to select a feature:")
                        (valid-answers (get-valid-answers-for-features))
                        (clips-type "symbol")
                        (clipboard "''")
                        (fact-type "input require ")))
)

;Ask if to change anymore
;Condition: anymore command
;Result: Ask anymore
;Salience: Must be lower than transform-prediction, because otherwise replace wouldnt work
(defrule whatif-values-anymore
    ;(declare (salience ?*medium-low-priority*))
    ?a <- (input whatif anymore)
    =>
    ; (printout t "FIRED: " "whatif-data-available" crlf)
    (retract ?a)
    (assert (ui-state (text "Any more?")
                        (valid-answers "{'type' : 'selection', 'value' : ['yes', 'no']}")
                        (clips-type "symbol")
                        (clipboard "''")
                        (fact-type "input whatif-asked")))
)

;Answered anymore with yes
;Condition: whatif-asked yes
;Result: Switch to select again
(defrule whatif-values-ask-yes
    ?a <- (input whatif-asked yes)
    =>
    ; (printout t "FIRED: " "whatif-data-available" crlf)
    (retract ?a)
    (assert(input ui select))
)

;Answered anymore with no
;Condition: whatif-asked no
;Result: Trigger calculation
(defrule whatif-values-ask-no
    ?a <- (input whatif-asked no)
    ;?o <- (input ui whatif)
    =>
    ; (printout t "FIRED: " "whatif-data-available" crlf)
    (retract ?a)
    (assert(input ui calc-predict))
    ;(retract ?o)
)

;Salience: Must be lower than transform-prediction
; (defrule whatif-build
;     (declare (salience ?*low-priority*))
;     ?o <- (input ui whatif)
;     ?p <- (prediction (features $?f2) (prediction-outcome nil))
;     ?l <- (list (name predictions) (content $?c)) 
;     =>
;     (retract ?o)
;     (printout t "Make whatif" crlf)
;     ;(assert (prediction (features (nth$ 1 ?c)) (prediction-outcome nil)))
;     ;get first of prediction list
;     ;must assert calc-predict
;     ;also exchange values if they get corrected (no duplicates)
; )

; (defrule transform-single-whatif-values
;     (declare (salience ?*medium-low-priority*))
;     ?f <- (input user-value ?x ?y)
;     ?g <- (input whatif-values-build $?k)
;     =>
;     (retract ?g)
;     (retract ?f)
;     (assert(input whatif-values-build ?k (str-cat ?x ":" ?y)))
; )

; (defrule build-whatif-values
;     (declare (salience ?*super-low-priority*))
;     ?b <- (input whatif-values-build $?k)
;     ?p <- (memory prediction-values $?s)
;     =>
;     (retract ?b)
;     (retract ?p)
;     (assert(input ui calc-predict))
;     (assert(memory previous-prediction-values $?s))
;     (createWhatIf ?k ?s)
; )

; (defrule build-whatif-values-previous-available
;     (declare (salience ?*low-priority*))
;     ?b <- (input whatif-values-build $?k)
;     ?p1 <- (memory prediction-values $?s1)
;     ?p2 <- (memory previous-prediction-values $?s2)
;     =>
;     (retract ?b)
;     (retract ?p1)
;     (retract ?p2)
;     (assert(input ui calc-predict))
;     (assert(memory previous-prediction-values ?s1))
;     (createWhatIf ?k ?s1)
; )