(<- (desig:action-grounding ?action-designator (place-object ?arm
                                                            ?gripper-opening
                                                            ?distance
                                                            ?left-reach-poses
                                                            ?right-reach-poses
                                                            ?left-release-poses
                                                            ?right-release-poses
                                                            ?joint-name ?environment-obj))
    (spec:property ?action-designator (:type :placing))
    (spec:property ?action-designator (:object ?held-object))
    (spec:property ?held-object (:type ?object-type))
    (obj-int:object-type-subtype :object ?object-type)
    (spec:property ?held-object (:urdf-name ?object-name))
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
    (lisp-fun obj-int:get-object-releasing-poses ?object-name
              :object-prismatic :left ?object-transform ?left-poses)
    (lisp-fun obj-int:get-object-releasing-poses ?object-name
              :object-prismatic :right ?object-transform ?right-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-place-down-manipulation-poses
              ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-release-poses ?right-release-poses))
    (-> (lisp-pred identity ?left-release-poses)
        (equal ?left-release-poses (list))
        (true))
    (-> (lisp-pred identity ?right-release-poses)
        (equal ?right-release-poses (list))
        (true)))