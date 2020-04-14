(defglobal
    ?*super-high-priority* = 1000
    ?*high-priority* = 500
    ?*medium-high-priority* = 100
    ?*medium-low-priority* = -100
    ?*low-priority* = -500
    ?*super-low-priority* = -1000
)

;template for chat message information (ui-state)
(deftemplate ui-state
    (multislot text)
    (slot image-url (default "''"))
    (slot valid-answers)
    (slot clips-type) ;symbol, string, numeric
    (slot clipboard)
    (slot fact-type)
    (slot skip)
)

;template for feature meta info
(deftemplate feature-meta
    (slot name)
    (slot data-type)
    (slot feature-type)
    (multislot values)
    (slot regex)
    (slot weight)
)

;template for target meta info
(deftemplate target-instance-meta
    (slot name)
    (slot weight)
)

;template for feature instance
(deftemplate feature-instance
    (slot name)
    (slot value)
)

;template for prediction
(deftemplate prediction
    (multislot features)
    (slot prediction-outcome)
    (slot timestamp (default-dynamic (getTimestamp)))
)

;template for list
(deftemplate list
    (slot name)
    (multislot content)
)

;template for rule (not used)
(deftemplate rule
    (multislot clauses)
    (slot result)
    (slot certainty)
)

;template for clause (not used)
(deftemplate clause
    (slot feature)
    (slot operator (type SYMBOL) (allowed-symbols
    eq gt gteq lt lteq))
    (slot value)
)

;sends a message to python
(deffunction send-message (?text ?image-url ?valid-answers ?clips-type ?clipboard ?fact-type ?skip);arg
    (bind ?random (get_random_text_slot 1 (length$ ?text)))
    (bind ?random_text (nth$ ?random ?text))
    (message_from_clips ?random_text ?image-url ?valid-answers ?clips-type ?clipboard ?fact-type ?skip)
)

;transforms feature values into python json-like format
(deffunction transform-feature-values (?features)
    (bind ?prediction-values nil)
    (loop-for-count (?cnt 1 (length$ ?features)) do
        (bind ?name (fact-slot-value (nth$ ?cnt ?features) name))
        (bind ?value (fact-slot-value (nth$ ?cnt ?features) value))
        (if (eq ?prediction-values nil)
            then (bind ?prediction-values (str-cat ?name ":" ?value))
            else (bind ?prediction-values ?prediction-values (str-cat ?name ":" ?value))))

    ; (bind ?prediction-values nil)
    ; (do-for-all-facts ((?w feature)) TRUE ;concatenating feature values for python predict function
    ;                     (if (eq ?prediction-values nil)
    ;                     then (bind ?prediction-values (str-cat ?w:name ":" ?w:value))
    ;                     else (bind ?prediction-values ?prediction-values (str-cat ?w:name ":" ?w:value)))) 
    (return ?prediction-values)
)

(deffunction transform-fixated-values (?fixed)
    (bind ?fixated-values nil)
    (loop-for-count (?cnt 1 (length$ ?fixed)) do
        (if (eq ?fixated-values nil)
            then (bind ?fixated-values (str-cat "fixed:" (nth$ ?cnt ?fixed)))
            else (bind ?fixated-values (str-cat ?fixated-values "," (nth$ ?cnt ?fixed)))
        )
    )
    (return ?fixated-values)
)

;creates a string of feature names comma seperated
(deffunction get-feature-names-as-string ()
    (bind ?feature-names nil)
    (do-for-all-facts ((?w feature-meta)) TRUE ;concatenating feature names
                        (if (eq ?feature-names nil)
                        then (bind ?feature-names ?w:name)
                        else (bind ?feature-names (str-cat ?feature-names ", " ?w:name)))) 
    (return ?feature-names)
)

;creates a string of target values comma seperated
(deffunction get-target-values-as-string ()
    (bind ?target-values nil)
    (do-for-all-facts ((?w target-instance-meta)) TRUE ;concatenating feature names
                        (if (eq ?target-values nil)
                        then (bind ?target-values (str-cat "'" ?w:name "'"))
                        else (bind ?target-values (str-cat ?target-values ", " "'" ?w:name "'")))) 
    (return ?target-values)
)

(deffunction get-feature-values-for-clipboard (?prediction)
    (bind ?pretty "")
    (do-for-all-facts ((?w feature-meta)) TRUE ;concatenating feature names
        (loop-for-count (?cnt 1 (length$ ?prediction)) do
            (if (eq ?w:name (fact-slot-value (nth$ ?cnt ?prediction) name))
            then (bind ?pretty (str-cat ?pretty ?w:name ": " (fact-slot-value (nth$ ?cnt ?prediction) value) "<br/>"))
            )
        )
    ) 
    (return ?pretty)
)

(deffunction get-valid-answers-for-features ()
    (bind ?valid_answers nil)
    (do-for-all-facts ((?w feature-meta)) TRUE
        (if (eq ?valid_answers nil)
        then (bind ?valid_answers (str-cat "{'type' : 'selection', 'value' : ['" ?w:name "'"))
        else (bind ?valid_answers (str-cat ?valid_answers ", " "'" ?w:name "'"))
        )
    )
    (bind ?valid_answers (str-cat ?valid_answers "]}"))
    (return ?valid_answers)
)

(deffunction get-valid-answers-for-target ()
    (bind ?valid_answers nil)
    (do-for-all-facts ((?w target-instance-meta)) TRUE ;concatenating feature names
                        (if (eq ?valid_answers nil)
                        then (bind ?valid_answers (str-cat "{'type' : 'selection', 'value' : ['" ?w:name "'"))
                        else (bind ?valid_answers (str-cat ?valid_answers ", " "'" ?w:name "'")))) 
    (bind ?valid_answers (str-cat ?valid_answers "]}"))
    (return ?valid_answers)
)

(deffunction get-data-type-for-feature (?feature)
    (do-for-all-facts ((?w feature-meta)) TRUE
        (if(eq ?w:name ?feature)
        then (return ?w:data-type))
    )
    (return "string")
)

;triggered if there is a new ui-state
(defrule ui-state
    ?ui <- (ui-state (text $?m)
                        (image-url ?i)
                        (valid-answers ?va)
                        (clips-type ?ct)
                        (clipboard ?c)
                        (fact-type ?f)
                        (skip ?sk))
    =>
    (printFacts)
    (send-message ?m ?i ?va ?ct ?c ?f ?sk)
    (retract ?ui)
    (if(neq ?f skip)
        then
        (halt))
)

;triggered if init
(defrule init-first
    ?i <- (input ui init)
    =>
    ;(watch all)
    (retract ?i)
    (assert(memory init-asked))
    (assert (ui-state (text "Hi, I am ERIC, a Bot for XAI." "Hi, my name is ERIC.")
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)

(defrule init
    (declare (salience ?*medium-high-priority*))
    ?i <- (input ui init)
    ?a <- (memory init-asked)
    =>
    ;(watch all)
    (retract ?i)
    (assert (ui-state (text "Hi, I am still ERIC." "Hi, my name is still ERIC.")    
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)

;Bottom catcher

;Catch for wrong input
(defrule bottom-floor-catch-wrong-ui-input
    (declare (salience ?*super-low-priority*))
    ?x <- (input ui ?v)
    =>
    (retract ?x)
    (assert (ui-state (text "Sorry, this answer is not valid." "I do not get what you mean." "Can you try to say that again?")
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)

;Catch if user input and no follow up
(defrule bottom-floor-catch-user-value-input-and-no-followup
    (declare (salience ?*super-low-priority*))
    ?x <- (initial-fact)
    =>
    (retract ?x)
    (assert(initial-fact))
    (assert (ui-state (text "Alright." "Ok." "I understand.")
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)

;Display possible outcomes
(defrule targetvalues
    ?f <- (input ui targetvalues)
    =>
    (retract ?f)
    (resetCertainty)
    (assert (ui-state (text (str-cat "The outcome of my prediction can be one of: " (get-target-values-as-string)))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)

;Clear Bot's working memory
(defrule restart 
    (input ui restart)
    =>
    (reset)
    (assert (ui-state (text (str-cat "Yes, of cou.."))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type skip)
                        (skip "input ui init")))
)

;new node on clipboard
(defrule new-node
    (declare (salience ?*super-low-priority*))
    ?i <- (input ui node)
    =>
    ;(watch all)
    (retract ?i)
    (assert (ui-state (text "And I put a new node on the clipboard to your right." "By the way, there is a new node on the clipboard." "Pinned it to your clipboard.")
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
)

;Returns certainty if available
(defrule certainty
    ?f <- (input ui certainty)
    =>
    (retract ?f)
    (bind ?c (getCertainty))
    (if (neq ?c nil)
    then (assert (ui-state (text ?c)
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
    else (assert (ui-state (text (str-cat "About what?"))
                        (valid-answers "''")
                        (clips-type "''")
                        (clipboard "''")
                        (fact-type "input ui")))
    )
    
)

;Cancel will remove all the non-memory facts
; (defrule cancel1
;     (declare (salience ?*super-high-priority*)) 
;     ?c <- (input $?q cancel)
;     ?z <- (input $?x)
;     =>
;     (printout t "REMOVED" crlf)
;     (printout t ?x crlf)
;     (retract ?c)
;     (retract ?z)
;     ;(assert(input ui cancel))
; )

;Cancel will remove all the non-memory facts
; (defrule cancel2
;     (declare (salience ?*high-priority*)) 
;     ?c <- (input ui cancel)
;     =>
;     (retract ?c)
;     (assert (ui-state (text "Alright." "Ok." "I understand.")
;                         (valid-answers "''")
;                         (suggested-answers "")
;                         (clipboard "''")
;                         (fact-type ui)))
; )

; ;Cancel will remove all the non-memory facts
; (defrule cancel2
;     (declare (salience ?*super-high-priority*)) 
;     ?c <- (input ?q cancel)
;     ?z <- (input ?x ?y)
;     =>
;     (retract ?c)
;     (retract ?z)
;     (assert(input ui cancel))
; )

; ;Cancel will remove all the non-memory facts
; (defrule cancel3
;     (declare (salience ?*super-high-priority*)) 
;     ?c <- (input ?q cancel)
;     ?z <- (input ?x ?y ?v)
;     =>
;     (retract ?c)
;     (retract ?z)
;     (assert(input ui cancel))
; )

; (defrule cancel4
;     (declare (salience ?*super-high-priority*)) 
;     ?c <- (input ?q ?w cancel)
;     ?z <- (input ?x ?y ?v)
;     =>
;     (retract ?c)
;     (retract ?z)
;     (assert(input ui cancel))
; )

;Cancel will remove all the non-memory facts
; (defrule cancel5
;     (declare (salience ?*high-priority*)) 
;     ?c <- (input ui cancel)
;     =>
;     (retract ?c)
;     (assert (ui-state (text "Alright." "Ok." "I understand.")
;                         (valid-answers "''")
;                         (suggested-answers "")
;                         (clipboard "''")
;                         (fact-type ui)))
; )
;Values direct
; (defrule values-direct-new
;     ?v <- (input ui values ?x)
;     =>
;     (retract ?v)
;     (assert (input prediction-values ?x))
; )

; (defrule values-direct-override
;     (declare (salience ?*medium-high-priority*))
;     ?v <- (input ui values ?x)
;     ?p <- (input prediction-values ?q)
;     =>
;     (retract ?v)
;     (retract ?p)
;     (assert (input prediction-values ?x))
; )

;Values - all at once
; (defrule values-new
;     ?v <- (input ui values)
;     =>
;     (retract ?v)
;     (assert (ui-state (text (str-cat "Ok, please provide some values in the format: [" (getFeatureNames) "]"))
;                         (valid-answers "")
;                         (suggested-answers "")
;                         (fact-type prediction-values)))
; )

; (defrule values-override
;     (declare (salience ?*medium-high-priority*))
;     ?v <- (input ui values)
;     ?p <- (input prediction-values $?q)
;     =>
;     (retract ?v)
;     (retract ?p)
;     (assert (ui-state (text (str-cat "Ok, please provide some values in the format: [" (getFeatureNames) "]"))
;                         (valid-answers "")
;                         (suggested-answers "")
;                         (fact-type prediction-values)))
; )

; (defrule req-values
;     (declare (salience ?*high-priority*))
;     (input prediction-values $?v)
;     ?r <- (input req values)
;     =>
;     (retract ?r)
;     (assert (ui-state (text (str-cat "Use " ?v "?") (str-cat "Do you want to use " ?v "?"))
;                         (valid-answers "yes no")
;                         (suggested-answers "")
;                         (fact-type old-values)))
; )

; (defrule remove-old-data
;     (declare (salience ?*high-priority*))
;     ?o <- (input old-values no)
;     ?p <- (input prediction-values ?v)
;     =>
;     (retract ?o)
;     (retract ?p)
;     (assert(input ui values))
; )

; (defrule keep-old-data
;     (declare (salience ?*high-priority*))
;     ?o <- (input old-values yes)
;     ?p <- (input prediction-values ?v)
;     =>
;     (retract ?o)
;     (retract ?p)
;     (assert (input prediction-values ?v))
; )

;Predicting
;"Predict me for {value}"
; (defrule predict-with-values
;     ?x <- (input ui predict ?v)
;     =>
;     (retract ?x)
;     (assert(input ui values ?v))
;     (assert (ui-state (text (str-cat "I predicted a value for you: " (custom_predict ?v) "."))
;         (valid-answers "")
;         (suggested-answers "")
;         (fact-type ui)))
; )

;How-to
;How-to make {x} become {y}?
; (defrule how-to-with-two-values
;     ?h <- (input ui how-to ?v ?t)
;     =>
;     (retract ?h)
;     (assert (ui-state (text (str-cat "In the record " ?v " " (getCounterfactual ?v ?t) " to become " ?t "."))
;                         (valid-answers "")
;                         (suggested-answers "");see retract ui-state and predict?
;                         (fact-type ui)))
; )

;How-to become {y}?
; (defrule how-to-with-target-value
;     ?h <- (input ui how-to ?t)
;     (input prediction-values ?v)
;     =>
;     (retract ?h)
;     (assert (ui-state (text (str-cat "In the record " ?v " " (getCounterfactual ?v ?t) " to become " ?t "."))
;                         (valid-answers "")
;                         (suggested-answers "");see retract ui-state and predict?
;                         (fact-type ui)))
; )

;How-to something
; (defrule how-to-without-data-available
;     (declare (salience ?*low-priority*))
;     ?h <- (input ui how-to)
;     =>
;     (retract ?h)
;     (assert(input ui values));are three requirements for how-to
;     (assert(input ui wish-value))
;     (assert(input ui calc-how-to))
; )

; (defrule how-to-with-data-available
;     (declare (salience ?*medium-high-priority*))
;     ?h <- (input ui how-to)
;     (input prediction-values ?v)
;     =>
;     (retract ?h)
;     (assert(input req values))
;     (assert(input ui wish-value))
;     (assert(input ui calc-how-to))
; )

; (defrule wish-value
;     (declare (salience ?*medium-low-priority*))
;     ?i <- (input ui wish-value)
;     =>
;     (retract ?i)
;     (assert (ui-state (text (str-cat "Which value should the prediction take?"))
;                         (valid-answers (getDistinctTargetValues))
;                         (suggested-answers "")
;                         (fact-type how-to-values)))
; )

; (defrule how-to-values-calculation
;     ?i <- (input ui calc-how-to)
;     ?h <- (input how-to-values ?v1)
;     (input prediction-values ?v2)
;     =>
;     (retract ?i)
;     (retract ?h)
;     (assert (ui-state (text (str-cat "In the current prediction " ?v2 " " (getCounterfactual ?v2 ?v1) " to become " ?v1 "."))
;                         (valid-answers "")
;                         (suggested-answers "");see retract ui-state and predict?
;                         (fact-type ui)))
; )



;Testing

; (defrule why
;     ?w <- (input ui why)
;     =>
;     (retract ?w)
;     (assert(input why-value 20))
;     (assert (ui-state (text "You asked the why question.")
;                         (valid-answers "")
;                         (suggested-answers "")
;                         (fact-type ui)))
; )

; (defrule why-certainty
;     ?w <- (input why-value ?v)
;     ?c <- (input ui certainty)
;     =>
;     (retract ?w)
;     (retract ?c)
;     (assert (ui-state (text "The certainty is 50%.")
;                         (valid-answers "")
;                         (suggested-answers "");in the case of skip, this will hint to follow up rule
;                         (fact-type skip)
;                         (skip evaluate)))
; )

; (defrule evaluate
;     ?e <- (input skip evaluate)
;     =>
;     (retract ?e)
;     (assert (ui-state (text "Hope you got this.")
;                         (valid-answers "[]")
;                         (suggested-answers "[]")
;                         (fact-type ui)))
; )

; (defrule where
;     (input ui where)
;     =>
;     (assert(input ui where-values))
;     (assert(input ui where-aim))
; )

; (defrule where-values
;     (input ui where-values)
;     =>
;     (assert (ui-state (text (str-cat "Provide some where-values"))
;                         (suggested-answers "[]")
;                         (fact-type where-values)))
; )

; (defrule where-aim
;     (input ui where-aim)
;     =>
;     (assert (ui-state (text (str-cat "Provide some where-aim"))
;                         (suggested-answers "[]")
;                         (fact-type where-aim)))
; )

; (defrule where-values-aim
;     (input ui where)
;     (input where-aim ?w1)
;     (input where-values ?w2)
;     =>
;     (assert (ui-state (text (str-cat "Finished"))
;                         (suggested-answers "[]")
;                         (fact-type ui)))
; )

; (defrule upsert
;     ?input <- (input ?i)
;     ?upsert <- (upsert ?i)
;     =>
;     (printout t ?i crlf)
;     (retract ?input)
;     (retract ?upsert)
;     (assert (input ?i))
; )

; (defrule update-answers-prediction-values
;     (declare (salience ?*super-high-priority*))
;     (input prediction-values ?v)
;     =>
;     (printout t "Changing valid answers" crlf)
;     (bind ?*valid-answers* (create$ how-to values featureNames predict end))
; )

