(<- (desig:action-grounding ?action-designator (wipe ?current-object-designator ?arm
                                                       ?left-reach-poses ?right-reach-poses
                                                       ?left-put-poses ?right-put-poses
                                                       ?left-retract-poses ?right-retract-poses
                                                       ?surface))
    (spec:property ?action-designator (:type :cleaning))
    (-> (spec:property ?action-designator (:arm ?arm))
        (-> (spec:property ?action-designator (:object ?object-designator))
            (or (cpoe:object-in-hand ?object-designator ?arm)
                (and (format "WARNING: Wanted to wipe with object ~a using arm ~a, ~
                              but it's not in the arm.~%" ?object-designator ?arm)
                     ))
            (cpoe:object-in-hand ?object-designator ?arm))
        (-> (spec:property ?action-designator (:object ?object-designator))
            (cpoe:object-in-hand ?object-designator ?arm)
            (and (cram-robot-interfaces:robot ?robot)
                 (cram-robot-interfaces:arm ?robot ?arm)
                 (cpoe:object-in-hand ?object-designator ?arm))))
    (once (or (cpoe:object-in-hand ?object-designator ?arm)
              (spec:property ?action-designator (:object ?object-designator))))
    (desig:current-designator ?object-designator ?current-object-designator)
    (spec:property ?current-object-designator (:type ?object-type))
    (spec:property ?current-object-designator (:name ?object-name))
    (obj-int:object-type-grasp ?object-type ?grasp)
    (-> (spec:property ?action-designator (:target ?surface))
        (and (desig:current-designator ?surface ?current-surface-designator)
             (desig:designator-groundings ?current-surface-designator ?poses)
             (member ?target-pose ?poses)
             (symbol-value cram-tf:*robot-base-frame* ?base-frame)
             (lisp-fun cram-tf:ensure-pose-in-frame ?target-pose ?base-frame :use-zero-time t
                       ?target-pose-in-base)
             (lisp-fun roslisp-utilities:rosify-underscores-lisp-name ?object-name ?tf-name)
             (lisp-fun cram-tf:pose-stamped->transform-stamped ?target-pose-in-base ?tf-name
                       ?target-transform))
        (and (lisp-fun obj-int:get-object-transform ?current-object-designator ?target-transform)
             (lisp-fun obj-int:get-object-pose ?current-object-designator ?target-pose)
             (desig:designator :surface ((:pose ?target-pose)) ?surface)))
    (lisp-fun obj-int:get-object-grasping-poses
              ?object-name ?object-type :left ?grasp ?target-transform
              ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses
              ?object-name ?object-type :right ?grasp ?target-transform
              ?right-poses)
    (lisp-fun extract-place-manipulation-poses ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses ?left-put-poses ?right-put-poses
                                 ?left-retract-poses ?right-retract-poses))))