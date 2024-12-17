class Infinity:
    def __init__(self, positive):
        self.sgn = positive

    def __gt__(self, other):
        return self.sgn

    def __ge__(self, other):
        return self.sgn or (isinstance(other, Infinity) and (not other.sgn))

    def __lt__(self, other):
        return not self.sgn

    def __le__(self, other):
        return (not self.sgn) or (isinstance(other, Infinity) and other.sgn)


class Board:
    squares = (((0, 0), (0, 1), (1, 0), (1, 1), (0, 2), (2, 0)),
               ((0, 7), (0, 6), (1, 7), (1, 6), (0, 5), (2, 7)),
               ((7, 0), (6, 0), (7, 1), (6, 1), (5, 0), (7, 2)),
               ((7, 7), (6, 7), (7, 6), (6, 6), (5, 7), (7, 5)))
    corners = ((0, 0), (0, 7), (7, 0), (7, 7))

    def __init__(self, parent=None, our=None, their=None, player=True):
        if our is None:
            our = {(3, 3): [(4, 2), (3, 2), (2, 2), (2, 3), (2, 4)],
                   (4, 4): [(3, 5), (4, 5), (5, 5), (5, 4), (5, 3)]}
        if their is None:
            their = {(3, 4): [(2, 3), (2, 4), (2, 5), (3, 5), (4, 5)],
                     (4, 3): [(3, 2), (4, 2), (5, 2), (5, 3), (5, 4)]}
        self.parent = parent
        self.our = our
        self.their = their
        self.player = player
        self.children = dict()
        self.directions = [(-1, -1), (-1, 0), (-1, 1),
                           (0, -1),            (0, 1),
                           (1, -1),  (1, 0),   (1, 1)]

    def peek(self, forced=False):
        for y, x in set([c for outer in self.their.values() for c in outer]):
            lines = (((y,) * x, range(x)),
                     ((y,) * (7 - x), range(7, x, -1)),
                     (range(y), (x,) * y),
                     (range(7, y, -1), (x,) * (7 - y)),
                     (range(max(y - x, 0), y), range(max(x - y, 0), x)),
                     (range(min(y - x, 0) + 7, y, -1), range(min(x - y, 0) + 7, x, -1)),
                     (range(max(x + y - 7, 0), y), range(min(x + y, 7), x, -1)),
                     (range(min(x + y, 7), y, -1), range(max(x + y - 7, 0), x)))

            child_line = []
            for line in lines:
                line = list(zip(*line))
                blank, player, their = -1, -1, -1
                for i, yx in enumerate(line):
                    if yx in self.our:
                        player = i
                    elif yx in self.their:
                        their = i
                    else:
                        blank = i
                if their > player > blank:
                    child_line.append(line[player + 1:])
            if child_line:
                self.children[(y, x)] = child_line

        if not self.children:
            if forced:
                return True
            self.our, self.their = self.their, self.our
            self.player = not self.player
            return self.peek(True)
        else:
            return False

    def move(self, coords):
        p1 = {key: value.copy() for key, value in self.our.items()}
        p2 = {key: value.copy() for key, value in self.their.items()}
        p1[coords] = []

        for line in self.children[coords]:
            for yx in line:
                p1[yx] = p2.pop(yx)

        for direction in self.directions:
            y, x = direction[0] + coords[0], direction[1] + coords[1]
            if (y, x) in p1:
                p1[(y, x)].remove(coords)
            elif (y, x) in p2:
                p2[(y, x)].remove(coords)
            elif 0 <= x < 8 and 0 <= y < 8:
                p1[coords].append((y, x))

        return Board(self, p2, p1, not self.player)

    def long_evaluate(self):
        pts = 1.
        for c, o1, o2, x, p1, p2 in Board.squares:
            if c in self.our:
                pts += 5
                if o1 in self.our:
                    pts += 2
                if o2 in self.our:
                    pts += 2
                if x in self.our:
                    pts += 1
            else:
                if x in self.our:
                    pts -= 4
                    if o1 in self.our:
                        pts -= 2
                    if o2 in self.our:
                        pts -= 2
                elif (o1 in self.our and ((o1[0] == 0 and any(yx in self.their for yx in zip((0,) * 6, range(1, 7)))) or
                                          (o1[0] == 7 and any(yx in self.their for yx in zip((7,) * 6, range(1, 7)))) or
                                          (o1[1] == 0 and any(yx in self.their for yx in zip(range(1, 7), (0,) * 6))) or
                                          (o1[1] == 7 and any(yx in self.their for yx in zip(range(1, 7), (7,) * 6)))) or
                      o2 in self.our and ((o2[0] == 0 and any(yx in self.their for yx in zip((0,) * 6, range(1, 7)))) or
                                          (o2[0] == 7 and any(yx in self.their for yx in zip((7,) * 6, range(1, 7)))) or
                                          (o2[1] == 0 and any(yx in self.their for yx in zip(range(1, 7), (0,) * 6))) or
                                          (o2[1] == 7 and any(yx in self.their for yx in zip(range(1, 7), (7,) * 6))))):
                    pts -= 6
                else:
                    if p1 in self.our:
                        pts += 0.5
                    if p2 in self.our:
                        pts += 0.5
        return pts * (len(self.children) ** 0.5)

    def evaluate(self):
        pts = 1
        for corner in Board.corners:
            if corner in self.our:
                pts += 1
        return pts * len(self.children)

    def search(self, max_depth=5, maximising=True, depth=0):
        self.peek()
        if depth == max_depth - 1:
            children = []
            if len(self.our) + len(self.their) < 52:
                evaluation = self.evaluate()
                for move in self.children:
                    child = self.move(move)
                    child.peek()
                    negamax = evaluation, child.evaluate()
                    children.append(negamax)
            elif len(self.our) + len(self.their) < 63:
                for move in self.children:
                    leaf = self.move(move)
                    children.append(len(leaf.their) - len(leaf.our))
            else:
                for move in self.children:
                    leaf = self.move(move)
                    our, their = len(leaf.our), len(leaf.their)
                    if our > their:
                        children.append(Infinity(True))
                    elif our == their:
                        children.append(0)
                    else:
                        children.append(Infinity(False))
        else:
            if depth:
                children = [self.move(move).search(max_depth, not maximising, depth + 1) for move in self.children]
            else:
                children = {}
                for move in self.children:
                    board = self.move(move)
                    children[board] = board.search(max_depth, not maximising, depth + 1)

        if depth:
            if maximising:
                if children:
                    return max(children)
                else:
                    return Infinity(False)
            else:
                if children:
                    return min(children)
                else:
                    return Infinity(True)
        else:
            if maximising:
                return max(children.items(), key=lambda x: x[1])[0]
            else:
                return min(children.items(), key=lambda x: x[1])[0]
