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
    (btr:bullet-world ?world)
    (lisp-fun btr:object ?world ?environment ?object)
    (lisp-fun get-object-pose-and-transform ?object ?environment
              (?object-pose ?object-transform))
    (lisp-fun cram-mobile-pick-place-plans::extract-hold-manipulation-poses
              ?arm ?gripper-opening ?object-transform
              (?reach-poses ?grasp-poses ?lift-poses))
    (-> (lisp-pred identity ?lift-poses)
        (equal ?lift-poses NIL)))