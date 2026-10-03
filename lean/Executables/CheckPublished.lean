import K4Ramsey.Counting.ValidatedTemplate
import K4Ramsey.Constructions.Published768.Data

open K4Ramsey
open K4Ramsey.Published768

def main (args : List String) : IO Unit := do
  let start ← IO.monoMsNow
  -- A runtime input prevents closed pure counts from being lifted into module
  -- initialization before the timer starts.
  let n := ((args.head?).getD "768").toNat!
  let certificate ← match (⟨n, redRows⟩ : Template).validate with
    | .ok cert => pure cert
    | .error message => throw (IO.userError message)
  let counts := certificate.countSubgraphs
  let numerator := counts.numerator n
  -- Force the pure computation through an IO branch before stopping the timer;
  -- otherwise the compiler can sink it into the later print operations.
  unless numerator = 10487165184 do throw (IO.userError "unexpected numerator")
  let elapsed := (← IO.monoMsNow) - start
  IO.println s!"red edges: {counts.redEdges}; blue triangles: {counts.blueTriangles}"
  IO.println s!"red K4: {counts.redK4}; blue K4: {counts.blueK4}"
  IO.println s!"numerator: {numerator}; denominator: {denominator768}"
  IO.println s!"verification: {elapsed} ms"
