(<- (desig:action-grounding ?action-designator (pp-plans:pour ?resolved-action-designator))
      (spec:property ?action-designator (:type :pouring))
      (spec:property ?action-designator (:source ?source-designator))
      (spec:property ?action-designator (:target ?target-designator))
      (desig:current-designator ?source-designator ?current-source-desig)
      (desig:current-designator ?target-designator ?current-target-desig)
      (spec:property ?current-source-desig (:type ?source-type))
      (spec:property ?current-source-desig (:name ?source-name))
      (spec:property ?current-target-desig (:type ?target-type))
      (spec:property ?current-target-desig (:name ?target-name))
      (lisp-fun man-int:get-object-transform ?current-source-desig ?source-transform)
      (lisp-fun man-int:get-object-transform ?current-target-desig ?target-transform)
      (lisp-fun man-int:calculate-object-faces ?source-transform (?source-top-face ?source-bottom-face))
      (lisp-fun man-int:calculate-object-faces ?target-transform (?target-top-face ?target-bottom-face))
      (-> (equal ?source-type ?target-type)
          (equal ?source-type :container))
      (-> (equal ?source-top-face ?target-top-face)
          (equal ?source-bottom-face ?target-bottom-face))
      (-> (spec:property ?action-designator (:arm ?arm))
          (true)
          (man-int:robot-free-hand ?_ ?arm))
      (-> (spec:property ?action-designator (:pour-direction ?pour-direction))
          (member ?pour-direction '(:into :out-of)))
      (lisp-fun man-int:get-action-pour-trajectory ?source-type ?pour-direction ?arm ?source-transform ?target-transform ?trajectory)
      (lisp-fun man-int:get-traj-poses-by-label ?trajectory :reaching ?reach-poses)
      (lisp-fun man-int:get-traj-poses-by-label ?trajectory :pouring ?pour-poses)
      (equal ?objects (?current-source-desig ?current-target-desig))
      (desig:designator :action ((:type :pouring)
                                 (:source ?current-source-desig)
                                 (:source-name ?source-name)
                                 (:target ?current-target-desig)
                                 (:target-name ?target-name)
                                 (:arm ?arm)
                                 (:pour-direction ?pour-direction)
                                 (:reach-poses ?reach-poses)
                                 (:pour-poses ?pour-poses))
                        ?resolved-action-designator))