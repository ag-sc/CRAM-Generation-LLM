(<- (desig:action-grounding ?action-designator (cut-object ?arm
                                                              ?gripper-opening
                                                              ?distance
                                                              ?left-reach-poses
                                                              ?right-reach-poses
                                                              ?left-grasp-poses
                                                              ?right-grasp-poses
                                                              (?left-cut-pose)
                                                              (?right-cut-pose)
                                                              ?joint-name ?environment-obj))
    (spec:property ?action-designator (:type :cutting))
    (spec:property ?action-designator (:object ?object-designator))
    (spec:property ?object-designator (:type ?object-type))
    (obj-int:object-type-subtype :food ?object-type)
    (spec:property ?object-designator (:urdf-name ?object-name))
    (spec:property ?object-designator (:part-of ?btr-environment))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:distance ?distance))
    (lisp-fun get-object-link ?object-name ?btr-environment ?object-link)
    (lisp-fun get-connecting-joint ?object-link ?connecting-joint)
    (lisp-fun cl-urdf:name ?connecting-joint ?joint-name)
    (btr:bullet-world ?world)
    (lisp-fun btr:object ?world ?btr-environment ?environment-obj)
    (lisp-fun obj-int:get-object-type-gripper-opening ?object-type ?gripper-opening)
    (lisp-fun get-object-pose-and-transform ?object-name ?btr-environment
              (?object-pose ?object-transform))
    (lisp-fun obj-int:get-object-grasping-poses ?object-name
              :object-prismatic :left :open ?object-transform ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?object-name
              :object-prismatic :right :open ?object-transform ?right-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-cut-object-manipulation-poses
              ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-grasp-poses ?right-grasp-poses
                                 ?left-cut-poses ?right-cut-poses))
    (-> (lisp-pred identity ?left-cut-poses)
        (equal ?left-cut-poses (?left-cut-pose))
        (equal (NIL) (?left-cut-pose)))
    (-> (lisp-pred identity ?right-cut-poses)
        (equal ?right-cut-poses (?right-cut-pose))
        (equal (NIL) (?right-cut-pose))))