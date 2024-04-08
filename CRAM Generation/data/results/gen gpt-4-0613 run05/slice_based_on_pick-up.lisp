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
    (-> (obj-int:object-rotationally-symmetric ?object-type)
        (equal ?rotationally-symmetric t)
        (equal ?rotationally-symmetric nil))
    (lisp-fun obj-int:get-object-type-slice-size ?object-type ?slice-size)
    (lisp-fun obj-int:get-object-slicing-poses
              ?object-name ?object-type :left ?knife ?object-transform
              ?left-poses)
    (lisp-fun obj-int:get-object-slicing-poses
              ?object-name ?object-type :right ?knife ?object-transform
              ?right-poses)
    (lisp-fun extract-slice-manipulation-poses ?knife ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-slice-poses ?right-slice-poses
                                 ?left-lift-poses ?right-lift-poses)))