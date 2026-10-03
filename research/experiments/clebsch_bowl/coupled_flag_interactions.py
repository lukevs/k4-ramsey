"""Identify collective versus individual higher-order block effects."""
import json
import time
from pathlib import Path
import numpy as np
import coupled_flag_pilot as core
from coupled_flag_followup import certify

if __name__ == "__main__":
    start = time.monotonic()
    out = Path("reports/global-coupled-pilot-003")
    out.mkdir(exist_ok=True, parents=True)
    g5, g6 = core.atlas(5), core.atlas(6)
    b5 = sum((core.gram_coefficients(g5,r) for r in (1,3)), [])
    b6 = sum((core.gram_coefficients(g6,r) for r in (0,2,4)), [])
    P = core.marginal(g6,g5)
    c = np.array(list(map(core.objective,g6)))
    runs = []
    for sizes in ((0,), (4,), (0,2), (2,4), (0,4)):
        extra = [b for b in b6 if b["roots"] in sizes]
        runs.append(core.solve("root_sizes_"+str(sizes), c, b5, extra, P=P))
    data = {}
    runs.append(core.solve("full_for_exact_certificate",c,b5,b6,P=P,certificate=data))
    cert = certify(c,data,out/"full-certificate.json")
    meta = {"base": [{k:b[k] for k in ("roots","type","flags")} for b in b5],
            "extra": [{k:b[k] for k in ("roots","type","flags")} for b in b6],
            "graphs6": np.array(g6).tolist()}
    (out/"coefficient-metadata.json").write_text(json.dumps(meta)+"\n")
    (out/"result.json").write_text(json.dumps({"runs":runs,"certificate":cert,
        "seconds":time.monotonic()-start},indent=2)+"\n")
    print(json.dumps(cert),flush=True)
