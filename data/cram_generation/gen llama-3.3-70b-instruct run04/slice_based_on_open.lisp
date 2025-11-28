(<- (desig:action-grounding?action-designator (slice-object?arm 
                                                                ?gripper-holding
                                                                ?distance
                                                                ?left-reach-poses
                                                                ?right-reach-poses
                                                                ?left-grasp-poses
                                                                ?right-grasp-poses
                                                                 (?left-lift-pose)
                                                                 (?right-lift-pose)
                                                                 (?left-2nd-lift-pose)
                                                                 (?right-2nd-lift-pose)
                                                                ?joint-name?environment-obj?knife-object))
    (spec:property?action-designator (:type :slicing))
    (spec:property?action-designator (:object?object-designator))
    (spec:property?object-designator (:type?object-type))
    (obj-int:object-type-subtype :food?object-type)
    (spec:property?object-designator (:urdf-name?object-name))
    (spec:property?object-designator (:part-of?btr-environment))
    (-> (spec:property?action-designator (:arm?arm))
        (true)
        (and (cram-robot-interfaces:robot?robot)
             (cram-robot-interfaces:arm?robot?arm)))
    (spec:property?action-designator (:distance?distance))
    (lisp-fun get-object-link?object-name?btr-environment?object-link)
    (lisp-fun get-connecting-joint?object-link?connecting-joint)
    (lisp-fun cl-urdf:name?connecting-joint?joint-name)
    (btr:bullet-world?world)
    (lisp-fun btr:object?world?btr-environment?environment-obj)
    (lisp-fun obj-int:get-object-type-gripper-holding?object-type?gripper-holding)
    (lisp-fun get-object-pose-and-transform?object-name?btr-environment
              (?object-pose?object-transform))
    (lisp-fun obj-int:get-object-grasping-poses?object-name
              :food-prismatic :left :hold?object-transform?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses?object-name
              :food-prismatic :right :hold?object-transform?right-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-pick-up-manipulation-poses
             ?arm?left-poses?right-poses
              (?left-reach-poses?right-reach-poses
                                ?left-grasp-poses?right-grasp-poses
                                ?left-lift-poses?right-lift-poses))
    (lisp-fun get-knife-object?btr-environment?knife-object)
    (-> (lisp-pred identity?left-lift-poses)
        (equal?left-lift-poses (?left-lift-pose?left-2nd-lift-pose))
        (equal (NIL NIL) (?left-lift-pose?left-2nd-lift-pose)))
    (-> (lisp-pred identity?right-lift-poses)
        (equal?right-lift-poses (?right-lift-pose?right-2nd-lift-pose))
        (equal (NIL NIL) (?right-lift-pose?right-2nd-lift-pose)))
    (spec:property?action-designator (:slicing-parameters (:small-slice-size 0.3) (:big-slice-size 0.7)))