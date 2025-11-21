(<- (desig:action-grounding ?action-designator (hold ?arm
                                                      ?gripper-opening
                                                      ?object-designator))
    (spec:property ?action-designator (:type :holding))
    (spec:property ?action-designator (:object ?object-designator))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (lisp-fun obj-int:get-object-type-gripper-opening
              (spec:property ?object-designator (:type ?object-type))
              ?gripper-opening)
    (spec:property ?object-designator (:part-of ?environment))
    (lisp-fun cram-robot-interfaces:object ?environment ?object-designator ?object)
    (lisp-fun cram-robot-interfaces:grasp-object ?arm ?object ?gripper-opening)))