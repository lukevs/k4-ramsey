import Std

/- Standalone exact-Nat evaluator for a typed-kernel histogram certificate.
   The native generator binds the histogram to the full candidate matrix; this
   program independently checks certificate structure/mass and exact arithmetic. -/

def numbers (line : String) : IO (Array Nat) := do
  let mut values := #[]
  for word in (line.splitOn " ").filter (· != "") do
    let some value := word.toNat? | throw (IO.userError "non-natural certificate entry")
    values := values.push value
  return values

def signatureColor (types q : Nat) (kernels : Array (Array Nat))
    (ids : Array Nat) (blue : Bool) : Nat := Id.run do
  let value := fun (edge s t : Nat) =>
    let raw := kernels[ids[edge]!]![s * types + t]!
    if blue then q - raw else raw
  let mut total := 0
  for s0 in [:types] do
    for s1 in [:types] do
      for s2 in [:types] do
        for s3 in [:types] do
          let product := value 0 s0 s1 * value 1 s0 s2 * value 2 s0 s3 *
            value 3 s1 s2 * value 4 s1 s3 * value 5 s2 s3
          total := total + product
  return total

def main (args : List String) : IO Unit := do
  let some path := args[0]? | throw (IO.userError "usage: typed_kernel_histogram certificate.txt")
  let raw ← IO.FS.readFile (System.FilePath.mk path)
  let lines := ((raw.splitOn "\n").filter (· != "")).toArray
  unless lines.size > 0 do throw (IO.userError "empty certificate")
  let header ← numbers lines[0]!
  unless header.size = 6 do throw (IO.userError "invalid header")
  let n := header[0]!
  let q := header[1]!
  let base := header[2]!
  let types := header[3]!
  let kernelCount := header[4]!
  let histogramCount := header[5]!
  unless n > 0 && q > 0 && base > 0 && types > 0 && types ≤ 16 &&
      n = base * types && kernelCount > 0 && lines.size = 1 + kernelCount + histogramCount do
    throw (IO.userError "invalid dimensions")
  let mut kernels : Array (Array Nat) := #[]
  for i in [:kernelCount] do
    let kernel ← numbers lines[1 + i]!
    unless kernel.size = types * types && kernel.all (· ≤ q) do
      throw (IO.userError "invalid kernel")
    kernels := kernels.push kernel
  let mut red := 0
  let mut blue := 0
  let mut mass := 0
  for i in [:histogramCount] do
    let row ← numbers lines[1 + kernelCount + i]!
    unless row.size = 7 do throw (IO.userError "invalid histogram row")
    let ids := row[:6].toArray
    unless ids.all (· < kernelCount) do throw (IO.userError "kernel id out of range")
    let count := row[6]!
    unless count > 0 do throw (IO.userError "zero histogram count")
    red := red + count * signatureColor types q kernels ids false
    blue := blue + count * signatureColor types q kernels ids true
    mass := mass + count
  unless mass = base ^ 4 do throw (IO.userError "histogram mass mismatch")
  let denominator := n ^ 4 * q ^ 6
  IO.println s!"{red} {blue} {red + blue} {denominator} {mass} {kernelCount} {histogramCount}"
