class USnte:
    def __init__(self, tiBgn, tiEnd):
        self.bgn = tiBgn
        self.end = tiEnd
        self.lSub = []
    def __eq__(self, other):  # for operator==
        return self.bgn == other.bgn and self.end == other.end
    def __repr__(self):
        return f'U({self.bgn}, {self.end})'
    def getval(self):
        print(f'get {self}', end=',')
        return self

# def testSort():
li = [USnte(9,9.2), USnte(2,3), USnte(3,4), USnte(1,1.5), USnte(1,2), USnte(6,7)]
out = str(sorted(li, key=lambda m: (m.bgn, m.end)))
assert out == "[U(1, 1.5), U(1, 2), U(2, 3), U(3, 4), U(6, 7), U(9, 9.2)]"

# search:
out = next((m for m in li if m.getval().bgn == 2), None)
print(f"\nBgn_Result: {out}")

out = li.index(USnte(1, 1.5))
print(f"index A={out}")

