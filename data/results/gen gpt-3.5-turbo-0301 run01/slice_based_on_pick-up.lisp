(<- (desig:action-grounding ?action-designator (slice ?arm
                                                      ?gripper-opening
                                                      ?distance
                                                      ?left-reach-poses
                                                      ?right-reach-poses
                                                      ?left-grasp-poses
                                                      ?right-grasp-poses
                                                      ?left-cut-poses
                                                      ?right-cut-poses
                                                      ?joint-name ?environment-obj))
    (spec:property ?action-designator (:type :cutting))
    (spec:property ?action-designator (:object ?food-object))
    (obj-int:object-type-subtype :food ?food-object)
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
    (lisp-fun obj-int:get-object-type-gripper-opening ?food-object ?gripper-opening)
    (lisp-fun obj-int:get-object-grasping-poses ?food-object-name
              :food :left :open ?food-object-link ?left-grasp-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?food-object-name
              :food :right :open ?food-object-link ?right-grasp-poses)
    (lisp-fun cram-mobile-slicing-plans::extract-slicing-poses
              ?arm ?left-grasp-poses ?right-grasp-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-cut-poses ?right-cut-poses))
    (-> (lisp-pred identity ?left-cut-poses)
        (equal ?left-cut-poses (?small-slice-pose ?big-slice-pose))
        (equal (NIL NIL) (?small-slice-pose ?big-slice-pose)))
    (-> (lisp-pred identity ?right-cut-poses)
        (equal ?right-cut-poses (?small-slice-pose ?big-slice-pose))
        (equal (NIL NIL) (?small-slice-pose ?big-slice-pose))))