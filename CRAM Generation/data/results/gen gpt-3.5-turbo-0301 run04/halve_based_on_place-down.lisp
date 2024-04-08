(<- (desig:action-grounding ?action-designator (halve ?current-object-designator ?arm
                                                      ?left-reach-poses ?right-reach-poses
                                                      ?left-cut-poses ?right-cut-poses
                                                      ?left-retract-poses ?right-retract-poses))
    (spec:property ?action-designator (:type :cutting))
    (-> (spec:property ?action-designator (:arm ?arm))
        (-> (spec:property ?action-designator (:object ?object-designator))
            (or (cpoe:object-in-hand ?object-designator ?arm)
                (and (format "WARNING: Wanted to cut an object ~a with arm ~a, ~
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
    (lisp-fun obj-int:get-object-transform ?current-object-designator ?object-transform)
    (lisp-fun obj-int:get-object-pose ?current-object-designator ?object-pose)
    (lisp-fun obj-int:get-object-bounding-box ?current-object-designator ?object-bbox)
    (lisp-fun extract-cutting-poses ?arm ?object-pose ?object-bbox ?object-transform
              ?left-cut-poses ?right-cut-poses)
    (lisp-fun extract-manipulation-poses ?arm ?left-cut-poses ?right-cut-poses
              ?left-reach-poses ?right-reach-poses ?left-retract-poses ?right-retract-poses)))