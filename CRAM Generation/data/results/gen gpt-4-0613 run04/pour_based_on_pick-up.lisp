(<- (desig:action-grounding ?action-designator (pour ?source-object-desig ?target-object-desig ?arm
                                                      ?source-gripper-opening ?target-gripper-opening
                                                      ?source-effort ?target-effort ?grasp
                                                      ?left-reach-poses ?right-reach-poses
                                                      ?left-grasp-poses ?right-grasp-poses
                                                      ?left-pour-poses ?right-pour-poses))
    (spec:property ?action-designator (:type :pouring))
    (spec:property ?action-designator (:source-object ?source-object-designator))
    (spec:property ?action-designator (:target-object ?target-object-designator))
    (desig:current-designator ?source-object-designator ?source-object-desig)
    (desig:current-designator ?target-object-designator ?target-object-desig)
    (spec:property ?source-object-desig (:type ?source-object-type))
    (spec:property ?target-object-desig (:type ?target-object-type))
    (spec:property ?source-object-desig (:name ?source-object-name))
    (spec:property ?target-object-desig (:name ?target-object-name))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (lisp-fun obj-int:get-object-transform ?source-object-desig ?source-object-transform)
    (lisp-fun obj-int:get-object-transform ?target-object-desig ?target-object-transform)
    (lisp-fun obj-int:calculate-object-faces ?source-object-transform (?source-facing-robot-face ?source-bottom-face))
    (lisp-fun obj-int:calculate-object-faces ?target-object-transform (?target-facing-robot-face ?target-bottom-face))
    (-> (obj-int:object-rotationally-symmetric ?source-object-type)
        (equal ?source-rotationally-symmetric t)
        (equal ?source-rotationally-symmetric nil))
    (-> (obj-int:object-rotationally-symmetric ?target-object-type)
        (equal ?target-rotationally-symmetric t)
        (equal ?target-rotationally-symmetric nil))
    (-> (spec:property ?action-designator (:grasp ?grasp))
        (true)
        (and (lisp-fun obj-int:get-object-type-grasps
                       ?source-object-type ?source-facing-robot-face ?source-bottom-face ?source-rotatiationally-symmetric ?arm
                       ?source-grasps)
             (member ?grasp ?source-grasps)))
    (lisp-fun obj-int:get-object-type-gripping-effort ?source-object-type ?source-effort)
    (lisp-fun obj-int:get-object-type-gripping-effort ?target-object-type ?target-effort)
    (lisp-fun obj-int:get-object-type-gripper-opening ?source-object-type ?source-gripper-opening)
    (lisp-fun obj-int:get-object-type-gripper-opening ?target-object-type ?target-gripper-opening)
    (lisp-fun obj-int:get-object-grasping-poses
              ?source-object-name ?source-object-type :left ?grasp ?source-object-transform
              ?left-source-poses)
    (lisp-fun obj-int:get-object-grasping-poses
              ?source-object-name ?source-object-type :right ?grasp ?source-object-transform
              ?right-source-poses)
    (lisp-fun obj-int:get-object-grasping-poses
              ?target-object-name ?target-object-type :left ?grasp ?target-object-transform
              ?left-target-poses)
    (lisp-fun obj-int:get-object-grasping-poses
              ?target-object-name ?target-object-type :right ?grasp ?target-object-transform
              ?right-target-poses)
    (lisp-fun extract-pour-manipulation-poses ?arm ?left-source-poses ?right-source-poses ?left-target-poses ?right-target-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-grasp-poses ?right-grasp-poses
                                 ?left-pour-poses ?right-pour-poses)))