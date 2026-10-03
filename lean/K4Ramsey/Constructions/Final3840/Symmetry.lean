import K4Ramsey.Constructions.Final3840.Model

namespace K4Ramsey.Final3840

def shift (i j : Coarse) : Coarse :=
  ⟨((((i.val / 64 + j.val / 64) % 3) * 64) + ((i.val % 64) ^^^ (j.val % 64))) % 192,
    Nat.mod_lt _ (by decide)⟩

end K4Ramsey.Final3840
