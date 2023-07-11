(<- (desig:action-grounding ?action-designator (hold ?arm
                                                        ?gripper-closing
                                                        ?distance
                                                        ?left-reach-poses
                                                        ?right-reach-poses
                                                        ?left-grasp-poses
                                                        ?right-grasp-poses
                                                        (?left-hold-pose)
                                                        (?right-hold-pose)
                                                        (?left-2nd-hold-pose)
                                                        (?right-2nd-hold-pose)
                                                        ?joint-name ?environment-obj))
    (spec:property ?action-designator (:type :holding))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:distance ?distance))
    (lisp-fun obj-int:get-object-type-gripper-closing ?gripper-closing)
    (lisp-fun cram-mobile-pick-place-plans::extract-hold-manipulation-poses
              ?arm ?left-grasp-poses ?right-grasp-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-hold-poses ?right-hold-poses))
    (-> (lisp-pred identity ?left-hold-poses)
        (equal ?left-hold-poses (?left-hold-pose ?left-2nd-hold-pose))
        (equal (NIL NIL) (?left-hold-pose ?left-2nd-hold-pose)))
    (-> (lisp-pred identity ?right-hold-poses)
        (equal ?right-hold-poses (?right-hold-pose ?right-2nd-hold-pose))
        (equal (NIL NIL) (?right-hold-pose ?right-2nd-hold-pose))))