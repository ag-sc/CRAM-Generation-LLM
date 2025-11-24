(<- (desig:action-grounding?action-designator (hold-object?arm 
                                                                 ?gripper-opening
                                                                 ?object-designator
                                                                 ?grasp-pose
                                                                 ?lift-pose
                                                                 ?joint-name
                                                                 ?environment-obj))
    (spec:property?action-designator (:type :holding))
    (spec:property?action-designator (:object?object-designator))
    (spec:property?object-designator (:type?object-type))
    (obj-int:object-type-subtype?object-type)
    (spec:property?object-designator (:urdf-name?object-name))
    (spec:property?object-designator (:part-of?btr-environment))
    (-> (spec:property?action-designator (:arm?arm))
        (true)
        (and (cram-robot-interfaces:robot?robot)
             (cram-robot-interfaces:arm?robot?arm)))
    (spec:property?action-designator (:gripper-opening?gripper-opening))
    (lisp-fun get-object-link?object-name?btr-environment?object-link)
    (lisp-fun get-connecting-joint?object-link?connecting-joint)
    (lisp-fun cl-urdf:name?connecting-joint?joint-name)
    (btr:bullet-world?world)
    (lisp-fun btr:object?world?btr-environment?environment-obj)
    (lisp-fun obj-int:get-object-type-gripper-opening?object-type?gripper-opening)
    (lisp-fun get-object-pose-and-transform?object-name?btr-environment
              (?object-pose?object-transform))
    (lisp-fun obj-int:get-object-grasping-poses?object-name
             ?object-type :firm?object-transform?grasp-pose)
    (lisp-fun cram-mobile-pick-place-plans::extract-lift-manipulation-pose
             ?arm?grasp-pose?lift-pose))