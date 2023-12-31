(<- (desig:action-grounding ?action-designator (slice ?object-designator ?knife-designator ?small-slice ?big-slice))
    (spec:property ?action-designator (:type :slicing))
    (-> (spec:property ?action-designator (:object ?object-designator))
        (cpoe:object-in-hand ?object-designator ?hand))
    (-> (spec:property ?action-designator (:tool ?knife-designator))
        (cpoe:object-in-hand ?knife-designator ?hand))
    (desig:current-designator ?object-designator ?current-object-designator)
    (spec:property ?current-object-designator (:type ?object-type))
    (spec:property ?current-object-designator (:name ?object-name))
    (lisp-fun obj-int:slice-object ?object-name ?object-type ?knife-designator
              ?small-slice ?big-slice)))