(<- (desig:action-grounding ?action-designator (pour ?arm
                                                        ?source-container-designator
                                                        ?target-container-designator
                                                        ?source-container-opening
                                                        ?target-container-opening
                                                        ?source-container-distance
                                                        ?target-container-distance
                                                        ?source-container-left-reach-poses
                                                        ?source-container-right-reach-poses
                                                        ?source-container-left-grasp-poses
                                                        ?source-container-right-grasp-poses
                                                        (?source-container-left-lift-pose)
                                                        (?source-container-right-lift-pose)
                                                        (?source-container-left-2nd-lift-pose)
                                                        (?source-container-right-2nd-lift-pose)
                                                        ?source-container-joint-name
                                                        ?target-container-joint-name
                                                        ?environment-obj))
    (spec:property ?action-designator (:type :pouring))
    (spec:property ?action-designator (:source ?source-container-designator))
    (spec:property ?action-designator (:target ?target-container-designator))
    (spec:property ?source-container-designator (:type ?source-container-type))
    (spec:property ?target-container-designator (:type ?target-container-type))
    (obj-int:object-type-subtype :container ?source-container-type)
    (obj-int:object-type-subtype :container ?target-container-type)
    (spec:property ?source-container-designator (:urdf-name ?source-container-name))
    (spec:property ?target-container-designator (:urdf-name ?target-container-name))
    (spec:property ?source-container-designator (:part-of ?btr-environment))
    (spec:property ?target-container-designator (:part-of ?btr-environment))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:source-distance ?source-container-distance))
    (spec:property ?action-designator (:target-distance ?target-container-distance))
    (lisp-fun get-container-link ?source-container-name ?btr-environment ?source-container-link)
    (lisp-fun get-container-link ?target-container-name ?btr-environment ?target-container-link)
    (lisp-fun get-connecting-joint ?source-container-link ?connecting-joint)
    (lisp-fun get-connecting-joint ?target-container-link ?connecting-joint)
    (lisp-fun cl-urdf:name ?connecting-joint ?source-container-joint-name)
    (lisp-fun cl-urdf:name ?connecting-joint ?target-container-joint-name)
    (btr:bullet-world ?world)
    (lisp-fun btr:object ?world ?btr-environment ?environment-obj)
    (lisp-fun obj-int:get-object-type-gripper-opening ?source-container-type ?source-container-opening)
    (lisp-fun obj-int:get-object-type-gripper-opening ?target-container-type ?target-container-opening)
    (lisp-fun get-container-pose-and-transform ?source-container-name ?btr-environment
              (?source-container-pose ?source-container-transform))
    (lisp-fun get-container-pose-and-transform ?target-container-name ?btr-environment
              (?target-container-pose ?target-container-transform))
    (lisp-fun obj-int:get-object-grasping-poses ?source-container-name
              :container-prismatic :left :close ?source-container-transform ?source-container-left-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?source-container-name
              :container-prismatic :right :close ?source-container-transform ?source-container-right-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?target-container-name
              :container-prismatic :left :close ?target-container-transform ?target-container-left-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?target-container-name
              :container-prismatic :right :close ?target-container-transform ?target-container-right-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-pick-up-manipulation-poses
              ?arm ?source-container-left-poses ?source-container-right-poses
              (?source-container-left-reach-poses ?source-container-right-reach-poses
                                                 ?source-container-left-grasp-poses ?source-container-right-grasp-poses
                                                 ?source-container-left-lift-poses ?source-container-right-lift-poses))
    (lisp-fun cram-mobile-pick-place-plans::extract-pick-up-manipulation-poses
              ?arm ?target-container-left-poses ?target-container-right-poses
              (?target-container-left-reach-poses ?target-container-right-reach-poses
                                                 ?target-container-left-grasp-poses ?target-container-right-grasp-poses
                                                 ?target-container-left-lift-poses ?target-container-right-lift-poses))
    (-> (lisp-pred identity ?source-container-left-lift-poses)
        (equal ?source-container-left-lift-poses (?source-container-left-lift-pose ?source-container-left-2nd-lift-pose))
        (equal (NIL NIL) (?source-container-left-lift-pose ?source-container-left-2nd-lift-pose)))
    (-> (lisp-pred identity ?source-container-right-lift-poses)
        (equal ?source-container-right-lift-poses (?source-container-right-lift-pose ?source-container-right-2nd-lift-pose))
        (equal (NIL NIL) (?source-container-right-lift-pose ?source-container-right-2nd-lift-pose)))
    (-> (lisp-pred identity ?target-container-left-lift-poses)
        (equal ?target-container-left-lift-poses (?target-container-left-lift-pose ?target-container-left-2nd-lift-pose))
        (equal (NIL NIL) (?target-container-left-lift-pose ?target-container-left-2nd-lift-pose)))
    (-> (lisp-pred identity ?target-container-right-lift-poses)
        (equal ?target-container-right-lift-poses (?target-container-right-lift-pose ?target-container-right-2nd-lift-pose))
        (equal (NIL NIL) (?target-container-right-lift-pose ?target-container-right-2nd-lift-pose)))))