from src.krystal.firewall import Firewall

def test_firewall_anomaly_detection():
    fw = Firewall(cfg={"cadence":{"basis":"time","interval_seconds":1,"reversal_trigger":{"anomaly_threshold":0.2}},
                       "layers":{}}, telemetry=type("T",(),{"emit":lambda *args,**kw:None})(), governance=type("G",(),{"seal_event":lambda *args,**kw:None})())
    assert fw.anomaly_detected({"anomaly_score":0.25}) is True
    assert fw.anomaly_detected({"anomaly_score":0.1}) is False
