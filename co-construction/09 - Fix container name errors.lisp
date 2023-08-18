(<- (desig:action-grounding ?action-designator (pick-up-object ?arm
                                                            ?gripper-opening
                                                            ?distance
                                                            ?left-reach-poses
                                                            ?right-reach-poses
                                                            ?left-grasp-poses
                                                            ?right-grasp-poses
                                                            (?left-lift-pose)
                                                            (?right-lift-pose)
                                                            (?left-2nd-lift-pose)
                                                            (?right-2nd-lift-pose)
                                                            ?joint-name
                                                            ?environment-obj))
    (spec:property ?action-designator (:type :picking-up))
    (spec:property ?action-designator (:object ?container-designator))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:distance ?distance))
    (spec:property ?container-designator (:type ?container-type))
    (obj-int:object-type-subtype :container ?container-type)
    (spec:property ?container-designator (:urdf-name ?urdf-name)) ; Corrected to :urdf-name
    (lisp-fun get-container-link ?urdf-name ?btr-environment ?container-link) ; Corrected variable name
    (lisp-fun get-connecting-joint ?container-link ?connecting-joint)
    (lisp-fun cl-urdf:name ?connecting-joint ?joint-name)
    (btr:bullet-world ?world)
    (lisp-fun btr:object ?world ?btr-environment ?environment-obj)
    (lisp-fun obj-int:get-object-type-gripper-opening ?container-type ?gripper-opening)
    (lisp-fun get-container-pose-and-transform ?urdf-name ?btr-environment  ; Corrected variable name
              (?container-pose ?container-transform)) 
    (lisp-fun obj-int:get-object-grasping-poses ?urdf-name ; Corrected variable name
              :container-prismatic :left :pick-up ?container-transform ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?urdf-name ; Corrected variable name
              :container-prismatic :right :pick-up ?container-transform ?right-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-pick-up-manipulation-poses
              ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-grasp-poses ?right-grasp-poses
                                 ?left-lift-poses ?right-lift-poses))
    (-> (lisp-pred identity ?left-lift-poses)
        (equal ?left-lift-poses (?left-lift-pose ?left-2nd-lift-pose))
        (equal (NIL NIL) (?left-lift-pose ?left-2nd-lift-pose)))
    (-> (lisp-pred identity ?right-lift-poses)
        (equal ?right-lift-poses (?right-lift-pose ?right-2nd-lift-pose))
        (equal (NIL NIL) (?right-lift-pose ?right-2nd-lift-pose))))