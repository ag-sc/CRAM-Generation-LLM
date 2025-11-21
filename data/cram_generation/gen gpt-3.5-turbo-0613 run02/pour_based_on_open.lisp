(<- (desig:action-grounding ?action-designator (pour ?source-container-designator ?target-container-designator))
    (spec:property ?action-designator (:type :pouring))
    (spec:property ?action-designator (:source ?source-container-designator))
    (spec:property ?action-designator (:target ?target-container-designator)))