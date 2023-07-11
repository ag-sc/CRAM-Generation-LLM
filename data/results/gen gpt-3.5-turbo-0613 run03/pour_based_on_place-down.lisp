(<- (desig:action-grounding ?action-designator (pour ?source-container ?target-container
                                                       ?source-pose ?target-pose))
    (spec:property ?action-designator (:type :pouring))
    (-> (spec:property ?action-designator (:object ?source-container))
        (cpoe:object-in-hand ?source-container ?arm))
    (-> (spec:property ?action-designator (:object ?target-container))
        (cpoe:object-in-hand ?target-container ?arm))
    (desig:current-designator ?source-container ?current-source-designator)
    (desig:current-designator ?target-container ?current-target-designator)
    (spec:property ?current-source-designator (:type ?source-type))
    (spec:property ?current-target-designator (:type ?target-type))
    (spec:property ?current-source-designator (:name ?source-name))
    (spec:property ?current-target-designator (:name ?target-name))
    (obj-int:object-type-grasp ?source-type ?source-grasp)
    (obj-int:object-type-grasp ?target-type ?target-grasp)
    (-> (spec:property ?action-designator (:source-pose ?source-pose))
        (and (symbol-value cram-tf:*robot-base-frame* ?base-frame)
             (lisp-fun cram-tf:ensure-pose-in-frame ?source-pose ?base-frame :use-zero-time t
                       ?source-pose-in-base))
        (and (lisp-fun obj-int:get-object-transform ?current-source-designator ?source-pose-in-base)
             (lisp-fun obj-int:get-object-pose ?current-source-designator ?source-pose)
             (desig:designator :location ((:pose ?source-pose)) ?source-container)))
    (-> (spec:property ?action-designator (:target-pose ?target-pose))
        (and (symbol-value cram-tf:*robot-base-frame* ?base-frame)
             (lisp-fun cram-tf:ensure-pose-in-frame ?target-pose ?base-frame :use-zero-time t
                       ?target-pose-in-base))
        (and (lisp-fun obj-int:get-object-transform ?current-target-designator ?target-pose-in-base)
             (lisp-fun obj-int:get-object-pose ?current-target-designator ?target-pose)
             (desig:designator :location ((:pose ?target-pose)) ?target-container)))
    (lisp-fun obj-int:get-object-grasping-poses
              ?source-name ?source-type :left ?source-grasp ?source-transform
              ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses
              ?target-name ?target-type :right ?target-grasp ?target-transform
              ?right-poses)
    (lisp-fun extract-pour-manipulation-poses ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses ?left-pour-poses ?right-pour-poses
                                 ?left-retract-poses ?right-retract-poses)))