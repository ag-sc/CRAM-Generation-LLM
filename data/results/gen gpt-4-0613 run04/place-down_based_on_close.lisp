(<- (desig:action-grounding ?action-designator (place-down ?arm
                                                           ?gripper-opening
                                                           ?distance
                                                           ?left-reach-poses
                                                           ?right-reach-poses
                                                           ?left-release-poses
                                                           ?right-release-poses
                                                           ?location-designator))
    (spec:property ?action-designator (:type :placing))
    (spec:property ?action-designator (:object ?held-object-designator))
    (spec:property ?held-object-designator (:part-of ?robot))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:distance ?distance))
    (spec:property ?action-designator (:gripper-opening ?gripper-opening))
    (spec:property ?action-designator (:location ?location-designator))
    (spec:property ?location-designator (:type :location))
    (spec:property ?location-designator (:urdf-name ?location-name))
    (spec:property ?location-designator (:part-of ?environment))
    (lisp-fun cram-mobile-pick-place-plans::extract-place-down-manipulation-poses
              ?arm ?left-release-poses ?right-release-poses
              (?left-reach-poses ?right-reach-poses)))