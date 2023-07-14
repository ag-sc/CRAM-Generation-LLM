(<- (desig:action-grounding ?action-designator (close-container ?arm
                                                                 ?gripper-closing
                                                                 ?distance
                                                                 ?left-reach-poses
                                                                 ?right-reach-poses
                                                                 ?left-grasp-poses
                                                                 ?right-grasp-poses
                                                                 (?left-lower-pose)
                                                                 (?right-lower-pose)
                                                                 (?left-2nd-lower-pose)
                                                                 (?right-2nd-lower-pose)
                                                                 ?joint-name ?environment-obj))
    (spec:property ?action-designator (:type :closing))
    (spec:property ?action-designator (:object ?container-designator))
    (spec:property ?container-designator (:type ?container-type))
    (obj-int:object-type-subtype :container ?container-type)
    (spec:property ?container-designator (:urdf-name ?container-name))
    (spec:property ?container-designator (:part-of ?btr-environment))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:distance ?distance))
    (lisp-fun get-container-link ?container-name ?btr-environment ?container-link)
    (lisp-fun get-connecting-joint ?container-link ?connecting-joint)
    (lisp-fun cl-urdf:name ?connecting-joint ?joint-name)
    (btr:bullet-world ?world)
    (lisp-fun btr:object ?world ?btr-environment ?environment-obj)
    (lisp-fun obj-int:get-object-type-gripper-closing ?container-type ?gripper-closing)
    (lisp-fun get-container-pose-and-transform ?container-name ?btr-environment
              (?container-pose ?container-transform))
    (lisp-fun obj-int:get-object-grasping-poses ?container-name
              :container-prismatic :left :close ?container-transform ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?container-name
              :container-prismatic :right :close ?container-transform ?right-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-close-manipulation-poses
              ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-grasp-poses ?right-grasp-poses
                                 ?left-lower-poses ?right-lower-poses))
     (-> (lisp-pred identity ?left-lower-poses)
        (equal ?left-lower-poses (?left-lower-pose ?left-2nd-lower-pose))
        (equal (NIL NIL) (?left-lower-pose ?left-2nd-lower-pose)))
    (-> (lisp-pred identity ?right-lower-poses)
        (equal ?right-lower-poses (?right-lower-pose ?right-2nd-lower-pose))
        (equal (NIL NIL) (?right-lower-pose ?right-2nd-lower-pose))))