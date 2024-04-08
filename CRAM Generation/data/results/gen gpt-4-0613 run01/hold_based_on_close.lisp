(<- (desig:action-grounding ?action-designator (hold-object ?arm
                                                            ?gripper-opening
                                                            ?object-designator
                                                            ?object-type
                                                            ?object-name
                                                            ?btr-environment
                                                            ?object-link
                                                            ?connecting-joint
                                                            ?joint-name
                                                            ?environment-obj))
    (spec:property ?action-designator (:type :holding))
    (spec:property ?action-designator (:object ?object-designator))
    (spec:property ?object-designator (:type ?object-type))
    (spec:property ?object-designator (:urdf-name ?object-name))
    (spec:property ?object-designator (:part-of ?btr-environment))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (lisp-fun get-object-link ?object-name ?btr-environment ?object-link)
    (lisp-fun get-connecting-joint ?object-link ?connecting-joint)
    (lisp-fun cl-urdf:name ?connecting-joint ?joint-name)
    (btr:bullet-world ?world)
    (lisp-fun btr:object ?world ?btr-environment ?environment-obj)
    (lisp-fun obj-int:get-object-type-gripper-opening ?object-type ?gripper-opening))