(<- (desig:action-grounding ?action-designator (place-object ?arm
                                                            ?gripper-opening
                                                            ?distance
                                                            ?left-reach-poses
                                                            ?right-reach-poses
                                                            ?left-release-poses
                                                            ?right-release-poses
                                                            ?joint-name ?target-location))
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
    (spec:property ?action-designator (:target-location ?target-location))
    (lisp-fun cram-mobile-pick-place-plans::extract-place-down-manipulation-poses
              ?arm ?left-release-poses ?right-release-poses
              (?left-reach-poses ?right-reach-poses))
    (lisp-fun obj-int:get-object-type-gripper-opening ?object-type ?gripper-opening)
    (lisp-fun get-object-pose-and-transform ?object-name ?object-pose ?object-transform)
    (lisp-fun get-target-location-pose-and-transform ?target-location ?target-pose ?target-transform)
    (lisp-fun cram-mobile-pick-place-plans::get-place-down-poses
              ?arm ?target-pose ?left-reach-poses ?right-reach-poses
              ?left-release-poses ?right-release-poses
              (?left-place-poses ?right-place-poses))
    (-> (lisp-pred identity ?left-place-poses)
        (equal ?left-place-poses (?left-place-pose))
        (equal (NIL) (?left-place-pose)))
    (-> (lisp-pred identity ?right-place-poses)
        (equal ?right-place-poses (?right-place-pose))
        (equal (NIL) (?right-place-pose))))