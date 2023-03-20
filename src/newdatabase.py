from src.primitives import Point, Segment, Angle, LineKey, CongKey, Ratio, Triangle, Circle
from src.fact import Fact
from src.predicate import Predicate

import itertools


class Database:

    def __init__(self,
                 lines: dict[LineKey, set[Point]] = None,
                 congs: dict[CongKey, set[Segment]] = None,
                 circles: list[Circle] = None,
                 midpFacts: list[list[Point]] = None,
                 paraFacts: list[set[LineKey]] = None,
                 perpFacts: list[set[LineKey]] = None,
                 eqangleFacts: list[set[Angle]] = None,
                 eqratioFacts: list[set[Ratio]] = None,
                 simtriFacts: list[set[Triangle]] = None,
                 contriFacts: list[set[Triangle]] = None) -> None:
        self.lines = lines or {}
        self.congs = congs or {}
        self.circles = circles or []
        self.midpFacts = midpFacts or []
        self.paraFacts = paraFacts or []
        self.perpFacts = perpFacts or []
        self.eqangleFacts = eqangleFacts or []
        self.eqratioFacts = eqratioFacts or []
        self.simtriFacts = simtriFacts or []
        self.contriFacts = contriFacts or []

    def _predicate_all_forms(self, fact: Fact) -> list[Predicate]:
        if fact.type == "coll":
            return [Predicate("coll", fact.objects)]
        if fact.type == "para":
            lk1, lk2 = fact.objects
            predicates = []
            for (A, B) in itertools.combinations(self.lines[lk1]):
                for (C, D) in itertools.combinations(self.lines[lk2]):
                    predicates.append(Predicate("para", [A, B, C, D]))
            return predicates
        if fact.type == "perp":
            lk1, lk2 = fact.objects
            predicates = []
            for (A, B) in itertools.combinations(self.lines[lk1]):
                for (C, D) in itertools.combinations(self.lines[lk2]):
                    predicates.append(Predicate("perp", [A, B, C, D]))
            return predicates
        if fact.type == "midp":
            M, A, B = fact.objects
            return [Predicate("midp", [M, A, B]), Predicate("midp", [M, B, A])]
        if fact.type == "cong":
            s1, s2 = fact.objects
            A, B, C, D = s1.p1, s1.p2, s2.p1, s2.p2
            return [
                Predicate("cong", [A, B, C, D]),
                Predicate("cong", [A, B, D, C]),
                Predicate("cong", [B, A, C, D]),
                Predicate("cong", [B, A, D, C]),
            ]
        if fact.type == "eqangle":
            lk1, lk2, lk3, lk4 = fact.objects
            angle_pairs = [
                [Angle(lk1, lk2), Angle(lk3, lk4)],
                [Angle(lk2, lk1), Angle(lk4, lk3)],
                [Angle(lk1, lk3), Angle(lk2, lk4)],
                [Angle(lk3, lk1), Angle(lk4, lk2)],
            ]
            predicates = []
            for (a1, a2) in angle_pairs:
                l1, l2 = self.lines[a1.lk1], self.lines[a1.lk2]
                l3, l4 = self.lines[a2.lk1], self.lines[a2.lk2]

                for (A, B) in itertools.combinations(l1, 2):
                    for (C, D) in itertools.combinations(l2, 2):
                        for (P, Q) in itertools.combinations(l3, 2):
                            for (U, V) in itertools.combinations(l4, 2):
                                predicates.append(
                                    Predicate("eqangle",
                                              [A, B, C, D, P, Q, U, V]))
            return predicates

        if fact.type == "eqratio":
            ck1, ck2, ck3, ck4 = fact.objects
            ratio_pairs = [
                [Ratio(ck1, ck2), Ratio(ck3, ck4)],
                [Ratio(ck2, ck1), Ratio(ck4, ck3)],
                [Ratio(ck1, ck3), Ratio(ck2, ck4)],
                [Ratio(ck3, ck1), Ratio(ck4, ck2)],
            ]
            predicates = []
            for (r1, r2) in ratio_pairs:
                s1, s2 = self.congs[r1.c1], self.congs[r1.c2]
                s3, s4 = self.congs[r2.c1], self.congs[r2.c2]
                for (A, B) in s1:
                    for (C, D) in s2:
                        for (P, Q) in s3:
                            for (U, V) in s4:
                                predicates.append(
                                    Predicate("eqratio",
                                              [A, B, C, D, P, Q, U, V]))
            return predicates

    def _predicate_to_fact(self, predicate: Predicate) -> Fact:
        if predicate.type == "coll":
            return Fact("coll", predicate.points)
        if predicate.type == "midp":
            M, A, B = predicate.points
            A, B = sorted([A, B])
            return Fact("midp", [M, A, B])
        if predicate.type == "para":
            A, B, C, D = predicate.points
            lAB = self.matchLine([A, B])
            lCD = self.matchLine([C, D])
            return Fact("para", [lAB, lCD])
        if predicate.type == "perp":
            A, B, C, D = predicate.points
            lAB = self.matchLine([A, B])
            lCD = self.matchLine([C, D])
            return Fact("perp", [lAB, lCD])
        if predicate.type == "eqangle":
            A, B, C, D, P, Q, U, V = predicate.points
            lAB = self.matchLine([A, B])
            lCD = self.matchLine([C, D])
            lPQ = self.matchLine([P, Q])
            lUV = self.matchLine([U, V])
            return Fact("eqangle", [lAB, lCD, lPQ, lUV])
        if predicate.type == "eqratio":
            A, B, C, D, P, Q, U, V = predicate.points
            cAB = self.matchCong([A, B])
            cCD = self.matchCong([C, D])
            cPQ = self.matchCong([P, Q])
            cUV = self.matchCong([U, V])
            return Fact("eqratio", [cAB, cCD, cPQ, cUV])
        if predicate.type == "cyclic":
            return Fact("cyclic", predicate.points)
        if predicate.type == "cong":
            A, B, C, D = predicate.points
            return Fact("cong", [Segment(A, B), Segment(C, D)])
        if predicate.type == "simtri":
            A, B, C, P, Q, R = predicate.points
            return Fact("simtri", [Triangle(A, B, C), Triangle(P, Q, R)])
        if predicate.type == "contri":
            A, B, C, P, Q, R = predicate.points
            return Fact("contri", [Triangle(A, B, C), Triangle(P, Q, R)])

        raise ValueError(f"{predicate} not applicable")

    def addPredicate(self, predicate: Predicate) -> None:
        """Add predicate into database
        Should only be used in the initialization phase
        """
        self.addFact(self._predicate_to_fact(predicate=predicate))

    def addFact(self, fact: Fact) -> None:
        """
        - Fact(coll, [P1, P2, P3])
        - Fact(para, [LK1, LK2])
        - Fact(perp, [LK1, LK2])
        - Fact(eqangle, [LK1, LK2, LK3, LK4])
        - Fact(eqratio, [CK1, CK2, CK3, CK4])
        - Fact(cyclic, [P1, P2, P3, P4])
        - Fact(cong, [S1, S2])
        - Fact(simtri, [T1, T2])
        - Fact(contri, [T1, T2])

        The process of adding facts
            1. check if it is already in, i.e., if there is
            new lines/para line pairs... found
            2. if nothing new, do nothing
            3. else, add to the fact

        """
        if self.containsFact(fact):
            return None

        if fact.type == "coll":
            self.collHandler(fact)
        elif fact.type == "midp":
            self.midpHandler(fact)
        elif fact.type == "para":
            self.paraHandler(fact)
        elif fact.type == "perp":
            self.perpHandler(fact)
        elif fact.type == "eqangle":
            self.eqangleHandler(fact)
        elif fact.type == "eqratio":
            self.eqratioHandler(fact)
        elif fact.type == "cyclic":
            self.cyclicHandler(fact)
        elif fact.type == "circle":
            self.circleHandler(fact)
        elif fact.type == "cong":
            self.congHandler(fact)
        elif fact.type == "simtri":
            self.simtriHandler(fact)
        elif fact.type == "contri":
            self.contriHandler(fact)

    def circleHandler(self, fact: Fact):
        """Add Fact(circle, [O, A, B, C])
        """
        center, points = fact.objects[0], fact.objects[1:]
        found = False
        i = 0
        while i < len(self.circles) and not found:
            circle = self.circles[i]
            if circle.center != center:
                continue
            inCount = sum(p in circle.points for p in points)
            if inCount >= 1:
                found = True
                self.circles[i] = Circle(center,
                                         circle.points.union(set(points)))

        if not found:
            self.circles.append(Circle(center, set(points)))

    def cyclicHandler(self, fact: Fact):
        """Add Fact(cyclic, [P1, P2, P3, P4])
        """

        def overlaps(set1: set, set2: set) -> bool:
            return len(set1.intersection(set2)) >= 3

        overlapsMap = [
            i for i in range(len(self.circles))
            if overlaps(self.circles[i].points, fact.objects)
        ]

        if len(overlapsMap) == 0:
            self.circles.append(Circle(self.newCenterName, set(fact.objects)))

        elif len(overlapsMap) == 1:
            pos = overlapsMap[0]
            circle = self.circles[pos]
            self.circles[pos] = Circle(circle.center,
                                       circle.points.union(set(fact.objects)))
        elif len(overlapsMap) >= 2:
            keep = overlapsMap[0]
            drops = overlapsMap[1:]
            circlePoints = set(fact.objects)
            for drop in drops:
                circlePoints = circlePoints.union(self.circles[drop].points)

            circleKeep = self.circles[keep]
            self.circles[keep] = Circle(circleKeep.center,
                                        circleKeep.points.union(circlePoints))
            for drop in drops:
                del self.circles[drop]

    def eqangleHandler(self, fact: Fact):
        """Add Fact(eqangle, [LK1, LK2, LK3, LK4])
        """
        lk1, lk2, lk3, lk4 = fact.objects
        found = False
        i = 0
        while i < len(self.eqangleFacts) and not found:
            factsi = self.eqangleFacts[i]
            angle_pairs = [
                [Angle(lk1, lk2), Angle(lk3, lk4)],
                [Angle(lk2, lk1), Angle(lk4, lk3)],
                [Angle(lk1, lk3), Angle(lk2, lk4)],
                [Angle(lk3, lk1), Angle(lk4, lk2)],
            ]
            for (a1, a2) in angle_pairs:
                if a1 in factsi or a2 in factsi:
                    self.eqangleFacts[i] = factsi.union({a1, a2})
                    found = True
                    break

        if not found:
            self.eqangleFacts.append({Angle(lk1, lk2), Angle(lk3, lk4)})

    def eqratioHandler(self, fact: Fact):
        """Add Fact(eqratio, [CK1, CK2, CK3, CK4])
        """
        ck1, ck2, ck3, ck4 = fact.objects
        found = False
        i = 0
        while i < len(self.eqratioFacts) and not found:
            factsi = self.eqratioFacts[i]
            ratio_pairs = [
                [Ratio(ck1, ck2), Ratio(ck3, ck4)],
                [Ratio(ck2, ck1), Ratio(ck4, ck3)],
                [Ratio(ck1, ck3), Ratio(ck2, ck4)],
                [Ratio(ck3, ck1), Ratio(ck4, ck2)],
            ]
            for (r1, r2) in ratio_pairs:
                if r1 in factsi or r2 in factsi:
                    self.eqratioFacts[i] = factsi.union({r1, r2})
                    found = True
                    break

        if not found:
            self.eqratioFacts.append({Ratio(ck1, ck2), Ratio(ck3, ck4)})

    def simtriHandler(self, fact: Fact):
        """Add Fact(simtri, [T1, T2])

        Be aware that the order of triangle vertices matters.
        """
        t1, t2 = fact.objects
        overlapsMap = [
            i for i in range(len(self.simtriFacts))
            if t1 in self.simtriFacts[i] or t2 in self.simtriFacts[i]
        ]

        if len(overlapsMap) == 0:
            self.simtriFacts.append({t1, t2})
        elif len(overlapsMap) == 1:
            pos = overlapsMap[0]
            tris = self.simtriFacts[pos]
            t: Triangle = t1 if t1 in tris else t2
            tt: Triangle = [tri for tri in tris if tri == t]
            # get the order of vertices
            ords = [[t.p1, t.p2, t.p3].index(v) for v in [tt.p1, tt.p2, tt.p3]]
            v1s = [t1.p1, t1.p2, t1.p3]
            v2s = [t2.p1, t2.p2, t2.p3]
            t1p = Triangle([v1s[o] for o in ords])
            t2p = Triangle([v2s[o] for o in ords])
            self.simtriFacts[pos] = tris.union({t1p, t2p})
        elif len(overlapsMap) == 2:
            keep, drop = overlapsMap
            tris = self.simtriFacts[keep]
            t: Triangle = t1 if t1 in tris else t2
            tt: Triangle = [tri for tri in tris if tri == t]
            # get the order of vertices
            ords = [[t.p1, t.p2, t.p3].index(v) for v in [tt.p1, tt.p2, tt.p3]]
            v1s = [t1.p1, t1.p2, t1.p3]
            v2s = [t2.p1, t2.p2, t2.p3]
            t1p = Triangle([v1s[o] for o in ords])
            t2p = Triangle([v2s[o] for o in ords])

            self.simtriFacts[keep] = self.simtriFacts[keep].union(
                self.simtriFacts[drop].union({t1p, t2p}))
            del self.simtriFacts[drop]

    def contriHandler(self, fact: Fact):
        """Add Fact(contri, [T1, T2])

        Be aware that the order of triangle vertices matters.
        """
        t1, t2 = fact.objects
        overlapsMap = [
            i for i in range(len(self.contriFacts))
            if t1 in self.contriFacts[i] or t2 in self.contriFacts[i]
        ]

        if len(overlapsMap) == 0:
            self.contriFacts.append({t1, t2})
        elif len(overlapsMap) == 1:
            pos = overlapsMap[0]
            tris = self.contriFacts[pos]
            t: Triangle = t1 if t1 in tris else t2
            tt: Triangle = [tri for tri in tris if tri == t]
            # get the order of vertices
            ords = [[t.p1, t.p2, t.p3].index(v) for v in [tt.p1, tt.p2, tt.p3]]
            v1s = [t1.p1, t1.p2, t1.p3]
            v2s = [t2.p1, t2.p2, t2.p3]
            t1p = Triangle([v1s[o] for o in ords])
            t2p = Triangle([v2s[o] for o in ords])
            self.contriFacts[pos] = tris.union({t1p, t2p})
        elif len(overlapsMap) == 2:
            keep, drop = overlapsMap
            tris = self.contriFacts[keep]
            t: Triangle = t1 if t1 in tris else t2
            tt: Triangle = [tri for tri in tris if tri == t]
            # get the order of vertices
            ords = [[t.p1, t.p2, t.p3].index(v) for v in [tt.p1, tt.p2, tt.p3]]
            v1s = [t1.p1, t1.p2, t1.p3]
            v2s = [t2.p1, t2.p2, t2.p3]
            t1p = Triangle([v1s[o] for o in ords])
            t2p = Triangle([v2s[o] for o in ords])

            self.contriFacts[keep] = self.contriFacts[keep].union(
                self.contriFacts[drop].union({t1p, t2p}))
            del self.contriFacts[drop]

    def collHandler(self, fact: Fact):
        """Add Fact(coll, [A, B, C])
        lines = {"line1": [A, B, C], "line2": [B, D, E], "line3": [F, G] }

        Case 1: coll(A, B, C)
        Case 2: coll(B, C, D)
        Case 3: coll(B, F, G)
        Case 4: coll(X, Y, Z)

        Additionally, we need to adjust the key changes in eqangleFacts
        """

        def overlaps(set1: set, set2: set) -> bool:
            return len(set1.intersection(set2)) >= 2

        overlapsMap = [
            lk for lk, points in self.lines.items()
            if overlaps(points, fact.objects)
        ]

        if len(overlapsMap) == 0:
            # case 4
            self.lines[self.newLineName] = set(fact.objects)
        elif len(overlapsMap) == 1:
            # case 1 and case 3
            self.lines[overlapsMap[0]] = self.lines[overlapsMap[0]].union(
                set(fact.objects))
        elif len(overlapsMap) == 2:
            # case 2
            keep, drop = overlapsMap
            self.lines[keep] = self.lines[keep].union(self.lines[drop].union(
                set(fact.objects)))
            del self.lines[drop]

            # key changes in eqangleFacts
            for angles in self.eqangleFacts:
                for angle in angles:
                    if angle.lk1 == drop:
                        angle.lk1 = keep
                    if angle.lk2 == drop:
                        angle.lk2 = keep

    def congHandler(self, fact: Fact):
        """Add Fact(cong, [s1, s2])
        congs = { "cong1": {s1, s2, s3}, "cong2": {s4, s5} }

        Case 1: cong(s1, s2)
        Case 2: cong(s1, s6)
        Case 3: cong(s1, s4)
        Case 4: cong(s7, s8)

        Additionally, we need to adjust the key changes in eqratioFacts
        """

        s1, s2 = fact.objects

        def overlaps(set1: set, set2: set) -> bool:
            return len(set1.intersection(set2)) > 0

        overlapsMap = [
            cKey for cKey, segments in self.congs.items()
            if overlaps(segments, {s1, s2})
        ]

        if len(overlapsMap) == 0:
            # case 4
            self.congs[self.newCongName] = {s1, s2}
        elif len(overlapsMap) == 1:
            # case 1 and case 3
            self.congs[overlapsMap[0]] = self.congs[overlapsMap[0]].union(
                {s1, s2})
        elif len(overlapsMap) == 2:
            # case 2
            keep, drop = overlapsMap
            self.congs[keep] = self.congs[keep].union(self.congs[drop])
            del self.congs[drop]

            # handle key changes in eqratioFacts
            for ratios in self.eqratioFacts:
                for ratio in ratios:
                    if ratio.c1 == drop:
                        ratio.c1 = keep
                    if ratio.c2 == drop:
                        ratio.c2 = keep

    def midpHandler(self, fact: Fact):
        """Add Fact(midp, [M,A,B])
        """
        M, A, B = fact.objects
        A, B = sorted([A, B])

        if [M, A, B] not in self.midpFacts:
            self.midpFacts.append([M, A, B])

    def paraHandler(self, fact: Fact):
        """Add Fact(para, [LK1, LK2])
        """
        lk1, lk2 = fact.objects
        found = False
        i = 0
        while i < len(self.paraFacts) and not found:
            if lk1 in self.paraFacts[i] or lk2 in self.paraFacts[i]:
                self.paraFacts[i] = self.paraFacts[i].union({lk1, lk2})
                found = True

        if not found:
            self.paraFacts.append({lk1, lk2})

    def perpHandler(self, fact: Fact):
        """Add Fact(perp, [LK1, LK2])
        """
        lk1, lk2 = fact.objects
        if {lk1, lk2} not in self.perpFacts:
            self.perpFacts.append({lk1, lk2})

    def containsFact(self, fact: Fact) -> bool:
        """
        Check if a fact is contained by the database
        """
        if fact.type == "coll":
            # Fact(coll, [p1,p2,..])
            for _, points in self.lines.items():
                if all(p in points for p in fact.objects):
                    return True
            return False

        if fact.type == "midp":
            # Fact(midp, [M,A,B])
            M, A, B = fact.objects
            A, B = sorted([A, B])
            return [M, A, B] in self.midpFacts

        if fact.type == "para":
            # Fact(para, [LK1, LK2])
            lk1, lk2 = fact.objects
            for parafact in self.paraFacts:
                if lk1 in parafact and lk2 in parafact:
                    return True
            return False

        if fact.type == "eqangle":
            # Fact(eqangle, [LK1, LK2, LK3 ,LK4])
            lk1, lk2, lk3, lk4 = fact.objects
            for angles in self.eqangleFacts:
                if Angle(lk1, lk2) in angles and Angle(lk3, lk4) in angles:
                    return True
                if Angle(lk2, lk1) in angles and Angle(lk4, lk3) in angles:
                    return True
                if Angle(lk1, lk3) in angles and Angle(lk2, lk4) in angles:
                    return True
                if Angle(lk3, lk1) in angles and Angle(lk4, lk2) in angles:
                    return True
            return False

        if fact.type == "cong":
            # Fact(cong, [S1, S2])
            s1, s2 = fact.objects
            for segments in self.congs.values():
                if s1 in segments and s2 in segments:
                    return True
            return False

        if fact.type == "eqratio":
            # Fact(eqratio, [CK1, CK2, CK3, CK4])
            ck1, ck2, ck3, ck4 = fact.objects
            for ratios in self.eqratioFacts:
                if Ratio(ck1, ck2) in ratios and Ratio(ck3, ck4) in ratios:
                    return True
                if Ratio(ck2, ck1) in ratios and Ratio(ck4, ck3) in ratios:
                    return True
                if Ratio(ck1, ck3) in ratios and Ratio(ck2, ck4) in ratios:
                    return True
                if Ratio(ck3, ck1) in ratios and Ratio(ck4, ck2) in ratios:
                    return True
            return False

        if fact.type == "perp":
            # Fact(perp, [lk1, lk2])
            lk1, lk2 = fact.objects
            return {lk1, lk2} in self.perpFacts

        if fact.type == "simtri":
            # Fact(simtri, [T1, T2])
            t1, t2 = fact.objects
            for tris in self.simtriFacts:
                if t1 in tris and t2 in tris:
                    return True
            return False

        if fact.type == "contri":
            # Fact(contri, [T1, T2])
            t1, t2 = fact.objects
            for tris in self.contriFacts:
                if t1 in tris and t2 in tris:
                    return True
            return False

        if fact.type == "circle":
            # Fact(circle, [O, P1, P2, ..])
            center, points = fact.objects[0], fact.objects[1:]
            for circle in self.circles:
                if center == circle.center and all(
                    [p in circle.points for p in points]):
                    return True

            return False

        if fact.type == "cyclic":
            # Fact(cyclic, [P1, P2, P3, P4])
            for circle in self.circles:
                if all([p in circle.points for p in fact.objects]):
                    return True
            return False

        raise ValueError("Invalid type of fact ", fact.type)

    @property
    def newLineName(self):
        for n in range(1, 50):
            if f'line{n}' not in self.lines:
                return f'line{n}'
        raise ValueError("Running out names for lines!")

    @property
    def newCongName(self):
        for n in range(1, 50):
            if f'cong{n}' not in self.congs:
                return f'cong{n}'
        raise ValueError("Running out names for congs!")

    @property
    def newCenterName(self):
        for n in range(1, 50):
            if f'O{n}' not in self.lines:
                return f'O{n}'
        raise ValueError("Running out names for centers!")

    def matchLine(self, points: list[Point]):
        """Search for the line, if found, return the name;
        else, create a new line connecting two points and
        return the new name
        """
        assert len(points) == 2
        for name, line in self.lines.items():
            if all(p in line for p in points):
                return name

        newName = self.newLineName
        self.lines[newName] = set(points)
        return newName

    def matchCong(self, points: list[Point]):
        """Search for the cong, if found, return the name;
        else, create a new Cong object with a segment of two points and
        return the new name
        """
        assert len(points) == 2
        for name, cong in self.congs.items():
            # cong is a list of segments
            for segment in cong:
                if str(segment) == "".join(sorted(points)):
                    return name

        newName = self.newCongName
        self.congs[newName] = {Segment(*points)}
        return newName

    def __repr__(self) -> str:
        s = "\nDatabase\n\n"

        # coll
        if self.lines:
            s += "> Coll Facts\n"
            for points in self.lines.values():
                if len(points) >= 3:
                    s += f"  coll({','.join(sorted(points))})\n"

        # para
        if self.paraFacts:
            s += "\n> Para Facts\n"
            for lines in self.paraFacts:
                s += f"  para( "
                for lineName in lines:
                    s += f"[{','.join(sorted(self.lines[lineName]))}] "
                s += f")\n"

        # perp
        if self.perpFacts:
            s += "\n> Perp Facts\n"
            for lines in self.perpFacts:
                s += f"  perp( "
                for lineName in lines:
                    s += f"[{','.join(sorted(self.lines[lineName]))}] "
                s += f")\n"

        # eqangle
        if self.eqangleFacts:
            s += "\n> Eqangle Facts\n"
            for angles in self.eqangleFacts:
                s += f"  eqangle( "
                angles_str = []
                for angle in angles:
                    angles_str.append(self.angle_to_str(angle))
                s += ", ".join(angles_str)
                s += " )\n"

        # cong
        if self.congs:
            s += "\n> Cong Facts\n"
            for segments in self.congs.values():
                if len(segments) > 1:
                    s += "  cong("
                    s += ", ".join([str(s) for s in segments])
                    s += ")\n"

        # eqratio
        if self.eqratioFacts:
            s += "\n> Eqratio Facts\n"
            for ratios in self.eqratioFacts:
                s += "  eqratio( "
                ratios_str = []
                for ratio in ratios:
                    ratios_str.append(self.ratio_to_str(ratio))
                s += ", ".join(ratios_str)
                s += " )\n"

        # simtri
        if self.simtriFacts:
            s += "\n> Simtri Facts\n"
            for tris in self.simtriFacts:
                s += "  simtri( "
                tris_str = ["".join([tri.p1, tri.p2, tri.p3]) for tri in tris]
                s += ", ".join(tris_str)
                s += ")\n"

        # contri
        if self.contriFacts:
            s += "\n> Contri Facts\n"
            for tris in self.contriFacts:
                s += "  contri( "
                tris_str = ["".join([tri.p1, tri.p2, tri.p3]) for tri in tris]
                s += ", ".join(tris_str)
                s += ")\n"

        # circle
        if self.circles:
            s += "\n> Circle Facts\n"
            for circle in self.circles:
                s += str(circle)
                s += "\n"

        s += "\n" + "#" * 40 + "\n\n"

        return s

    def angle_to_str(self, angle: Angle):
        l1, l2 = angle.lk1, angle.lk2
        p1str = ','.join(sorted(self.lines[l1]))
        p2str = ','.join(sorted(self.lines[l2]))
        return f"Angle([{p1str}],[{p2str}])"

    def ratio_to_str(self, ratio: Ratio):
        c1, c2 = ratio.c1, ratio.c2
        c1str = ",".join([str(s) for s in self.congs[c1]])
        c2str = ",".join([str(s) for s in self.congs[c2]])
        return f"Ratio([{c1str}],[{c2str}])"