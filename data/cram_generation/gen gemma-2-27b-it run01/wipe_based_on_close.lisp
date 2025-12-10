(<- (desig:action-grounding ?action-designator (wipe-surface ?arm
                                                                  ?gripper-opening
                                                                  ?distance
                                                                  ?left-reach-poses
                                                                  ?right-reach-poses
                                                                  ?left-grasp-poses
                                                                  ?right-grasp-poses
                                                                  (?left-wipe-pose)
                                                                  (?right-wipe-pose)
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
    (lisp-fun obj-int:get-object-grasping-poses ?surface-name
              :surface-planar :left :wipe ?surface-transform ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?surface-name
              :surface-planar :right :wipe ?surface-transform ?right-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-pick-up-manipulation-poses
              ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-grasp-poses ?right-grasp-poses
                                 ?left-wipe-poses ?right-wipe-poses))
    (-> (lisp-pred identity ?left-wipe-poses)
        (equal ?left-wipe-poses (?left-wipe-pose))
        (equal (NIL) (?left-wipe-pose)))
    (-> (lisp-pred identity ?right-wipe-poses)
        (equal ?right-wipe-poses (?right-wipe-pose))
        (equal (NIL) (?right-wipe-pose))))