(<- (desig:action-grounding ?action-designator (hold-object ?arm
                                                            ?gripper-closing
                                                            ?object-designator
                                                            ?btr-environment
                                                            ?environment-obj))
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
    (lisp-fun obj-int:get-object-holding-poses ?object-name
              :object-prismatic :firm ?object-transform ?holding-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-hold-manipulation-poses
              ?arm ?holding-poses
              (?holding-poses)))