(<- (desig:action-grounding ?action-designator (place-down ?arm
                                                             ?gripper-opening
                                                             ?distance
                                                             ?left-reach-poses
                                                             ?right-reach-poses
                                                             ?left-grasp-poses
                                                             ?right-grasp-poses
                                                             (?left-lift-pose)
                                                             (?right-lift-pose)
                                                             (?left-2nd-lift-pose)
                                                             (?right-2nd-lift-pose)
                                                             ?joint-name ?environment-obj))
    (spec:property ?action-designator (:type :placing))
    (spec:property ?action-designator (:object ?held-object-designator))
    (spec:property ?held-object-designator (:type ?held-object-type))
    (obj-int:object-type-subtype :object ?held-object-type)
    (spec:property ?held-object-designator (:urdf-name ?held-object-name))
    (spec:property ?held-object-designator (:part-of ?btr-environment))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:distance ?distance))
    (lisp-fun get-object-link ?held-object-name ?btr-environment ?held-object-link)
    (lisp-fun get-connecting-joint ?held-object-link ?connecting-joint)
    (lisp-fun cl-urdf:name ?connecting-joint ?joint-name)
    (btr:bullet-world ?world)
    (lisp-fun btr:object ?world ?btr-environment ?environment-obj)
    (lisp-fun obj-int:get-object-type-gripper-opening ?held-object-type ?gripper-opening)
    (lisp-fun get-object-pose-and-transform ?held-object-name ?btr-environment
              (?held-object-pose ?held-object-transform))
    (lisp-fun obj-int:get-object-grasping-poses ?held-object-name
              :object-prismatic :left :open ?held-object-transform ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?held-object-name
              :object-prismatic :right :open ?held-object-transform ?right-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-place-down-manipulation-poses
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