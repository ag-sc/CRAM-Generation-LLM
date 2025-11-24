(<- (desig:action-grounding?action-designator (slice-object?arm 
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
                                                                 ?environment-obj
                                                                 ?knife-object
                                                                 ?cutting-surface))
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
    (lisp-fun obj-int:get-object-type-gripper-opening?object-type?gripper-opening)
    (lisp-fun get-object-pose-and-transform?object-name?btr-environment
              (?object-pose?object-transform))
    (lisp-fun obj-int:get-object-grasping-poses?object-name
              :food-prismatic :left :slice?object-transform?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses?object-name
              :food-prismatic :right :slice?object-transform?right-poses)
    (l