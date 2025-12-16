mock_legacy_notams = [
    # NOTAM 1: Simple closure with defined end time
    """
    !DEN 12/034 (KDEN) ZDV
    RWY 17L/35R CLSD due to WIP MOWING.
    EFFECTIVE: 2512181100-2512181500. 
    CONTACT TOWER FOR SPECIFIC INSTRUCTIONS.
    """,
    # NOTAM 2: NAVAID outage with "Until Further Notice" (UFN)
    """
    !SFO 12/035 (KSFO) ZOA
    ILS RWY 28R INOP.
    EFFECTIVE: 2512181230 UNTIL UFN.
    EXPECT VISUAL APPROACHES.
    """,
    # NOTAM 3: Obstruction with altitude limits
    """
    !HYG 08/003 (KHYG) ZAN
    OBST POWER LINES NOT CHARTED 50FT AGL.
    EFFECTIVE: 2512170000-PERM.
    LOC: NEAR APCH END RWY 01.
    """
]