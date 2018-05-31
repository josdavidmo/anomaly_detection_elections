from scraping import Scraping

e14 = Scraping()
depts = e14.get_depts()
for dept in depts:
    muns = e14.get_muns(dept[0])
    for mun in muns:
        zones = e14.get_zones(dept[0], mun[0])
        for zone in zones:
            puests = e14.get_puest(dept[0], mun[0], zone[0])
