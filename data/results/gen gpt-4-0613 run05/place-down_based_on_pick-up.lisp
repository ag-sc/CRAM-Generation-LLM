(<- (desig:action-grounding ?action-designator (place-object ?arm
                                                            ?gripper-opening
                                                            ?distance
                                                            ?left-reach-poses
                                                            ?right-reach-poses
                                                            ?left-release-poses
                                                            ?right-release-poses
                                                            ?target-pose))
    (spec:property ?action-designator (:type :placing))
    (spec:property ?action-designator (:object ?held-object))
    (spec:property ?held-object (:type ?object-type))
    (obj-int:object-type-subtype :object ?object-type)
    (spec:property ?held-object (:urdf-name ?object-name))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:distance ?distance))
    (spec:property ?action-designator (:target-pose ?target-pose))
    (lisp-fun obj-int:get-object-type-gripper-opening ?object-type ?gripper-opening)
    (lisp-fun cram-mobile-pick-place-plans::extract-place-down-manipulation-poses
              ?arm ?left-release-poses ?right-release-poses
              (?left-reach-poses ?right-reach-poses))
    (-> (lisp-pred identity ?left-release-poses)
        (equal ?left-release-poses ?left-release-poses)
        (true))
    (-> (lisp-pred identity ?right-release-poses)
        (equal ?right-release-poses ?right-release-poses)
        (true)))