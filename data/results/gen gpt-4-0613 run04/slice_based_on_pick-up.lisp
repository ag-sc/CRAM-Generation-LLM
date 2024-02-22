(<- (desig:action-grounding ?action-designator (slice ?current-object-desig ?knife
                                                          ?cutting-board ?slice-size))
    (spec:property ?action-designator (:type :slicing))
    (spec:property ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-desig)
    (spec:property ?current-object-desig (:type ?object-type))
    (spec:property ?current-object-desig (:name ?object-name))
    (-> (spec:property ?action-designator (:knife ?knife))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:tool ?robot ?knife)))
    (-> (spec:property ?action-designator (:cutting-board ?cutting-board))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:tool ?robot ?cutting-board)))
    (lisp-fun obj-int:get-object-transform ?current-object-desig ?object-transform)
    (lisp-fun obj-int:calculate-object-faces ?object-transform (?facing-robot-face ?bottom-face))
    (-> (spec:property ?action-designator (:slice-size ?slice-size))
        (true)
        (and (lisp-fun obj-int:get-object-size
                       ?object-type ?facing-robot-face ?bottom-face ?slice-size)
             (member ?slice-size '(:small :big))))
    (lisp-fun obj-int:get-object-cutting-poses
              ?object-name ?object-type :left ?knife ?cutting-board ?object-transform
              ?left-poses)
    (lisp-fun obj-int:get-object-cutting-poses
              ?object-name ?object-type :right ?knife ?cutting-board ?object-transform
              ?right-poses)
    (lisp-fun extract-slice-manipulation-poses ?knife ?cutting-board ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-cut-poses ?right-cut-poses
                                 ?left-lift-poses ?right-lift-poses)))