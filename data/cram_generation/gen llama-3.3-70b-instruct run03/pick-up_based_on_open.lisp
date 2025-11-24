(<- (desig:action-grounding?action-designator (pick-up?arm 
                                                                ?gripper-closing
                                                                ?distance
                                                                ?left-reach-poses
                                                                ?right-reach-poses
                                                                ?left-grasp-poses
                                                                ?right-grasp-poses
                                                                 (?left-lift-pose)
                                                                 (?right-lift-pose)
                                                                 (?left-2nd-lift-pose)
                                                                 (?right-2nd-lift-pose)
                                                                ?joint-name?environment-obj?object-designator))
    (spec:property?action-designator (:type :picking-up))
    (spec:property?action-designator (:object?object-designator))
    (spec:property?object-designator (:type?object-type))
    (obj-int:object-type-subtype?object-type)
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
    (lisp-fun obj-int:get-object-type-gripper-closing?object-type?gripper-closing)
    (lisp-fun get-object-pose-and-transform?object-name?btr-environment
              (?object-pose?object-transform))
    (lisp-fun obj-int:get-object-grasping-poses?object-name
             ?object-type :left :pick-up?object-transform?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses?object-name
             ?object-type :right :pick-up?object-transform?right-poses)
    (lisp-fun cram-mobile-pick-place