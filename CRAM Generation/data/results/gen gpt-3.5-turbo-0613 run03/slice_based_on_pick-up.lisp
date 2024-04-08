(<- (desig:action-grounding ?action-designator (slice ?current-object-desig ?knife
                                                      ?cutting-plane ?effort ?cutting-force
                                                      ?small-slice ?big-slice))
    (spec:property ?action-designator (:type :slicing))
    (spec:property ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-desig)
    (spec:property ?current-object-desig (:type ?object-type))
    (spec:property ?current-object-desig (:name ?object-name))
    (-> (spec:property ?action-designator (:knife ?knife))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:tool ?robot ?knife)))
    (lisp-fun obj-int:get-object-transform ?current-object-desig ?object-transform)
    (lisp-fun obj-int:calculate-object-faces ?object-transform (?facing-robot-face ?bottom-face))
    (-> (spec:property ?action-designator (:cutting-plane ?cutting-plane))
        (true)
        (and (lisp-fun obj-int:get-object-type-cutting-planes
                       ?object-type ?facing-robot-face ?bottom-face ?cutting-planes)
             (member ?cutting-plane ?cutting-planes)))
    (lisp-fun obj-int:get-object-type-cutting-effort ?object-type ?effort)
    (lisp-fun obj-int:get-object-type-cutting-force ?object-type ?cutting-force)
    (lisp-fun obj-int:get-object-slicing-poses
              ?object-name ?object-type ?cutting-plane ?object-transform
              ?small-slice ?big-slice))