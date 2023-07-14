(<- (desig:action-grounding ?action-designator (wipe-surface ?arm
                                                             ?towel
                                                             ?surface
                                                             ?wipe-pattern
                                                             ?wipe-force
                                                             ?wipe-duration))
    (spec:property ?action-designator (:type :wiping))
    (spec:property ?action-designator (:object ?surface-designator))
    (spec:property ?surface-designator (:type ?surface-type))
    (obj-int:object-type-subtype :surface ?surface-type)
    (spec:property ?surface-designator (:urdf-name ?surface-name))
    (spec:property ?surface-designator (:part-of ?btr-environment))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:towel ?towel))
    (spec:property ?action-designator (:wipe-pattern ?wipe-pattern))
    (spec:property ?action-designator (:wipe-force ?wipe-force))
    (spec:property ?action-designator (:wipe-duration ?wipe-duration))
    (btr:bullet-world ?world)
    (lisp-fun btr:object ?world ?btr-environment ?environment-obj)
    (lisp-fun get-surface-pose-and-transform ?surface-name ?btr-environment
              (?surface-pose ?surface-transform))
    (lisp-fun obj-int:get-object-wiping-poses ?surface-name
              :surface-prismatic :left :open ?surface-transform ?left-poses)
    (lisp-fun obj-int:get-object-wiping-poses ?surface-name
              :surface-prismatic :right :open ?surface-transform ?right-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-wipe-manipulation-poses
              ?arm ?left-poses ?right-poses
              (?left-wipe-poses ?right-wipe-poses)))