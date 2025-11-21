(<- (desig:action-grounding ?action-designator (pour ?source-object-designator ?target-object-designator ?arm
                                                      ?left-reach-poses ?right-reach-poses
                                                      ?left-pour-poses ?right-pour-poses
                                                      ?left-retract-poses ?right-retract-poses
                                                      ?location))
    (spec:property ?action-designator (:type :pouring))
    (-> (spec:property ?action-designator (:arm ?arm))
        (-> (spec:property ?action-designator (:source-object ?source-object-designator))
            (or (cpoe:object-in-hand ?source-object-designator ?arm)
                (and (format "WARNING: Wanted to pour from object ~a with arm ~a, ~
                              but it's not in the arm.~%" ?source-object-designator ?arm)
                     ))
            (cpoe:object-in-hand ?source-object-designator ?arm))
        (-> (spec:property ?action-designator (:target-object ?target-object-designator))
            (cpoe:object-in-hand ?target-object-designator ?arm)
            (and (cram-robot-interfaces:robot ?robot)
                 (cram-robot-interfaces:arm ?robot ?arm)
                 (cpoe:object-in-hand ?target-object-designator ?arm))))
    (once (or (cpoe:object-in-hand ?source-object-designator ?arm)
              (spec:property ?action-designator (:source-object ?source-object-designator))))
    (desig:current-designator ?source-object-designator ?current-source-object-designator)
    (spec:property ?current-source-object-designator (:type ?source-object-type))
    (spec:property ?current-source-object-designator (:name ?source-object-name))
    (obj-int:object-type-grasp ?source-object-type ?grasp)
    (-> (spec:property ?action-designator (:target ?location))
        (and (desig:current-designator ?location ?current-location-designator)
             (desig:designator-groundings ?current-location-designator ?poses)
             (member ?target-pose ?poses)
             (symbol-value cram-tf:*robot-base-frame* ?base-frame)
             (lisp-fun cram-tf:ensure-pose-in-frame ?target-pose ?base-frame :use-zero-time t
                       ?target-pose-in-base)
             (lisp-fun roslisp-utilities:rosify-underscores-lisp-name ?source-object-name ?tf-name)
             (lisp-fun cram-tf:pose-stamped->transform-stamped ?target-pose-in-base ?tf-name
                       ?target-transform))
        (and (lisp-fun obj-int:get-object-transform ?current-source-object-designator ?target-transform)
             (lisp-fun obj-int:get-object-pose ?current-source-object-designator ?target-pose)
             (desig:designator :location ((:pose ?target-pose)) ?location)))
    (lisp-fun obj-int:get-object-grasping-poses
              ?source-object-name ?source-object-type :left ?grasp ?target-transform
              ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses
              ?source-object-name ?source-object-type :right ?grasp ?target-transform
              ?right-poses)
    (lisp-fun extract-pour-manipulation-poses ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses ?left-pour-poses ?right-pour-poses
                                 ?left-retract-poses ?right-retract-poses))))