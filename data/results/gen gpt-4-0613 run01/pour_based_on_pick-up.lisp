(<- (desig:action-grounding ?action-designator (pour ?arm
                                                      ?source-container
                                                      ?target-container
                                                      ?pouring-poses
                                                      ?joint-name ?environment-obj))
    (spec:property ?action-designator (:type :pouring))
    (spec:property ?action-designator (:source-object ?source-container-designator))
    (spec:property ?source-container-designator (:type ?source-container-type))
    (obj-int:object-type-subtype :container ?source-container-type)
    (spec:property ?source-container-designator (:urdf-name ?source-container-name))
    (spec:property ?source-container-designator (:part-of ?btr-environment))
    (spec:property ?action-designator (:target-object ?target-container-designator))
    (spec:property ?target-container-designator (:type ?target-container-type))
    (obj-int:object-type-subtype :container ?target-container-type)
    (spec:property ?target-container-designator (:urdf-name ?target-container-name))
    (spec:property ?target-container-designator (:part-of ?btr-environment))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (btr:bullet-world ?world)
    (lisp-fun btr:object ?world ?btr-environment ?environment-obj)
    (lisp-fun get-container-link ?source-container-name ?btr-environment ?source-container-link)
    (lisp-fun get-connecting-joint ?source-container-link ?connecting-joint)
    (lisp-fun cl-urdf:name ?connecting-joint ?joint-name)
    (lisp-fun get-container-pose-and-transform ?source-container-name ?btr-environment
              (?source-container-pose ?source-container-transform))
    (lisp-fun get-container-pose-and-transform ?target-container-name ?btr-environment
              (?target-container-pose ?target-container-transform))
    (lisp-fun obj-int:get-object-pouring-poses ?source-container-name
              :container-prismatic :open ?source-container-transform ?pouring-poses))