(<- (desig:action-grounding ?action-designator (close ?container-designator))
    (spec:property ?action-designator (:type :closing))
    (spec:property ?action-designator (:object ?container-designator))
    (spec:property ?container-designator (:type :container))
    (spec:property ?container-designator (:name ?container-name))
    (lisp-fun obj-int:get-container-closing-poses ?container-name ?container-designator
              ?closing-poses)
    (desig:designator :location ((:pose ?closing-poses)) ?closing-designator))