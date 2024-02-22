(<- (desig:action-grounding ?action-designator (open ?current-object-desig ?arm
                                                      ?gripper-opening ?effort ?grasp
                                                      ?left-reach-poses ?right-reach-poses
                                                      ?left-grasp-poses ?right-grasp-poses
                                                      ?left-lift-poses ?right-lift-poses))
    (spec:property ?action-designator (:type :opening))
    (spec:property ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-desig)
    (spec:property ?current-object-desig (:type ?object-type))
    (spec:property ?current-object-desig (:name ?object-name))
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
    (lisp-fun obj-int:get-object-grasping-poses
              ?object-name ?object-type :left ?grasp ?object-transform
              ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses
              ?object-name ?object-type :right ?grasp ?object-transform
              ?right-poses)
    (lisp-fun extract-open-manipulation-poses ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-grasp-poses ?right-grasp-poses
                                 ?left-lift-poses ?right-lift-poses)))