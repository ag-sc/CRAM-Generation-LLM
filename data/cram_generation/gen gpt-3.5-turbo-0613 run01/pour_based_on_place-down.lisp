(<- (desig:action-grounding ?action-designator (pour ?current-object-designator ?arm
                                                       ?left-reach-poses ?right-reach-poses
                                                       ?left-pour-poses ?right-pour-poses
                                                       ?left-retract-poses ?right-retract-poses
                                                       ?source-container ?target-container))
    (spec:property ?action-designator (:type :pouring))
    (-> (spec:property ?action-designator (:arm ?arm))
        (-> (spec:property ?action-designator (:object ?object-designator))
            (or (cpoe:object-in-hand ?object-designator ?arm)
                (and (format "WARNING: Wanted to pour an object ~a with arm ~a, ~
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
    (-> (spec:property ?action-designator (:source ?source-container))
        (and (desig:current-designator ?source-container ?current-source-designator)
             (desig:designator-groundings ?current-source-designator ?source-poses)
             (member ?source-pose ?source-poses)
             (symbol-value cram-tf:*robot-base-frame* ?base-frame)
             (lisp-fun cram-tf:ensure-pose-in-frame ?source-pose ?base-frame :use-zero-time t
                       ?source-pose-in-base)
             (lisp-fun roslisp-utilities:rosify-underscores-lisp-name ?object-name ?tf-name)
             (lisp-fun cram-tf:pose-stamped->transform-stamped ?source-pose-in-base ?tf-name
                       ?source-transform))
        (and (lisp-fun obj-int:get-object-transform ?current-source-designator ?source-transform)
             (lisp-fun obj-int:get-object-pose ?current-source-designator ?source-pose)
             (desig:designator :source ((:pose ?source-pose)) ?source-container)))
    (-> (spec:property ?action-designator (:target ?target-container))
        (and (desig:current-designator ?target-container ?current-target-designator)
             (desig:designator-groundings ?current-target-designator ?target-poses)
             (member ?target-pose ?target-poses)
             (symbol-value cram-tf:*robot-base-frame* ?base-frame)
             (lisp-fun cram-tf:ensure-pose-in-frame ?target-pose ?base-frame :use-zero-time t
                       ?target-pose-in-base)
             (lisp-fun roslisp-utilities:rosify-underscores-lisp-name ?object-name ?tf-name)
             (lisp-fun cram-tf:pose-stamped->transform-stamped ?target-pose-in-base ?tf-name
                       ?target-transform))
        (and (lisp-fun obj-int:get-object-transform ?current-target-designator ?target-transform)
             (lisp-fun obj-int:get-object-pose ?current-target-designator ?target-pose)
             (desig:designator :target ((:pose ?target-pose)) ?target-container)))
    (lisp-fun obj-int:get-object-grasping-poses
              ?object-name ?object-type :left ?grasp ?source-transform
              ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses
              ?object-name ?object-type :right ?grasp ?source-transform
              ?right-poses)
    (lisp-fun extract-pour-manipulation-poses ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses ?left-pour-poses ?right-pour-poses
                                 ?left-retract-poses ?right-retract-poses))))