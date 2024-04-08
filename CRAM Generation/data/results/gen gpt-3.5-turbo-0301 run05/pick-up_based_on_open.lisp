(<- (desig:action-grounding ?action-designator (pick-up ?arm
                                                        ?gripper-opening
                                                        ?distance
                                                        ?object-designator
                                                        ?left-reach-poses
                                                        ?right-reach-poses
                                                        ?left-grasp-poses
                                                        ?right-grasp-poses
                                                        (?left-lift-pose)
                                                        (?right-lift-pose)
                                                        (?left-2nd-lift-pose)
                                                        (?right-2nd-lift-pose)))
    (spec:property ?action-designator (:type :pick-up))
    (spec:property ?action-designator (:object ?object-designator))
    (spec:property ?object-designator (:type ?object-type))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:distance ?distance))
    (lisp-fun obj-int:get-object-type-gripper-opening ?object-type ?gripper-opening)
    (lisp-fun obj-int:get-object-grasping-poses ?object-designator
              :object :left :open NIL ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?object-designator
              :object :right :open NIL ?right-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-pick-up-manipulation-poses
              ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-grasp-poses ?right-grasp-poses
                                 ?left-lift-poses ?right-lift-poses))
    (-> (lisp-pred identity ?left-lift-poses)
        (equal ?left-lift-poses (?left-lift-pose ?left-2nd-lift-pose))
        (equal (NIL NIL) (?left-lift-pose ?left-2nd-lift-pose)))
    (-> (lisp-pred identity ?right-lift-poses)
        (equal ?right-lift-poses (?right-lift-pose ?right-2nd-lift-pose))
        (equal (NIL NIL) (?right-lift-pose ?right-2nd-lift-pose))))