(<- (desig:action-grounding ?action-designator (pour ?source-container ?target-container))
    (spec:property ?action-designator (:type :pouring))
    (spec:property ?action-designator (:source ?source-container))
    (spec:property ?action-designator (:target ?target-container))
    (desig:current-designator ?source-container ?current-source-container)
    (spec:property ?current-source-container (:type ?source-type))
    (spec:property ?current-source-container (:name ?source-name))
    (desig:current-designator ?target-container ?current-target-container)
    (spec:property ?current-target-container (:type ?target-type))
    (spec:property ?current-target-container (:name ?target-name))
    (lisp-fun obj-int:get-container-transform ?current-source-container ?source-transform)
    (lisp-fun obj-int:get-container-transform ?current-target-container ?target-transform)
    (lisp-fun obj-int:get-container-pouring-poses ?source-type ?target-type
              ?source-transform ?target-transform
              (?pouring-poses))
    (lisp-fun extract-pouring-manipulation-poses ?pouring-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-pour-poses ?right-pour-poses)))