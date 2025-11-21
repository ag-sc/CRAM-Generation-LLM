(<- (desig:action-grounding ?action-designator (pour ?source-container ?target-container))
    (spec:property ?action-designator (:type :pouring))
    (spec:property ?action-designator (:source ?source-container))
    (spec:property ?action-designator (:target ?target-container))
    (lisp-fun obj-int:get-container-transform ?source-container ?source-transform)
    (lisp-fun obj-int:get-container-transform ?target-container ?target-transform)
    (lisp-fun obj-int:get-container-volume ?source-container ?source-volume)
    (lisp-fun obj-int:get-container-volume ?target-container ?target-volume)
    (lisp-fun obj-int:get-container-content ?source-container ?source-content)
    (lisp-fun obj-int:get-container-content ?target-container ?target-content)
    (lisp-fun obj-int:get-container-pouring-poses ?source-container ?source-transform
              ?target-container ?target-transform ?pouring-poses)
    (lisp-fun extract-pouring-manipulation-poses ?pouring-poses
              ?source-volume ?target-volume ?source-content ?target-content
              (?left-reach-poses ?right-reach-poses
                                 ?left-pour-poses ?right-pour-poses)))