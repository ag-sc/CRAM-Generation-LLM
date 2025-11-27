(<- (desig:action-grounding ?action-designator (close ?container-designator ?arm
                                                        ?left-reach-poses ?right-reach-poses
                                                        ?left-put-poses ?right-put-poses
                                                        ?left-retract-poses ?right-retract-poses))
    (spec:property ?action-designator (:type :closing))
    (-> (spec:property ?action-designator (:container ?container-designator))
        (cram-object-interfaces:container ?container-designator))
    (-> (spec:property ?action-designator (:arm ?arm))
        (cram-robot-interfaces:robot ?robot)
        (cram-robot-interfaces:arm ?robot ?arm)))
    (lisp-fun obj-int:get-container-closing-poses
              ?container-designator ?arm
              ?left-poses ?right-poses)
    (lisp-fun extract-place-manipulation-poses ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses ?left-put-poses ?right-put-poses
                                 ?left-retract-poses ?right-retract-poses))))