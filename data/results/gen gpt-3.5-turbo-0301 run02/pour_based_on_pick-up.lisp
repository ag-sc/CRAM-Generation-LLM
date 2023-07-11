(<- (desig:action-grounding ?action-designator (pour ?source-container-designator
                                                      ?target-container-designator
                                                      ?pouring-arm
                                                      ?pouring-gripper-opening
                                                      ?pouring-distance
                                                      ?source-container-left-reach-poses
                                                      ?source-container-right-reach-poses
                                                      ?source-container-left-grasp-poses
                                                      ?source-container-right-grasp-poses
                                                      ?target-container-left-reach-poses
                                                      ?target-container-right-reach-poses
                                                      ?target-container-left-grasp-poses
                                                      ?target-container-right-grasp-poses
                                                      ?joint-name ?environment-obj))
    (spec:property ?action-designator (:type :pouring))
    (spec:property ?action-designator (:source ?source-container-designator))
    (spec:property ?source-container-designator (:type ?source-container-type))
    (obj-int:object-type-subtype :container ?source-container-type)
    (spec:property ?source-container-designator (:urdf-name ?source-container-name))
    (spec:property ?source-container-designator (:part-of ?btr-environment))
    (spec:property ?action-designator (:target ?target-container-designator))
    (spec:property ?target-container-designator (:type ?target-container-type))
    (obj-int:object-type-subtype :container ?target-container-type)
    (spec:property ?target-container-designator (:urdf-name ?target-container-name))
    (spec:property ?target-container-designator (:part-of ?btr-environment))
    (-> (spec:property ?action-designator (:arm ?pouring-arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?pouring-arm)))
    (spec:property ?action-designator (:distance ?pouring-distance))
    (lisp-fun get-container-link ?source-container-name ?btr-environment ?source-container-link)
    (lisp-fun get-connecting-joint ?source-container-link ?connecting-joint)
    (lisp-fun cl-urdf:name ?connecting-joint ?joint-name)
    (btr:bullet-world ?world)
    (lisp-fun btr:object ?world ?btr-environment ?environment-obj)
    (lisp-fun obj-int:get-object-type-gripper-opening ?source-container-type ?pouring-gripper-opening)
    (lisp-fun get-container-pose-and-transform ?source-container-name ?btr-environment
              (?source-container-pose ?source-container-transform))
    (lisp-fun obj-int:get-object-grasping-poses ?source-container-name
              :container-prismatic :left :open ?source-container-transform ?source-container-left-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?source-container-name
              :container-prismatic :right :open ?source-container-transform ?source-container-right-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?target-container-name
              :container-prismatic :left :open ?source-container-transform ?target-container-left-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?target-container-name
              :container-prismatic :right :open ?source-container-transform ?target-container-right-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-pour-manipulation-poses
              ?pouring-arm ?source-container-left-poses ?source-container-right-poses
              ?target-container-left-poses ?target-container-right-poses
              (?source-container-lift-poses ?target-container-lift-poses))
    (-> (lisp-pred identity ?source-container-lift-poses)
        (equal ?source-container-lift-poses ?target-container-lift-poses)))