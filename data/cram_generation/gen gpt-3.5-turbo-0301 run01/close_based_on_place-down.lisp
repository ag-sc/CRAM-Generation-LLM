(<- (desig:action-grounding ?action-designator (close ?container-designator))
    (spec:property ?action-designator (:type :closing))
    (spec:property ?action-designator (:object ?container-designator))
    (spec:property ?container-designator (:type :container))
    (spec:property ?container-designator (:name ?container-name))
    (lisp-fun obj-int:get-container-closing-poses ?container-name ?container-designator
              ?closing-poses)
    (lisp-fun extract-closing-manipulation-poses ?closing-poses ?left-reach-poses
              ?right-reach-poses ?left-grasp-poses ?right-grasp-poses
              ?left-retract-poses ?right-retract-poses)
    (or (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot :left)
             (cram-robot-interfaces:arm ?robot :right))
        (format "WARNING: Could not find robot or arms for closing container ~a.~%"
                ?container-designator)))