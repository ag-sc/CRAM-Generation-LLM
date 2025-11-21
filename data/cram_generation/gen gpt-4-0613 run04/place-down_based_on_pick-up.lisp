(<- (desig:action-grounding ?action-designator (place-down ?current-object-desig ?location-desig ?arm
                                                            ?gripper-opening ?effort ?grasp
                                                            ?left-reach-poses ?right-reach-poses
                                                            ?left-place-poses ?right-place-poses
                                                            ?left-lift-poses ?right-lift-poses))
    (spec:property ?action-designator (:type :placing-down))
    (spec:property ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-desig)
    (spec:property ?current-object-desig (:type ?object-type))
    (spec:property ?current-object-desig (:name ?object-name))
    (spec:property ?action-designator (:location ?location-designator))
    (desig:current-designator ?location-designator ?location-desig)
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (lisp-fun obj-int:get-object-transform ?current-object-desig ?object-transform)
    (lisp-fun obj-int:calculate-object-faces ?object-transform (?facing-robot-face ?bottom-face))
    (-> (obj-int:object-rotationally-symmetric ?object-type)
        (equal ?rotationally-symmetric t)
        (equal ?rotationally-symmetric nil))
    (-> (spec:property ?action-designator (:grasp ?grasp))
        (true)
        (and (lisp-fun obj-int:get-object-type-grasps
                       ?object-type ?facing-robot-face ?bottom-face ?rotatiationally-symmetric ?arm
                       ?grasps)
             (member ?grasp ?grasps)))
    (lisp-fun obj-int:get-object-type-gripping-effort ?object-type ?effort)
    (lisp-fun obj-int:get-object-type-gripper-opening ?object-type ?gripper-opening)
    (lisp-fun obj-int:get-object-placing-poses
              ?object-name ?object-type :left ?grasp ?object-transform
              ?left-poses)
    (lisp-fun obj-int:get-object-placing-poses
              ?object-name ?object-type :right ?grasp ?object-transform
              ?right-poses)
    (lisp-fun extract-place-down-manipulation-poses ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-place-poses ?right-place-poses
                                 ?left-lift-poses ?right-lift-poses)))