(<- (desig:action-grounding ?action-designator (hold-object ?arm
                                                            ?gripper-closing
                                                            ?object-designator))
    (spec:property ?action-designator (:type :holding))
    (spec:property ?action-designator (:object ?object-designator))
    (spec:property ?object-designator (:type ?object-type))
    (spec:property ?object-designator (:urdf-name ?object-name))
    (spec:property ?object-designator (:part-of ?btr-environment))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (btr:bullet-world ?world)
    (lisp-fun btr:object ?world ?btr-environment ?environment-obj)
    (lisp-fun obj-int:get-object-type-gripper-closing ?object-type ?gripper-closing)
    (lisp-fun get-object-pose-and-transform ?object-name ?btr-environment
              (?object-pose ?object-transform))
    (lisp-fun obj-int:get-object-grasping-poses ?object-name
              :object :left :closed ?object-transform ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?object-name
              :object :right :closed ?object-transform ?right-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-hold-manipulation-poses
              ?arm ?left-poses ?right-poses
              (?left-hold-poses ?right-hold-poses)))