import json

with open("debug_timeline_raw.json", "r", encoding="utf-8") as f:
    data = json.load(f)

frames = data["info"]["frames"]

print("=== Searching for Grub / Larva related events ===")

found = False

for i, frame in enumerate(frames):
    for ev in frame.get("events", []):
        etype = ev.get("type")
        mtype = ev.get("monsterType", "")
        subtype = ev.get("monsterSubType", "")
        killType = ev.get("killType", "")
        predefined = ev.get("predefinedTargetId", "")

        if (
            mtype in ("HORDE", "VOID_GRUB", "VOID_LARVA")
            or subtype in ("VOIDGRUB", "VOID_LARVA")
            or killType in ("VOID_GRUB", "VOID_LARVA")
            or predefined in ("VOID_GRUB", "VOID_LARVA")
        ):
            found = True
            print(f"\n[Frame {i}] timestamp={ev.get('timestamp')}")
            print(json.dumps(ev, indent=2, ensure_ascii=False))

if not found:
    print("→ No GRUB / LARVA related events found.")
