(<- (desig:action-grounding ?action-designator (pp-plans:slice ?resolved-action-designator))
      (spec:property ?action-designator (:type :cutting))
      (spec:property ?action-designator (:object ?object-designator))
      (desig:current-designator ?object-designator ?current-object-desig)
      (spec:property ?current-object-desig (:type ?object-type))
      (spec:property ?current-object-desig (:name ?object-name))
      (lisp-fun man-int:get-object-transform ?current-object-desig ?object-transform)
      (lisp-fun man-int:calculate-object-faces ?object-transform (?facing-robot-face ?bottom-face))
      (lisp-fun man-int:get-action-cutting-planes ?object-type ?cutting-planes)
      (equal ?objects (?current-object-desig))
      (-> (equal ?arm :left)
          (and (lisp-fun man-int:get-action-trajectory :slicing ?arm ?cutting-planes ?objects
                         ?left-trajectory)
               (lisp-fun man-int:get-traj-poses-by-label ?left-trajectory :reaching
                         ?left-reach-poses)
               (lisp-fun man-int:get-traj-poses-by-label ?left-trajectory :cutting
                         ?left-cutting-poses))
          (and (equal ?left-reach-poses NIL)
               (equal ?left-cutting-poses NIL)))
      (-> (equal ?arm :right)
          (and (lisp-fun man-int:get-action-trajectory :slicing ?arm ?cutting-planes ?objects
                         ?right-trajectory)
               (lisp-fun man-int:get-traj-poses-by-label ?right-trajectory :reaching
                         ?right-reach-poses)
               (lisp-fun man-int:get-traj-poses-by-label ?right-trajectory :cutting
                         ?right-cutting-poses))
          (and (equal ?right-reach-poses NIL)
               (equal ?right-cutting-poses NIL)))
      (desig:designator :action ((:type :slicing)
                                 (:object ?current-object-desig)
                                 (:object-name  ?object-name)
                                 (:arm ?arm)
                                 (:cutting-planes ?cutting-planes)
                                 (:left-reach-poses ?left-reach-poses)
                                 (:right-reach-poses ?right-reach-poses)
                                 (:left-cutting-poses ?left-cutting-poses)
                                 (:right-cutting-poses ?right-cutting-poses)
                                 (:small-slice ?small-slice)
                                 (:big-slice ?big-slice)
                                 (:cut :cutting))
                        ?resolved-action-designator)))