import Std

/- Standalone ordered-index graphon recount. No imports from existing counters.
   UInt64 is used only after checking n^4*q^6 <= 2^64-1. -/
def orderedColor (n : Nat) (p : Array (Array UInt64)) : UInt64 := Id.run do
  let mut total : UInt64 := 0
  for i in [:n] do
    for j in [:n] do
      let edge := p[i]![j]!
      if edge != 0 then
        let mut common := Array.replicate n (0 : UInt64)
        for k in [:n] do
          common := common.set! k (p[i]![k]! * p[j]![k]!)
        let mut subtotal : UInt64 := 0
        for k in [:n] do
          let a := common[k]!
          if a != 0 then
            for l in [:n] do
              subtotal := subtotal + a * common[l]! * p[k]![l]!
        total := total + edge * subtotal
  return total

def numbers (line : String) : IO (Array Nat) := do
  let mut values := #[]
  for word in (line.splitOn " ").filter (· != "") do
    let some value := word.toNat? | throw (IO.userError "non-natural matrix entry")
    values := values.push value
  return values

def main (args : List String) : IO Unit := do
  let some path := args[0]? | throw (IO.userError "usage: graphon_audit matrix.txt")
  let raw ← IO.FS.readFile (System.FilePath.mk path)
  let lines := ((raw.splitOn "\n").filter (· != "")).toArray
  unless lines.size > 0 do throw (IO.userError "empty input")
  let header ← numbers lines[0]!
  unless header.size = 2 do throw (IO.userError "invalid header")
  let n := header[0]!
  let q := header[1]!
  unless n > 0 && n ≤ 192 && q > 0 && lines.size = n+1 do
    throw (IO.userError "invalid order/denominator/row count")
  let denominator := n^4*q^6
  unless denominator ≤ 18446744073709551615 do throw (IO.userError "UInt64 bound exceeded")
  let mut red : Array (Array UInt64) := #[]
  for i in [:n] do
    let row ← numbers lines[i+1]!
    unless row.size = n && row.all (· ≤ q) do throw (IO.userError "invalid probability row")
    red := red.push (row.map UInt64.ofNat)
  for i in [:n] do
    for j in [:n] do
      unless red[i]![j]! = red[j]![i]! do throw (IO.userError "asymmetric probability matrix")
  let blue := red.map (fun row => row.map (fun value => UInt64.ofNat q - value))
  let r := orderedColor n red
  let b := orderedColor n blue
  IO.println s!"{r.toNat} {b.toNat} {(r+b).toNat} {denominator}"
