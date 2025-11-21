(<- (desig:action-grounding ?action-designator (place-down ?arm
                                                           ?gripper-opening
                                                           ?distance
                                                           ?left-reach-poses
                                                           ?right-reach-poses
                                                           ?left-release-poses
                                                           ?right-release-poses
                                                           ?location-designator))
    (spec:property ?action-designator (:type :placing))
    (spec:property ?action-designator (:object ?held-object-designator))
    (spec:property ?held-object-designator (:type ?held-object-type))
    (obj-int:object-type-subtype :object ?held-object-type)
    (spec:property ?held-object-designator (:urdf-name ?held-object-name))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:distance ?distance))
    (spec:property ?location-designator (:type :location))
    (spec:property ?location-designator (:urdf-name ?location-name))
    (spec:property ?location-designator (:part-of ?btr-environment))
    (lisp-fun get-location-pose-and-transform ?location-name ?btr-environment
              (?location-pose ?location-transform))
    (lisp-fun obj-int:get-object-grasping-poses ?held-object-name
              :object-prismatic :left :open ?location-transform ?left-release-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?held-object-name
              :object-prismatic :right :open ?location-transform ?right-release-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-place-down-manipulation-poses
              ?arm ?left-release-poses ?right-release-poses
              (?left-reach-poses ?right-reach-poses)))