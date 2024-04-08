(<- (desig:action-grounding ?action-designator (place-down ?current-object-desig ?arm
                                                            ?gripper-opening ?effort ?release
                                                            ?left-reach-poses ?right-reach-poses
                                                            ?left-release-poses ?right-release-poses))
    (spec:property ?action-designator (:type :placing-down))
    (spec:property ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-desig)
    (spec:property ?current-object-desig (:type ?object-type))
    (spec:property ?current-object-desig (:name ?object-name))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (lisp-fun obj-int:get-object-transform ?current-object-desig ?object-transform)
    (lisp-fun obj-int:get-object-type-gripper-opening ?object-type ?gripper-opening)
    (lisp-fun obj-int:get-object-type-gripping-effort ?object-type ?effort)
    (-> (spec:property ?action-designator (:release ?release))
        (true)
        (and (lisp-fun obj-int:get-object-type-releases
                       ?object-type ?release)
             (member ?release ?releases)))
    (lisp-fun obj-int:get-object-release-poses
              ?object-name ?object-type :left ?release ?object-transform
              ?left-release-poses)
    (lisp-fun obj-int:get-object-release-poses
              ?object-name ?object-type :right ?release ?object-transform
              ?right-release-poses)
    (lisp-fun extract-place-down-manipulation-poses ?arm ?left-release-poses ?right-release-poses
              (?left-reach-poses ?right-reach-poses)))