(<- (desig:action-grounding ?action-designator (place-down ?arm
                                                           ?gripper-opening
                                                           ?distance
                                                           ?left-reach-poses
                                                           ?right-reach-poses
                                                           ?left-place-poses
                                                           ?right-place-poses
                                                           (?left-lower-pose)
                                                           (?right-lower-pose)
                                                           (?left-2nd-lower-pose)
                                                           (?right-2nd-lower-pose)
                                                           ?joint-name ?environment-obj))
    (spec:property ?action-designator (:type :placing))
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
    (lisp-fun obj-int:get-object-type-gripper-opening ?container-type ?gripper-opening)
    (lisp-fun get-container-pose-and-transform ?container-name ?btr-environment
              (?container-pose ?container-transform))
    (lisp-fun obj-int:get-object-placing-poses ?container-name
              :container-prismatic :left :open ?container-transform ?left-poses)
    (lisp-fun obj-int:get-object-placing-poses ?container-name
              :container-prismatic :right :open ?container-transform ?right-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-place-down-manipulation-poses
              ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-place-poses ?right-place-poses
                                 ?left-lower-poses ?right-lower-poses))
     (-> (lisp-pred identity ?left-lower-poses)
        (equal ?left-lower-poses (?left-lower-pose ?left-2nd-lower-pose))
        (equal (NIL NIL) (?left-lower-pose ?left-2nd-lower-pose)))
    (-> (lisp-pred identity ?right-lower-poses)
        (equal ?right-lower-poses (?right-lower-pose ?right-2nd-lower-pose))
        (equal (NIL NIL) (?right-lower-pose ?right-2nd-lower-pose))))