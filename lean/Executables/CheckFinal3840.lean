import K4Ramsey.Constructions.Final3840.Count

open K4Ramsey.Final3840

def timed (name : String) (f : Unit → Int) : IO Unit := do
  let start ← IO.monoMsNow
  let value := f ()
  IO.println s!"{name}: {value} ({(← IO.monoMsNow) - start} ms)"

def main : IO Unit := do
  let start ← IO.monoMsNow
  let mut totals : Int × Int × Int × Int := (0, 0, 0, 0)
  for i in List.finRange 192 do
    totals := (totals.1 + Count.triangleAt i,
      totals.2.1 + Count.cycleAt i,
      totals.2.2.1 + Count.diamondAt i,
      totals.2.2.2 + Count.tetrahedronAt i)
    if i.val % 16 == 15 then
      IO.println s!"through {i.val}: {totals} ({(← IO.monoMsNow) - start} ms)"
      (← IO.getStdout).flush
  IO.println s!"baseRoot: {Count.baseRoot 0}"
  IO.println s!"TOTALS: {totals}"
