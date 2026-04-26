from Services.CropActivityData import get_activities_for_crop

acts = get_activities_for_crop('wheat')
print('Wheat activities (with cycles):')
for a in acts:
    print(f'  {a["name"]} - day {a["days_from_sowing"]} (cycle {a["cycle_number"]}/{a["total_cycles"]})')