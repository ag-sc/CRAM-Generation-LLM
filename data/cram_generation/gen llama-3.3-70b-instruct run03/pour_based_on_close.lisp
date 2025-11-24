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
    (spec:property?source-container-designator (:type?source-container-type))
    (obj-int:object-type-subtype :container?source-container-type)
    (spec:property?source-container-designator (:urdf-name?source-container-name))
    (spec:property?source-container-designator (:part-of?btr-environment))
    (spec:property?action-designator (:target?target-container-designator))
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
    (lisp-fun get-container-link?target-container