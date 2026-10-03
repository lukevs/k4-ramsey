import Std

/-!
Independent exact-Nat ordered-class recount for equal-mass rational graphons.

This version accepts up to 384 classes.  It keeps every ordered quadruple,
including repeated class indices, and normalizes by `n^4 * q^6`.  `Nat`
arithmetic is unbounded; the input limits are resource limits only.
-/

def orderedColor (n : Nat) (p : Array (Array Nat)) : Nat := Id.run do
  let mut total : Nat := 0
  for i in [:n] do
    for j in [:n] do
      let edge := p[i]![j]!
      if edge != 0 then
        let mut common := Array.replicate n 0
        let mut active : Array Nat := #[]
        for k in [:n] do
          let value := p[i]![k]! * p[j]![k]!
          if value != 0 then
            common := common.set! k value
            active := active.push k
        let mut subtotal : Nat := 0
        for k in active do
          let a := common[k]!
          for l in active do
            subtotal := subtotal + a * common[l]! * p[k]![l]!
        total := total + edge * subtotal
  return total

def numbers (line : String) : IO (Array Nat) := do
  let mut values := #[]
  for word in (line.splitOn " ").filter (· != "") do
    let some value := word.toNat?
      | throw (IO.userError "non-natural matrix entry")
    values := values.push value
  return values

def main (args : List String) : IO Unit := do
  let some path := args[0]?
    | throw (IO.userError "usage: latent_graphon_nat_audit matrix.txt")
  let raw ← IO.FS.readFile (System.FilePath.mk path)
  let lines := ((raw.splitOn "\n").filter (· != "")).toArray
  unless lines.size > 0 do throw (IO.userError "empty input")
  let header ← numbers lines[0]!
  unless header.size = 2 do throw (IO.userError "invalid header")
  let n := header[0]!
  let q := header[1]!
  unless n > 0 && n ≤ 384 && q > 0 && q ≤ 65536 && lines.size = n + 1 do
    throw (IO.userError "invalid order/denominator/row count")
  let mut red : Array (Array Nat) := #[]
  for i in [:n] do
    let row ← numbers lines[i + 1]!
    unless row.size = n && row.all (· ≤ q) do
      throw (IO.userError "invalid probability row")
    red := red.push row
  for i in [:n] do
    for j in [:n] do
      unless red[i]![j]! = red[j]![i]! do
        throw (IO.userError "asymmetric probability matrix")
  let blue := red.map (fun row => row.map (fun value => q - value))
  let redTotal := orderedColor n red
  let blueTotal := orderedColor n blue
  let denominator := n ^ 4 * q ^ 6
  IO.println s!"{redTotal} {blueTotal} {redTotal + blueTotal} {denominator}"
