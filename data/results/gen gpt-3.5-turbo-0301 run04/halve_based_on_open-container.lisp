(<- (desig:action-grounding ?action-designator (halve ?arm
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
                                                      ?joint-name ?object))
    (spec:property ?action-designator (:type :cutting))
    (spec:property ?action-designator (:object ?object-designator))
    (spec:property ?object-designator (:type :food))
    (spec:property ?object-designator (:part-of ?btr-environment))
    (spec:property ?object-designator (:urdf-name ?object-name))
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
    (lisp-fun obj-int:get-object-type-gripper-opening :food ?gripper-opening)
    (lisp-fun get-object-pose-and-transform ?object-name ?btr-environment
              (?object-pose ?object-transform))
    (lisp-fun obj-int:get-object-grasping-poses ?object-name
              :food :left :open ?object-transform ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?object-name
              :food :right :open ?object-transform ?right-poses)
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