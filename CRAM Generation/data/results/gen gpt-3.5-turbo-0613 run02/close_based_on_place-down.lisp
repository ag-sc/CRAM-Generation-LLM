(<- (desig:action-grounding ?action-designator (close-container ?container-designator))
    (spec:property ?action-designator (:type :closing))
    (spec:property ?action-designator (:container ?container-designator))
    (desig:current-designator ?container-designator ?current-container-designator)
    (spec:property ?current-container-designator (:type ?container-type))
    (spec:property ?current-container-designator (:name ?container-name))
    (obj-int:container-type-closing ?container-type ?closing)
    (-> (spec:property ?action-designator (:container ?container-designator))
        (and (desig:current-designator ?container-designator ?current-container-designator)
             (desig:designator-groundings ?current-container-designator ?poses)
             (member ?target-pose ?poses)
             (symbol-value cram-tf:*robot-base-frame* ?base-frame)
             (lisp-fun cram-tf:ensure-pose-in-frame ?target-pose ?base-frame :use-zero-time t
                       ?target-pose-in-base)
             (lisp-fun roslisp-utilities:rosify-underscores-lisp-name ?container-name ?tf-name)
             (lisp-fun cram-tf:pose-stamped->transform-stamped ?target-pose-in-base ?tf-name
                       ?target-transform))
        (and (lisp-fun obj-int:get-container-transform ?current-container-designator ?target-transform)
             (lisp-fun obj-int:get-container-pose ?current-container-designator ?target-pose)
             (desig:designator :container ((:pose ?target-pose)) ?container-designator))))