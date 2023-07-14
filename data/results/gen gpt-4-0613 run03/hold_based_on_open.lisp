(<- (desig:action-grounding ?action-designator (hold-object ?arm
                                                           ?gripper-closing
                                                           ?object-designator))
    (spec:property ?action-designator (:type :holding))
    (spec:property ?action-designator (:object ?object-designator))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:gripper-closing ?gripper-closing)))