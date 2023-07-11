(<- (desig:action-grounding ?action-designator (wipe ?arm ?towel-designator ?surface-designator))
    (spec:property ?action-designator (:type :cleaning))
    (spec:property ?action-designator (:object ?surface-designator))
    (spec:property ?surface-designator (:type ?surface-type))
    (obj-int:object-type-subtype :surface ?surface-type)
    (spec:property ?surface-designator (:urdf-name ?surface-name))
    (spec:property ?surface-designator (:part-of ?btr-environment))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:tool ?towel-designator))
    (spec:property ?towel-designator (:type :towel))
    (spec:property ?towel-designator (:part-of ?btr-environment))
    (spec:property ?towel-designator (:urdf-name ?towel-name))
    (lisp-fun get-surface-pose-and-transform ?surface-name ?btr-environment
              (?surface-pose ?surface-transform))
    (lisp-fun cram-mobile-pick-place-plans::extract-wipe-manipulation-poses
              ?arm ?surface-pose ?surface-transform
              ?towel-name
              (?reach-poses ?grasp-poses ?lift-poses))
    (-> (lisp-pred identity ?lift-poses)
        (equal ?lift-poses NIL)
        (true)))