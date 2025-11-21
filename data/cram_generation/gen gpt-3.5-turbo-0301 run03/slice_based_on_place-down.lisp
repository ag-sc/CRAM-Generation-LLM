(<- (desig:action-grounding ?action-designator (slice ?current-object-designator ?arm
                                                      ?left-reach-poses ?right-reach-poses
                                                      ?left-cut-poses ?right-cut-poses
                                                      ?left-retract-poses ?right-retract-poses
                                                      ?small-slice ?big-slice))
    (spec:property ?action-designator (:type :slicing))
    (-> (spec:property ?action-designator (:arm ?arm))
        (-> (spec:property ?action-designator (:object ?object-designator))
            (or (cpoe:object-in-hand ?object-designator ?arm)
                (and (format "WARNING: Wanted to slice an object ~a with arm ~a, ~
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
    (-> (lisp-fun obj-int:get-object-bounding-box ?current-object-designator)
        (lisp-fun extract-slice-poses ?small-slice ?big-slice))
    (lisp-fun obj-int:get-object-grasping-poses
              ?object-name ?object-type :left ?grasp ?small-slice
              ?left-cut-poses)
    (lisp-fun obj-int:get-object-grasping-poses
              ?object-name ?object-type :right ?grasp ?small-slice
              ?right-cut-poses)
    (lisp-fun extract-slicing-manipulation-poses ?arm ?left-cut-poses ?right-cut-poses
              (?left-reach-poses ?right-reach-poses ?left-cut-poses ?right-cut-poses
                                 ?left-retract-poses ?right-retract-poses))))