(<- (desig:action-grounding ?action-designator (halve ?current-object-desig ?cutting-plane ?effort))
    (spec:property ?action-designator (:type :cutting))
    (spec:property ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-desig)
    (spec:property ?current-object-desig (:type ?object-type))
    (spec:property ?current-object-desig (:name ?object-name))
    (lisp-fun obj-int:is-food-object ?object-type)
    (lisp-fun obj-int:get-object-transform ?current-object-desig ?object-transform)
    (lisp-fun obj-int:get-object-bounding-box ?object-transform ?object-bbox)
    (lisp-fun obj-int:calculate-cutting-plane ?object-bbox ?cutting-plane)
    (lisp-fun obj-int:get-object-cutting-effort ?object-type ?effort)
    (lisp-fun extract-cutting-manipulation-poses ?cutting-plane ?object-transform ?effort
              (?left-reach-poses ?right-reach-poses
                                 ?left-grasp-poses ?right-grasp-poses
                                 ?left-cut-poses ?right-cut-poses)))