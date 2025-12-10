(<- (desig:action-grounding ?action-designator (pour ?source-container-desig ?target-container-desig ?arm
                                                          ?gripper-opening ?effort ?grasp
                                                          ?left-reach-poses ?right-reach-poses
                                                          ?left-grasp-poses ?right-grasp-poses
                                                          ?left-pour-poses ?right-pour-poses))
    (spec:property ?action-designator (:type :pouring))
    (spec:property ?action-designator (:source-container ?source-container-designator))
    (desig:current-designator ?source-container-designator ?source-container-desig)
    (spec:property ?source-container-desig (:type ?source-container-type))
    (spec:property ?source-container-desig (:name ?source-container-name))
    (spec:property ?action-designator (:target-container ?target-container-designator))
    (desig:current-designator ?target-container-designator ?target-container-desig)
    (spec:property ?target-container-desig (:type ?target-container-type))
    (spec:property ?target-container-desig (:name ?target-container-name))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (lisp-fun obj-int:get-object-transform ?source-container-desig ?source-container-transform)
    (lisp-fun obj-int:get-object-transform ?target-container-desig ?target-container-transform)
    (lisp-fun obj-int:calculate-object-faces ?source-container-transform (?source-facing-robot-face ?source-bottom-face))
    (lisp-fun obj-int:calculate-object-faces ?target-container-transform (?target-facing-robot-face ?target-bottom-face))
    (-> (obj-int:object-rotationally-symmetric ?source-container-type)
        (equal ?source-rotationally-symmetric t)
        (equal ?source-rotationally-symmetric nil))
    (-> (spec:property ?action-designator (:grasp ?grasp))
        (true)
        (and (lisp-fun obj-int:get-object-type-grasps
                       ?source-container-type ?source-facing-robot-face ?source-bottom-face ?source-rotationally-symmetric ?arm
                       ?grasps)
             (member ?grasp ?grasps)))
    (lisp-fun obj-int:get-object-type-gripping-effort ?source-container-type ?effort)
    (lisp-fun obj-int:get-object-type-gripper-opening ?source-container-type ?gripper-opening)
    (lisp-fun obj-int:get-object-grasping-poses
              ?source-container-name ?source-container-type :left ?grasp ?source-container-transform
              ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses
              ?source-container-name ?source-container-type :right ?grasp ?source-container-transform
              ?right-poses)
    (lisp-fun extract-pour-manipulation-poses ?arm ?left-poses ?right-poses ?target-container-transform
              (?left-reach-poses ?right-reach-poses
                                 ?left-grasp-poses ?right-grasp-poses
                                 ?left-pour-poses ?right-pour-poses)))