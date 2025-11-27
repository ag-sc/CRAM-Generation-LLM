(<- (desig:action-grounding ?action-designator (wipe ?surface-desig ?arm ?towel ?effort ?reach-poses ?wipe-poses ?lift-poses))
    (spec:property ?action-designator (:type :wiping))
    (spec:property ?action-designator (:surface ?surface-designator))
    (desig:current-designator ?surface-designator ?surface-desig)
    (spec:property ?surface-desig (:type ?surface-type))
    (spec:property ?surface-desig (:name ?surface-name))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (lisp-fun obj-int:get-object-transform ?surface-desig ?surface-transform)
    (lisp-fun obj-int:calculate-object-faces ?surface-transform (?facing-robot-face ?top-face))
    (-> (obj-int:surface-rotationally-symmetric ?surface-type)
        (equal ?rotationally-symmetric t)
        (equal ?rotationally-symmetric nil))
    (lisp-fun obj-int:get-surface-type-wiping-effort ?surface-type ?effort)
    (lisp-fun obj-int:get-surface-type-wiping-poses
              ?surface-name ?surface-type :left ?towel ?surface-transform
              ?left-poses)
    (lisp-fun obj-int:get-surface-type-wiping-poses
              ?surface-name ?surface-type :right ?towel ?surface-transform
              ?right-poses)
    (lisp-fun extract-wipe-manipulation-poses ?arm ?left-poses ?right-poses
              (?reach-poses ?wipe-poses ?lift-poses)))