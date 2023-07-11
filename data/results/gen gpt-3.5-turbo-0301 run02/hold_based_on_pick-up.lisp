(<- (desig:action-grounding ?action-designator (hold ?arm
                                                      ?gripper-closing
                                                      ?distance
                                                      ?left-hold-poses
                                                      ?right-hold-poses
                                                      ?joint-name))
    (spec:property ?action-designator (:type :holding))
    (spec:property ?action-designator (:object ?object-designator))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:distance ?distance))
    (lisp-fun cram-mobile-pick-place-plans::extract-hold-manipulation-poses
              ?arm ?left-hold-poses ?right-hold-poses)
    (lisp-fun obj-int:get-object-type-gripper-closing ?object-type ?gripper-closing)
    (lisp-fun obj-int:get-object-connecting-joint ?object-name ?connecting-joint)
    (lisp-fun cl-urdf:name ?connecting-joint ?joint-name))