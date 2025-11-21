(<- (desig:action-grounding ?action-designator (pour ?source-container-desig ?target-container-desig
                                                      ?pouring-effort ?pouring-poses))
    (spec:property ?action-designator (:type :pouring))
    (spec:property ?action-designator (:source-container ?source-container-designator))
    (spec:property ?action-designator (:target-container ?target-container-designator))
    (desig:current-designator ?source-container-designator ?source-container-desig)
    (desig:current-designator ?target-container-designator ?target-container-desig)
    (spec:property ?source-container-desig (:type ?source-container-type))
    (spec:property ?target-container-desig (:type ?target-container-type))
    (spec:property ?source-container-desig (:name ?source-container-name))
    (spec:property ?target-container-desig (:name ?target-container-name))
    (lisp-fun obj-int:get-container-pouring-effort ?source-container-type ?target-container-type
              ?pouring-effort)
    (lisp-fun obj-int:get-container-pouring-poses ?source-container-type ?target-container-type
              ?pouring-poses))