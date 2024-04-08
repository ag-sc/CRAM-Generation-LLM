(<- (desig:action-grounding ?action-designator (wipe-surface ?arm
                                                             ?gripper-opening
                                                             ?distance
                                                             ?left-reach-poses
                                                             ?right-reach-poses
                                                             ?left-wipe-poses
                                                             ?right-wipe-poses
                                                             (?left-lift-pose)
                                                             (?right-lift-pose)
                                                             (?left-2nd-lift-pose)
                                                             (?right-2nd-lift-pose)
                                                             ?joint-name
                                                             ?environment-obj))
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
    (spec:property ?action-designator (:distance ?distance))
    (lisp-fun get-surface-link ?surface-name ?btr-environment ?surface-link)
    (lisp-fun get-connecting-joint ?surface-link ?connecting-joint)
    (lisp-fun cl-urdf:name ?connecting-joint ?joint-name)
    (btr:bullet-world ?world)
    (lisp-fun btr:object ?world ?btr-environment ?environment-obj)
    (lisp-fun obj-int:get-object-type-gripper-opening ?surface-type ?gripper-opening)
    (lisp-fun get-surface-pose-and-transform ?surface-name ?btr-environment
              (?surface-pose ?surface-transform))
    (lisp-fun obj-int:get-object-wiping-poses ?surface-name
              :surface-prismatic :left :wipe ?surface-transform ?left-poses)
    (lisp-fun obj-int:get-object-wiping-poses ?surface-name
              :surface-prismatic :right :wipe ?surface-transform ?right-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-wipe-up-manipulation-poses
              ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-wipe-poses ?right-wipe-poses
                                 ?left-lift-poses ?right-lift-poses))
    (-> (lisp-pred identity ?left-lift-poses)
        (equal ?left-lift-poses (?left-lift-pose ?left-2nd-lift-pose))
        (equal (NIL NIL) (?left-lift-pose ?left-2nd-lift-pose)))
    (-> (lisp-pred identity ?right-lift-poses)
        (equal ?right-lift-poses (?right-lift-pose ?right-2nd-lift-pose))
        (equal (NIL NIL) (?right-lift-pose ?right-2nd-lift-pose)))))