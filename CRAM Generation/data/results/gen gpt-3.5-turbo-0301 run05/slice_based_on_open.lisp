(<- (desig:action-grounding ?action-designator (slice ?arm
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
    (spec:property ?action-designator (:type :cutting))
    (spec:property ?action-designator (:object ?food-object))
    (spec:property ?food-object (:type :food))
    (spec:property ?food-object (:urdf-name ?food-object-name))
    (spec:property ?food-object (:part-of ?btr-environment))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:distance ?distance))
    (lisp-fun get-food-object-link ?food-object-name ?btr-environment ?food-object-link)
    (lisp-fun get-connecting-joint ?food-object-link ?connecting-joint)
    (lisp-fun cl-urdf:name ?connecting-joint ?joint-name)
    (btr:bullet-world ?world)
    (lisp-fun btr:object ?world ?btr-environment ?environment-obj)
    (lisp-fun obj-int:get-object-type-gripper-opening :food ?gripper-opening)
    (lisp-fun get-food-object-pose-and-transform ?food-object-name ?btr-environment
              (?food-object-pose ?food-object-transform))
    (lisp-fun obj-int:get-object-grasping-poses ?food-object-name
              :food :left :open ?food-object-transform ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?food-object-name
              :food :right :open ?food-object-transform ?right-poses)
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
        (equal (NIL NIL) (?right-lift-pose ?right-2nd-lift-pose)))
    (lisp-fun obj-int:slice-object ?food-object-name ?btr-environment
              (?small-slice-pose ?big-slice-pose)))