(<- (desig:action-grounding ?action-designator (pp-plans:place-down ?resolved-action-designator))
      (spec:property ?action-designator (:type :placing-down))
      (spec:property ?action-designator (:object ?object-designator))
      (desig:current-designator ?object-designator ?current-object-desig)
      (spec:property ?current-object-desig (:type ?object-type))
      (spec:property ?current-object-desig (:name ?object-name))
      (spec:property ?action-designator (:location ?location-designator))
      (desig:current-designator ?location-designator ?current-location-desig)
      (spec:property ?current-location-desig (:type :location))
      (spec:property ?current-location-desig (:name ?location-name))
      (lisp-fun man-int:get-object-transform ?current-object-desig ?object-transform)
      (lisp-fun man-int:get-location-transform ?current-location-desig ?location-transform)
      (lisp-fun man-int:calculate-object-faces ?object-transform (?facing-robot-face ?bottom-face))
      (-> (spec:property ?action-designator (:arm ?arm))
          (true)
          (man-int:robot-holding-object ?_ ?arm ?current-object-desig))
      (-> (lisp-fun man-int:get-action-trajectory :placing-down ?arm ?gripper-opening
                                                 ?object-transform ?location-transform
                                                 ?objects ?trajectory)
          (true)
          (lisp-fun man-int:get-traj-poses-by-label ?trajectory :reaching ?reach-poses)
          (lisp-fun man-int:get-traj-poses-by-label ?trajectory :placing-down ?place-poses))
      (lisp-fun man-int:get-action-gripping-effort ?object-type ?effort)
      (equal ?objects (?current-object-desig))
      (desig:designator :action ((:type :placing-down)
                                 (:object ?current-object-desig)
                                 (:object-name ?object-name)
                                 (:location ?current-location-desig)
                                 (:location-name ?location-name)
                                 (:arm ?arm)
                                 (:gripper-opening ?gripper-opening)
                                 (:effort ?effort)
                                 (:reach-poses ?reach-poses)
                                 (:place-poses ?place-poses))
                        ?resolved-action-designator))