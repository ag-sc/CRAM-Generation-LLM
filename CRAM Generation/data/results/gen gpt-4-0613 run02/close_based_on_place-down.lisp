(<- (desig:action-grounding ?action-designator (close ?container-designator ?arm
                                                        ?left-reach-poses ?right-reach-poses
                                                        ?left-grasp-poses ?right-grasp-poses
                                                        ?left-retract-poses ?right-retract-poses))
    (spec:property ?action-designator (:type :closing))
    (-> (spec:property ?action-designator (:arm ?arm))
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (once (spec:property ?action-designator (:object ?container-designator)))
    (desig:current-designator ?container-designator ?current-container-designator)
    (spec:property ?current-container-designator (:type ?container-type))
    (spec:property ?current-container-designator (:name ?container-name))
    (obj-int:container-type-grasp ?container-type ?grasp)
    (lisp-fun obj-int:get-container-grasping-poses
              ?container-name ?container-type :left ?grasp ?left-grasp-poses)
    (lisp-fun obj-int:get-container-grasping-poses
              ?container-name ?container-type :right ?grasp ?right-grasp-poses)
    (lisp-fun extract-close-manipulation-poses ?arm ?left-grasp-poses ?right-grasp-poses
              (?left-reach-poses ?right-reach-poses ?left-grasp-poses ?right-grasp-poses
                                 ?left-retract-poses ?right-retract-poses))))