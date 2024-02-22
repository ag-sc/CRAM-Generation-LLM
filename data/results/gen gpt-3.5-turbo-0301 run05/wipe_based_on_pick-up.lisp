(<- (desig:action-grounding ?action-designator (wipe ?surface-desig ?towel-desig ?arm
                                                     ?gripper-opening ?effort ?grasp
                                                     ?left-reach-poses ?right-reach-poses
                                                     ?left-grasp-poses ?right-grasp-poses
                                                     ?left-wipe-poses ?right-wipe-poses))
    (spec:property ?action-designator (:type :cleaning))
    (spec:property ?action-designator (:surface ?surface-designator))
    (desig:current-designator ?surface-designator ?surface-desig)
    (spec:property ?surface-desig (:type ?surface-type))
    (spec:property ?surface-desig (:name ?surface-name))
    (spec:property ?action-designator (:tool ?towel-designator))
    (desig:current-designator ?towel-designator ?towel-desig)
    (spec:property ?towel-desig (:type :towel))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (lisp-fun obj-int:get-surface-transform ?surface-desig ?surface-transform)
    (lisp-fun obj-int:get-surface-faces ?surface-transform (?facing-robot-face ?bottom-face))
    (-> (spec:property ?action-designator (:grasp ?grasp))
        (true)
        (and (lisp-fun obj-int:get-towel-type-grasps
                       ?towel-desig ?facing-robot-face ?bottom-face ?arm
                       ?grasps)
             (member ?grasp ?grasps)))
    (lisp-fun obj-int:get-towel-type-gripping-effort ?towel-desig ?effort)
    (lisp-fun obj-int:get-towel-type-gripper-opening ?towel-desig ?gripper-opening)
    (lisp-fun obj-int:get-towel-wiping-poses
              ?towel-desig ?grasp ?surface-transform
              :left ?left-wipe-poses
              :right ?right-wipe-poses)
    (lisp-fun extract-wipe-manipulation-poses ?arm ?left-wipe-poses ?right-wipe-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-grasp-poses ?right-grasp-poses
                                 ?left-wipe-poses ?right-wipe-poses)))