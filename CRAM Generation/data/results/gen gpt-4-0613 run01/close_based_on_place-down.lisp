(<- (desig:action-grounding ?action-designator (close ?current-object-designator ?arm))
    (spec:property ?action-designator (:type :closing))
    (-> (spec:property ?action-designator (:arm ?arm))
        (-> (spec:property ?action-designator (:object ?object-designator))
            (or (cpoe:object-in-hand ?object-designator ?arm)
                (and (format "WARNING: Wanted to close an object ~a with arm ~a, ~
                              but it's not in the arm.~%" ?object-designator ?arm)
                     ))
            (cpoe:object-in-hand ?object-designator ?arm))
        (-> (spec:property ?action-designator (:object ?object-designator))
            (cpoe:object-in-hand ?object-designator ?arm)
            (and (cram-robot-interfaces:robot ?robot)
                 (cram-robot-interfaces:arm ?robot ?arm)
                 (cpoe:object-in-hand ?object-designator ?arm))))
    (once (or (cpoe:object-in-hand ?object-designator ?arm)
              (spec:property ?action-designator (:object ?object-designator))))
    (desig:current-designator ?object-designator ?current-object-designator)
    (spec:property ?current-object-designator (:type ?object-type))
    (spec:property ?current-object-designator (:name ?object-name))
    (obj-int:object-type-grasp ?object-type ?grasp)
    (lisp-fun obj-int:get-object-closing-poses
              ?object-name ?object-type :left ?grasp
              ?left-poses)
    (lisp-fun obj-int:get-object-closing-poses
              ?object-name ?object-type :right ?grasp
              ?right-poses)
    (lisp-fun extract-close-manipulation-poses ?arm ?left-poses ?right-poses
              (?left-close-poses ?right-close-poses)))