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
    (spec:property ?action-designator (:type :picking))
    (spec:property ?action-designator (:object ?object-designator))
    (spec:property ?object-designator (:type ?object-type))
    (obj-int:object-type-subtype :object ?object-type)
    (spec:property ?object-designator (:urdf-name ?object-name))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:distance ?distance))
    (lisp-fun obj-int:get-object-type-gripper-opening ?object-type ?gripper-opening)
    (lisp-fun get-object-pose-and-transform ?object-name ?object-transform)
    (lisp-fun obj-int:get-object-grasping-poses ?object-name
              :object-prismatic :left :close ?object-transform ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?object-name
              :object-prismatic :right :close ?object-transform ?right-poses)
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
        (equal (NIL NIL) (?right-lift-pose ?right-2nd-lift-pose)))))