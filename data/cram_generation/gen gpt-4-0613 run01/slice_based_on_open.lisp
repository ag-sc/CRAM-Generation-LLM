(<- (desig:action-grounding ?action-designator (slice-object ?arm
                                                             ?knife
                                                             ?cutting-board
                                                             ?food-object
                                                             ?small-slice
                                                             ?big-slice))
    (spec:property ?action-designator (:type :slicing))
    (spec:property ?action-designator (:object ?food-designator))
    (spec:property ?food-designator (:type ?food-type))
    (obj-int:object-type-subtype :food ?food-type)
    (spec:property ?food-designator (:urdf-name ?food-name))
    (spec:property ?food-designator (:part-of ?btr-environment))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:knife ?knife))
    (spec:property ?action-designator (:cutting-board ?cutting-board))
    (btr:bullet-world ?world)
    (lisp-fun btr:object ?world ?btr-environment ?environment-obj)
    (lisp-fun get-food-object-pose-and-transform ?food-name ?btr-environment
              (?food-object-pose ?food-object-transform))
    (lisp-fun obj-int:get-object-slicing-poses ?food-name
              :food :small-slice ?food-object-transform ?small-slice)
    (lisp-fun obj-int:get-object-slicing-poses ?food-name
              :food :big-slice ?food-object-transform ?big-slice)))