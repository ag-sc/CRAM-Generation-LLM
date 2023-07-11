(<- (desig:action-grounding ?action-designator (hold ?arm
                                                      ?gripper-closing
                                                      ?object-designator))
    (spec:property ?action-designator (:type :holding))
    (spec:property ?action-designator (:object ?object-designator))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (lisp-fun obj-int:get-object-type-gripper-closing ?object-designator ?gripper-closing))