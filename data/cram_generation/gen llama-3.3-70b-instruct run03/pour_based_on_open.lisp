(<- (desig:action-grounding?action-designator (pour?arm 
                                                                ?gripper-opening
                                                                ?distance
                                                                ?source-container
                                                                ?target-container
                                                                ?left-reach-poses
                                                                ?right-reach-poses
                                                                ?left-grasp-poses
                                                                ?right-grasp-poses
                                                                 (?left-lift-pose)
                                                                 (?right-lift-pose)
                                                                 (?left-2nd-lift-pose)
                                                                 (?right-2nd-lift-pose)
                                                                ?joint-name?environment-obj))
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
    (lisp-fun obj-int:get-object-type