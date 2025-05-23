(<- (desig:action-grounding ?action-designator (hold ?current-object-desig ?arm
                                                     ?gripper-effort ?gripper-opening
                                                     ?left-hold-poses ?right-hold-poses))
    (spec:property ?action-designator (:type :holding))
    (spec:property ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-desig)
    (spec:property ?current-object-desig (:type ?object-type))
    (spec:property ?current-object-desig (:name ?object-name))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (lisp-fun obj-int:get-object-gripping-effort ?object-type ?gripper-effort)
    (lisp-fun obj-int:get-object-gripper-opening ?object-type ?gripper-opening)
    (lisp-fun obj-int:get-object-holding-poses
              ?object-name ?object-type :left ?left-hold-poses)
    (lisp-fun obj-int:get-object-holding-poses
              ?object-name ?object-type :right ?right-hold-poses)))