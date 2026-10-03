import K4Ramsey.Multiplicity
import K4Ramsey.Published768Data

open K4Ramsey
open K4Ramsey.Published768

def main (args : List String) : IO Unit := do
  let start ← IO.monoMsNow
  -- A runtime input prevents closed pure counts from being lifted into module
  -- initialization before the timer starts.
  let n := ((args.head?).getD "768").toNat!
  let certificate : Template := ⟨n, redRows⟩
  unless certificate.isValid do throw (IO.userError "invalid certificate")
  let redEdges := certificate.redEdgeCount
  let blue := certificate.blueRows
  let triangles := triangleCount n blue
  let redK4 := fourCliqueCount n redRows
  let blueK4 := fourCliqueCount n blue
  let numerator := n + 14 * (n * (n - 1) / 2 - redEdges) +
    36 * triangles + 24 * (redK4 + blueK4)
  -- Force the pure computation through an IO branch before stopping the timer;
  -- otherwise the compiler can sink it into the later print operations.
  unless numerator = 10487165184 do throw (IO.userError "unexpected numerator")
  let elapsed := (← IO.monoMsNow) - start
  IO.println s!"red edges: {redEdges}; blue triangles: {triangles}"
  IO.println s!"red K4: {redK4}; blue K4: {blueK4}"
  IO.println s!"numerator: {numerator}; denominator: {denominator768}"
  IO.println s!"verification: {elapsed} ms"
