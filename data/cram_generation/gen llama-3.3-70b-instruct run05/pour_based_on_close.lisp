(<- (desig:action-grounding?action-designator (pour-container?arm 
                                                                 ?gripper-opening
                                                                 ?distance
                                                                 ?source-left-reach-poses
                                                                 ?source-right-reach-poses
                                                                 ?source-left-grasp-poses
                                                                 ?source-right-grasp-poses
                                                                  (?source-left-lift-pose)
                                                                  (?source-right-lift-pose)
                                                                  (?source-left-2nd-lift-pose)
                                                                  (?source-right-2nd-lift-pose)
                                                                 ?target-left-reach-poses
                                                                 ?target-right-reach-poses
                                                                 ?target-left-grasp-poses
                                                                 ?target-right-grasp-poses
                                                                  (?target-left-lift-pose)
                                                                  (?target-right-lift-pose)
                                                                  (?target-left-2nd-lift-pose)
                                                                  (?target-right-2nd-lift-pose)
                                                                 ?joint-name
                                                                 ?environment-obj
                                                                 ?source-container-designator
                                                                 ?target-container-designator))
    (spec:property?action-designator (:type :pouring))
    (spec:property?action-designator (:object?source-container-designator))
    (spec:property?action-designator (:target?target-container-designator))
    (spec:property?source-container-designator (:type?source-container-type))
    (obj-int:object-type-subtype :container?source-container-type)
    (spec:property?source-container-designator (:urdf-name?source-container-name))
    (spec:property?source-container-designator (:part-of?btr-environment))
    (spec:property?target-container-designator (:type?target-container-type))
    (obj-int:object-type-subtype :container?target-container-type)
    (spec:property?target-container-designator (:urdf-name?target-container-name))
    (spec:property?target-container-designator (:part-of?btr-environment))
    (-> (spec:property?action-designator (:arm?arm))
        (true)
        (and (cram-robot-interfaces:robot?robot)
             (cram-robot-interfaces:arm?robot?arm)))
    (spec:property?action-designator (:distance?distance))
    (lisp-fun get-container-link?source-container-name?btr-environment?source-container-link)
    (lisp-fun get-container-link?target-container-name?btr-environment?target-container-link)
    (lisp-fun get-connecting-joint?source-container-link?connecting-joint)
    (lisp-fun cl-urdf:name?connecting-joint?joint-name)
    (btr:bullet-world?world)
    (lisp-fun btr:object?world?btr-environment?environment-obj)
    (lisp-fun obj-int:get-object-type-gripper-opening?source-container-type?gripper-opening)
    (lisp-fun get-container-pose-and-transform?source-container-name?btr-environment
              (?source-container-pose?source-container-transform))
    (lisp-fun get-container-pose-and-transform?target-container-name?btr-environment
              (?target-container-pose?target-container-transform))
    (lisp-fun obj-int:get-object-grasping-poses?source-container-name
              :container-prismatic :left :close?source-container-transform?source-left-poses)
    (lisp-fun obj-int:get-object-grasping-poses?source-container-name
              :container-prismatic :right :close?source-container-transform?source-right-poses)
    (lisp-fun obj-int:get-object-grasping-poses?target-container-name
              :container-prismatic :left :open?target-container-transform?target-left-poses)
    (lisp-fun obj-int:get-object-grasping-poses?target-container-name
              :container-prismatic :right :open?target-container-transform?target-right-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-pick-up-manipulation-poses
             ?arm?source-left-poses?source-right-poses
              (?source-left-reach-poses?source-right-reach-poses
                                ?source-left-grasp-poses?source-right-grasp-poses
                                ?source-left-lift-poses?source-right-lift-poses))
    (lisp-fun cram-mobile-pick-place-plans::extract-pick-up-manipulation-poses
             ?arm?target-left-poses?target-right-poses
              (?target-left-reach-poses?target-right-reach-poses
                                ?target-left-grasp-poses?target-right-grasp-poses
                                ?target-left-lift-poses?target-right-lift-poses))
    (-> (lisp-pred identity?source-left-lift-poses)
        (equal?source-left-lift-poses (?source-left-lift-pose?source-left-2nd-lift-pose))
        (equal (NIL NIL) (?source-left-lift-pose?source-left-2nd-lift-pose)))
    (-> (lisp-pred identity?source-right-lift-poses)
        (equal?source-right-lift-poses (?source-right-lift-pose?source-right-2nd-lift-pose))
        (equal (NIL NIL) (?source-right-lift-pose?source-right-2nd-lift-pose))
    (-> (lisp-pred identity?target-left-lift-poses)
        (equal?target-left-lift-poses (?target-left-lift-pose?target-left-2nd-lift-pose))
        (equal (NIL NIL) (?target-left-lift-pose?target-left-2nd-lift-pose)))
    (-> (lisp-pred identity?target-right-lift-poses)
        (equal?target-right-lift-poses (?target-right-lift-pose?target-right-2nd-lift-pose))
        (equal (NIL NIL) (?target-right-lift-pose?target-right-2nd-lift-pose)))