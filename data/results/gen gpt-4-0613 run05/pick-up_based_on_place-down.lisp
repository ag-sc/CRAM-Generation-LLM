(<- (desig:action-grounding ?action-designator (pick ?object-designator ?arm
                                                       ?left-reach-poses ?right-reach-poses
                                                       ?left-grasp-poses ?right-grasp-poses
                                                       ?left-retract-poses ?right-retract-poses))
    (spec:property ?action-designator (:type :picking))
    (-> (spec:property ?action-designator (:arm ?arm))
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (-> (spec:property ?action-designator (:object ?object-designator))
        (cpoe:object-in-world ?object-designator))
    (lisp-fun obj-int:get-object-grasping-poses
              ?object-designator :left ?left-grasp-poses)
    (lisp-fun obj-int:get-object-grasping-poses
              ?object-designator :right ?right-grasp-poses)
    (lisp-fun extract-pick-manipulation-poses ?arm ?left-grasp-poses ?right-grasp-poses
              (?left-reach-poses ?right-reach-poses ?left-grasp-poses ?right-grasp-poses
                                 ?left-retract-poses ?right-retract-poses))))