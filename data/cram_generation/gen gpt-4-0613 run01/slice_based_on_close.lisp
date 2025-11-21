(<- (desig:action-grounding ?action-designator (slice-object ?arm
                                                             ?knife
                                                             ?object
                                                             ?small-slice
                                                             ?big-slice))
    (spec:property ?action-designator (:type :slicing))
    (spec:property ?action-designator (:object ?object-designator))
    (spec:property ?object-designator (:type ?object-type))
    (obj-int:object-type-subtype :food ?object-type)
    (spec:property ?object-designator (:urdf-name ?object-name))
    (spec:property ?object-designator (:part-of ?btr-environment))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:tool ?knife))
    (btr:bullet-world ?world)
    (lisp-fun btr:object ?world ?btr-environment ?environment-obj)
    (lisp-fun get-object-pose-and-transform ?object-name ?btr-environment
              (?object-pose ?object-transform))
    (lisp-fun obj-int:get-object-slicing-poses ?object-name
              :food :small-slice ?object-transform ?small-slice)
    (lisp-fun obj-int:get-object-slicing-poses ?object-name
              :food :big-slice ?object-transform ?big-slice)))