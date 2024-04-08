(<- (desig:action-grounding ?action-designator (halve ?current-object-desig ?knife
                                                      ?cutting-plane ?effort ?cutting-force
                                                      ?left-reach-poses ?right-reach-poses
                                                      ?left-cut-poses ?right-cut-poses
                                                      ?left-lift-poses ?right-lift-poses))
    (spec:property ?action-designator (:type :halving))
    (spec:property ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-desig)
    (spec:property ?current-object-desig (:type ?object-type))
    (spec:property ?current-object-desig (:name ?object-name))
    (-> (spec:property ?action-designator (:knife ?knife))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?knife)))
    (lisp-fun obj-int:get-object-transform ?current-object-desig ?object-transform)
    (lisp-fun obj-int:calculate-object-faces ?object-transform (?facing-robot-face ?bottom-face))
    (-> (spec:property ?action-designator (:cutting-plane ?cutting-plane))
        (true)
        (and (lisp-fun obj-int:get-object-type-cutting-planes
                       ?object-type ?facing-robot-face ?bottom-face ?cutting-planes)
             (member ?cutting-plane ?cutting-planes)))
    (lisp-fun obj-int:get-object-type-cutting-effort ?object-type ?effort)
    (lisp-fun obj-int:get-object-type-cutting-force ?object-type ?cutting-force)
    (lisp-fun obj-int:get-object-cutting-poses
              ?object-name ?object-type :left ?cutting-plane ?object-transform
              ?left-poses)
    (lisp-fun obj-int:get-object-cutting-poses
              ?object-name ?object-type :right ?cutting-plane ?object-transform
              ?right-poses)
    (lisp-fun extract-halve-manipulation-poses ?knife ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-cut-poses ?right-cut-poses
                                 ?left-lift-poses ?right-lift-poses)))