(<- (desig:action-grounding ?action-designator (open ?container-designator ?arm
                                                        ?left-reach-poses ?right-reach-poses
                                                        ?left-put-poses ?right-put-poses
                                                        ?left-retract-poses ?right-retract-poses))
    (spec:property ?action-designator (:type :opening))
    (-> (spec:property ?action-designator (:container ?container-designator))
        (cpoe:object-in-view ?container-designator))
    (-> (spec:property ?action-designator (:arm ?arm))
        (-> (spec:property ?action-designator (:container ?container-designator))
            (cpoe:object-in-view ?container-designator))))
    (desig:current-designator ?container-designator ?current-container-designator)
    (spec:property ?current-container-designator (:type ?container-type))
    (spec:property ?current-container-designator (:name ?container-name))
    (obj-int:container-type-open ?container-type ?open-action)
    (lisp-fun obj-int:get-object-opening-poses
              ?container-name ?container-type :left ?open-action
              ?left-poses)
    (lisp-fun obj-int:get-object-opening-poses
              ?container-name ?container-type :right ?open-action
              ?right-poses)
    (lisp-fun extract-open-manipulation-poses ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses ?left-put-poses ?right-put-poses
                                 ?left-retract-poses ?right-retract-poses))))