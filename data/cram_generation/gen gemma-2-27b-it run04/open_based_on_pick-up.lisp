(<- (desig:action-grounding ?action-designator (open ?current-object-desig ?arm ?effort ?opening-angle ?left-reach-poses ?right-reach-poses ?left-open-poses ?right-open-poses)
    (spec:property ?action-designator (:type :opening))
    (spec:property ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-desig)
    (spec:property ?current-object-desig (:type ?object-type))
    (spec:property ?current-object-desig (:name ?object-name))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (lisp-fun obj-int:get-object-transform ?current-object-desig ?object-transform)
    (lisp-fun obj-int:calculate-object-faces ?object-transform (?facing-robot-face ?top-face))
    (-> (obj-int:object-rotationally-symmetric ?object-type)
        (equal ?rotationally-symmetric t)
        (equal ?rotationally-symmetric nil))
    (-> (spec:property ?action-designator (:opening-angle ?opening-angle))
        (true)
        (and (lisp-fun obj-int:get-object-type-opening-angles ?object-type ?facing-robot-face ?top-face ?rotationally-symmetric ?arm ?opening-angles)
             (member ?opening-angle ?opening-angles)))
    (lisp-fun obj-int:get-object-type-opening-effort ?object-type ?effort)
    (lisp-fun obj-int:get-object-opening-poses
              ?object-name ?object-type :left ?opening-angle ?object-transform
              ?left-poses)
    (lisp-fun obj-int:get-object-opening-poses
              ?object-name ?object-type :right ?opening-angle ?object-transform
              ?right-poses)
    (lisp-fun extract-open-manipulation-poses ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-open-poses ?right-open-poses))))