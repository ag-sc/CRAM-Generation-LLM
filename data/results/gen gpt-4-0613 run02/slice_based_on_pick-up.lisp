(<- (desig:action-grounding ?action-designator (slice ?current-object-desig ?knife
                                                          ?cutting-board ?slice-size-small ?slice-size-big
                                                          ?cutting-poses ?left-slice-poses ?right-slice-poses))
    (spec:property ?action-designator (:type :slicing))
    (spec:property ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-desig)
    (spec:property ?current-object-desig (:type ?object-type))
    (spec:property ?current-object-desig (:name ?object-name))
    (-> (spec:property ?action-designator (:knife ?knife))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:tool ?robot ?knife)))
    (lisp-fun obj-int:get-object-transform ?current-object-desig ?object-transform)
    (lisp-fun obj-int:calculate-object-faces ?object-transform (?facing-robot-face ?bottom-face))
    (lisp-fun obj-int:get-object-type-slice-sizes ?object-type ?slice-size-small ?slice-size-big)
    (lisp-fun obj-int:get-object-cutting-poses
              ?object-name ?object-type :left ?knife ?object-transform
              ?left-poses)
    (lisp-fun obj-int:get-object-cutting-poses
              ?object-name ?object-type :right ?knife ?object-transform
              ?right-poses)
    (lisp-fun extract-slice-manipulation-poses ?knife ?left-poses ?right-poses
              (?cutting-poses ?left-slice-poses ?right-slice-poses)))