(<- (desig:action-grounding ?action-designator (slice ?current-object-designator ?knife-designator
                                                       ?left-reach-poses ?right-reach-poses
                                                       ?left-slice-poses ?right-slice-poses
                                                       ?left-retract-poses ?right-retract-poses
                                                       ?small-slice-designator ?big-slice-designator))
    (spec:property ?action-designator (:type :slicing))
    (-> (spec:property ?action-designator (:object ?current-object-designator))
        (cpoe:object-in-hand ?current-object-designator ?knife-designator))
    (-> (spec:property ?action-designator (:object ?small-slice-designator))
        (desig:designator :object ((:type :food) (:name (format nil "small-~a" ?object-name))))
        (spec:property ?small-slice-designator (:type :food))
        (spec:property ?small-slice-designator (:name (format nil "small-~a" ?object-name))))
    (-> (spec:property ?action-designator (:object ?big-slice-designator))
        (desig:designator :object ((:type :food) (:name (format nil "big-~a" ?object-name))))
        (spec:property ?big-slice-designator (:type :food))
        (spec:property ?big-slice-designator (:name (format nil "big-~a" ?object-name))))
    (once (or (cpoe:object-in-hand ?current-object-designator ?knife-designator)
              (spec:property ?action-designator (:object ?current-object-designator))))
    (desig:current-designator ?current-object-designator ?current-object-designator)
    (spec:property ?current-object-designator (:type ?object-type))
    (spec:property ?current-object-designator (:name ?object-name))
    (lisp-fun obj-int:get-object-grasping-poses
              ?knife-designator ?knife-type :left ?knife-grasp ?knife-transform
              ?left-poses)
    (lisp-fun obj-int:get-object-grasping-poses
              ?knife-designator ?knife-type :right ?knife-grasp ?knife-transform
              ?right-poses)
    (lisp-fun extract-slicing-poses ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses ?left-slice-poses ?right-slice-poses
                                 ?left-retract-poses ?right-retract-poses))))