(<- (desig:action-grounding ?action-designator (pour ?source-container-designator
                                                      ?target-container-designator
                                                      ?pouring-arm
                                                      ?pouring-gripper-opening
                                                      ?pouring-distance
                                                      ?source-container-pose
                                                      ?source-container-transform
                                                      ?target-container-pose
                                                      ?target-container-transform
                                                      ?pouring-poses
                                                      ?joint-name
                                                      ?environment-obj))
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
    (lisp-fun get-container-pose-and-transform ?target-container-name ?btr-environment
              (?target-container-pose ?target-container-transform))
    (lisp-fun obj-int:get-object-grasping-poses ?source-container-name
              :container-prismatic :left :open ?source-container-transform ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?source-container-name
              :container-prismatic :right :open ?source-container-transform ?right-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-pouring-manipulation-poses
              ?pouring-arm ?left-poses ?right-poses ?target-container-pose
              (?pouring-poses))
    (lisp-fun obj-int:get-object-grasping-poses ?target-container-name
              :container-prismatic :left :open ?target-container-transform ?target-left-poses)
    (lisp-fun obj-int:get-object-grasping-poses ?target-container-name
              :container-prismatic :right :open ?target-container-transform ?target-right-poses))