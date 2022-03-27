#!/usr/bin/env python3

import json
import math
import os
import re


NAME_REGEX = re.compile(r"^[a-z][^a-z0-9\-]")
SUPPORTED_LANGUAGES = ["en", "pt", "es"]
SUPPORTED_MECHANICS = {
    "regional-a": {
        "teams": 16,
        "dates": 18
    },
    "regional-b": {
        "teams": 36,
        "dates": 18
    },
    "national-a": {
        "teams": 20,
        "dates": 38
    }
}


def exit_with_error(*error):
    print(*error)
    exit(1)


def verify_name(name):
    return len(name) > 0 and not NAME_REGEX.search(name)


def verify_image(image, path):
    for kind in ["svg", "png", "jpg", "jpeg", "gif"]:
        if os.path.isfile("{path}/{image}.{kind}".format(path=path, image=image, kind=kind)):
            return True
    return False


def check_stadiums():
    print("Checking stadiums:")
    stadiums = {}
    for stadium in os.listdir("stadium"):
        if not verify_name(stadium):
            exit_with_error("  Error found on stadium:", stadium, "the name is invalid")
        json_file = "stadium/{name}/data.json".format(name=stadium)
        if (os.path.isfile(json_file)):
            with open(json_file) as json_file:
                try:
                    data = json.load(json_file)

                    name = data["name"] if "name" in data else exit_with_error("  Error found on stadium:", stadium, "the name is missing")
                    if (len(name) == 0):
                        exit_with_error("  Error found on stadium:", stadium, "the name is empty")
                    for language, localizedName in name.items():
                        if (language not in SUPPORTED_LANGUAGES):
                            exit_with_error("  Error found on stadium:", stadium, "unknown language:", language, "on name")
                        if len(localizedName) == 0:
                            exit_with_error("  Error found on stadium:", stadium, "the name is empty", localizedName)

                    nickname = data["nickname"] if "nickname" in data else exit_with_error("  Error found on stadium:", stadium, "the nickname is missing")
                    if (len(nickname) == 0):
                        exit_with_error("  Error found on stadium:", stadium, "the nickname is empty")
                    for language, localizedNickname in nickname.items():
                        if (language not in SUPPORTED_LANGUAGES):
                            exit_with_error("  Error found on stadium:", stadium, "unknown language:", language, "on nickname")
                        if len(localizedNickname) == 0:
                            exit_with_error("  Error found on stadium:", stadium, "the nickname is empty", localizedNickname)

                    capacity = data["capacity"] if "capacity" in data else exit_with_error("  Error found on stadium:", stadium, "the capacity is missing")
                    if type(capacity) is not int or capacity <= 0:
                        exit_with_error("  Error found on stadium:", stadium, "the capacity is invalid")

                    coord = data["coord"] if "coord" in data else exit_with_error("  Error found on stadium:", stadium, "the coords is missing")
                    lat = coord["lat"] if "lat" in coord else exit_with_error("  Error found on stadium:", stadium, "the lat is missing")
                    lon = coord["lon"] if "lon" in coord else exit_with_error("  Error found on stadium:", stadium, "the lon is missing")
                    if type(lat) is not float or math.isnan(lat) or lat < -90 or lat > 90 or lat == 0.0:
                        exit_with_error("  Error found on stadium:", stadium, "the lat is invalid")
                    if type(lon) is not float or math.isnan(lon) or lon < -90 or lon > 90 or lon == 0.0:
                        exit_with_error("  Error found on stadium:", stadium, "the lon is invalid")

                    stadiums[stadium] = {
                        "name": name,
                        "nickname": nickname,
                        "capacity": capacity,
                        "coord": {
                            "lat": lat,
                            "lon": lon
                        }
                    }
                except Exception as e:
                    exit_with_error("  Error found on stadium:", stadium, "error parsing json data", e)
        else:
            exit_with_error("  Error found on stadium:", stadium, "the data.json file is missing")
    return stadiums


def check_locations_cities(confederation, country, region, cities):
    print("Checking locations: cities for region:", region, "in country:", country, "in confederation:", confederation)
    result = {}
    base_path = "world/{confederation}/{country}/{region}".format(confederation=confederation, country=country, region=region)
    for city in os.listdir(base_path):
        if not os.path.isdir(os.path.join(base_path, city)):
            continue
        if not city in cities:
            exit_with_error("  Error found on city:", city, "the city is not in the list of cities")
        if not verify_image("flag", "{base_path}/{city}".format(base_path=base_path, city=city)):
            exit_with_error("Error: the city", city, "flag image is missing")

        json_file = "{base_path}/{city}/data.json".format(base_path=base_path, city=city)
        if (os.path.isfile(json_file)):
            with open(json_file) as json_file:
                try:
                    data = json.load(json_file)

                    name = data["name"] if "name" in data else exit_with_error("  Error found on city:", city, "the name is missing")
                    if (len(name) == 0):
                        exit_with_error("  Error found on city:", city, "the name is empty")
                    for language, localizedName in name.items():
                        if (language not in SUPPORTED_LANGUAGES):
                            exit_with_error("  Error found on city:", city, "unknown language:", language, "on name")
                        if len(localizedName) == 0:
                            exit_with_error("  Error found on city:", city, "the name is empty", localizedName)

                    coord = data["coord"] if "coord" in data else exit_with_error("  Error found on city:", city, "the coords is missing")
                    lat = coord["lat"] if "lat" in coord else exit_with_error("  Error found on city:", city, "the lat is missing")
                    lon = coord["lon"] if "lon" in coord else exit_with_error("  Error found on city:", city, "the lon is missing")
                    if type(lat) is not float or math.isnan(lat) or lat < -90 or lat > 90 or lat == 0.0:
                        exit_with_error("  Error found on city:", city, "the lat is invalid")
                    if type(lon) is not float or math.isnan(lon) or lon < -90 or lon > 90 or lon == 0.0:
                        exit_with_error("  Error found on city:", city, "the lon is invalid")

                    result[city] = {
                        "name": name,
                        "coord": {
                            "lat": lat,
                            "lon": lon
                        }
                    }
                except Exception as e:
                    exit_with_error("  Error found on city:", city, "error parsing json data", e)
        else:
            exit_with_error("  Error found on city:", city, "the data.json file is missing")

    return result


def check_locations_regions(confederation, country, regions):
    print("Checking locations: regions for country:", country, "in confederation:", confederation)
    result = {}
    base_path = "world/{confederation}/{country}".format(confederation=confederation, country=country)
    for region in os.listdir(base_path):
        if not os.path.isdir(os.path.join(base_path, region)):
            continue
        if not region in regions:
            exit_with_error("  Error found on region:", region, "the region is not in the list of regions")
        if not verify_image("flag", "{base_path}/{region}".format(base_path=base_path, region=region)):
            exit_with_error("Error: the region flag image is missing")

        json_file = "{base_path}/{region}/data.json".format(base_path=base_path, region=region)
        if (os.path.isfile(json_file)):
            with open(json_file) as json_file:
                try:
                    data = json.load(json_file)

                    name = data["name"] if "name" in data else exit_with_error("  Error found on region:", region, "the name is missing")
                    if (len(name) == 0):
                        exit_with_error("  Error found on region:", region, "the name is empty")
                    for language, localizedName in name.items():
                        if (language not in SUPPORTED_LANGUAGES):
                            exit_with_error("  Error found on region:", region, "unknown language:", language, "on name")
                        if len(localizedName) == 0:
                            exit_with_error("  Error found on region:", region, "the name is empty", localizedName)

                    cities = os.listdir("{base_path}/{region}".format(base_path=base_path, region=region))

                    result[region] = {
                        "name": name,
                        "cities": check_locations_cities(confederation, country, region, cities)
                    }
                except Exception as e:
                    exit_with_error("  Error found on region:", region, "error parsing json data", e)
        else:
            exit_with_error("  Error found on region:", region, "the data.json file is missing")

    return result


def check_locations_countries(confederation, countries):
    print("Checking locations: countries for confederation:", confederation)
    result = {}
    base_path = "world/{confederation}".format(confederation=confederation)
    for country in os.listdir(base_path):
        if not os.path.isdir(os.path.join(base_path, country)):
            continue
        if not country in countries:
            exit_with_error("  Error found on country:", country, "the country is not in the list of countries")
        if not verify_image("flag", "{base_path}/{country}".format(base_path=base_path, country=country)):
            exit_with_error("Error: the country flag image is missing")

        json_file = "{base_path}/{country}/data.json".format(base_path=base_path, country=country)
        if (os.path.isfile(json_file)):
            with open(json_file) as json_file:
                try:
                    data = json.load(json_file)

                    name = data["name"] if "name" in data else exit_with_error("  Error found on country:", country, "the name is missing")
                    if (len(name) == 0):
                        exit_with_error("  Error found on country:", country, "the name is empty")
                    for language, localizedName in name.items():
                        if (language not in SUPPORTED_LANGUAGES):
                            exit_with_error("  Error found on country:", country, "unknown language:", language, "on name")
                        if len(localizedName) == 0:
                            exit_with_error("  Error found on country:", country, "the name is empty", localizedName)

                    regions = os.listdir("{base_path}/{country}".format(base_path=base_path, country=country))

                    result[country] = {
                        "name": name,
                        "regions": check_locations_regions(confederation, country, regions)
                    }
                except Exception as e:
                    exit_with_error("  Error found on country:", country, "error parsing json data", e)
        else:
            exit_with_error("  Error found on country:", country, "the data.json file is missing")

    return result


def check_locations_confederations(confederations):
    print("Checking locations: confederations")
    result = {}
    for conf in os.listdir("world"):
        if not os.path.isdir(os.path.join("world", conf)):
            continue
        if not conf in confederations:
            exit_with_error("  Error found on confederation:", conf, "the confederation is not in the list of confederations")
        if not verify_image("logo", "world/{conf}".format(conf=conf)):
            exit_with_error("Error: the conf logo image is missing")

        json_file = "world/{conf}/data.json".format(conf=conf)
        if (os.path.isfile(json_file)):
            with open(json_file) as json_file:
                try:
                    data = json.load(json_file)

                    name = data["name"] if "name" in data else exit_with_error("  Error found on confedetaion:", conf, "the name is missing")
                    if (len(name) == 0):
                        exit_with_error("  Error found on confedetaion:", conf, "the name is empty")
                    for language, localizedName in name.items():
                        if (language not in SUPPORTED_LANGUAGES):
                            exit_with_error("  Error found on confedetaion:", conf, "unknown language:", language, "on name")
                        if len(localizedName) == 0:
                            exit_with_error("  Error found on confedetaion:", conf, "the name is empty", localizedName)

                    nickname = data["nickname"] if "nickname" in data else exit_with_error("  Error found on confedetaion:", conf, "the nickname is missing")
                    if (len(nickname) == 0):
                        exit_with_error("  Error found on confedetaion:", conf, "the nickname is empty")
                    for language, localizedNickname in nickname.items():
                        if (language not in SUPPORTED_LANGUAGES):
                            exit_with_error("  Error found on confedetaion:", conf, "unknown language:", language, "on nickname")
                        if len(localizedNickname) == 0:
                            exit_with_error("  Error found on confedetaion:", conf, "the nickname is empty", localizedNickname)
                    
                    countries = os.listdir("world/{conf}".format(conf=conf))

                    result[conf] = {
                        "name": name,
                        "nickname": nickname,
                        "countries": check_locations_countries(conf, countries)
                    }
                except Exception as e:
                    exit_with_error("  Error found on confedetaion:", conf, "error parsing json data", e)
        else:
            exit_with_error("  Error found on confedetaion:", conf, "the data.json file is missing")

    return result


def check_locations():
    print("Checking locations")
    locations = {}
    if not verify_image("logo", "world"):
        exit_with_error("Error: the world logo image is missing")

    json_file = "world/data.json"
    if (os.path.isfile(json_file)):
        with open(json_file) as json_file:
            try:
                data = json.load(json_file)

                name = data["name"] if "name" in data else exit_with_error("  Error found on world the name is missing")
                if (len(name) == 0):
                    exit_with_error("  Error found on world the name is empty")
                for language, localizedName in name.items():
                    if (language not in SUPPORTED_LANGUAGES):
                        exit_with_error("  Error found on world unknown language:", language, "on name")
                    if len(localizedName) == 0:
                        exit_with_error("  Error found on world the name is empty", localizedName)

                nickname = data["nickname"] if "nickname" in data else exit_with_error("  Error found on world the nickname is missing")
                if (len(nickname) == 0):
                    exit_with_error("  Error found on world the nickname is empty")
                for language, localizedNickname in nickname.items():
                    if (language not in SUPPORTED_LANGUAGES):
                        exit_with_error("  Error found on world unknown language:", language, "on nickname")
                    if len(localizedNickname) == 0:
                        exit_with_error("  Error found on world the nickname is empty", localizedNickname)
                
                confederations = os.listdir("world")

                locations["world"] = {
                    "name": name,
                    "nickname": nickname,
                    "confederations": check_locations_confederations(confederations)
                }
            except Exception as e:
                exit_with_error("  Error found on world: error parsing json data", e)
    else:
        exit_with_error("  Error found on world: the data.json file is missing")

    return locations


def check_teams(stadiums, locations):
    print("Checking teams")
    teams = {}
    for team in os.listdir("teams"):
        if not verify_name(team):
            exit_with_error("  Error found on team:", team, "the name is invalid")
        if not verify_image("shield", "teams/{team}".format(team=team)):
            exit_with_error("Error: the team", team, "shield image is missing")
        json_file = "teams/{team}/data.json".format(team=team)
        if (os.path.isfile(json_file)):
            with open(json_file) as json_file:
                try:
                    data = json.load(json_file)

                    name = data["name"] if "name" in data else exit_with_error("  Error found on team:", team, "the name is missing")
                    if (len(name) == 0):
                        exit_with_error("  Error found on team:", team, "the name is empty")
                    for language, localizedName in name.items():
                        if (language not in SUPPORTED_LANGUAGES):
                            exit_with_error("  Error found on team:", team, "unknown language:", language, "on name")
                        if len(localizedName) == 0:
                            exit_with_error("  Error found on team:", team, "the name is empty", localizedName)

                    nickname = data["nickname"] if "nickname" in data else exit_with_error("  Error found on team:", team, "the nickname is missing")
                    if (len(nickname) == 0):
                        exit_with_error("  Error found on team:", team, "the nickname is empty")
                    for language, localizedNickname in nickname.items():
                        if (language not in SUPPORTED_LANGUAGES):
                            exit_with_error("  Error found on team:", team, "unknown language:", language, "on nickname")
                        if len(localizedNickname) == 0:
                            exit_with_error("  Error found on team:", team, "the nickname is empty", localizedNickname)

                    acronym = data["acronym"] if "acronym" in data else exit_with_error("  Error found on team:", team, "the acronym is missing")
                    if (len(acronym) == 0):
                        exit_with_error("  Error found on team:", team, "the acronym is empty")
                    for language, localizedAcronym in acronym.items():
                        if (language not in SUPPORTED_LANGUAGES):
                            exit_with_error("  Error found on team:", team, "unknown language:", language, "on acronym")
                        if len(localizedAcronym) == 0:
                            exit_with_error("  Error found on team:", team, "the acronym is empty", localizedAcronym)
                        if localizedAcronym.upper() != localizedAcronym:
                            exit_with_error("  Error found on team:", team, "the acronym is not all caps", localizedAcronym)

                    stadium = data["stadium"] if "stadium" in data else exit_with_error("  Error found on team:", team, "the stadium is missing")
                    if (len(stadium) == 0):
                        exit_with_error("  Error found on team:", team, "the stadium is empty")
                    if not stadium in stadiums:
                        exit_with_error("  Error found on team:", team, "the stadium", stadium, "is missing on stadium list")

                    world = data["world"] if "world" in data else exit_with_error("  Error found on team:", team, "the world is missing")
                    continent = world["continent"] if "continent" in world else exit_with_error("  Error found on team:", team, "the continent is missing")
                    country = world["country"] if "country" in world else exit_with_error("  Error found on team:", team, "the country is missing")
                    region = world["region"] if "region" in world else exit_with_error("  Error found on team:", team, "the region is missing")
                    city = world["city"] if "city" in world else exit_with_error("  Error found on team:", team, "the city is missing")

                    if not continent in locations["world"]["confederations"]:
                        exit_with_error("  Error found on team:", team, "the continent", continent, "is missing on locations list")
                    if not country in locations["world"]["confederations"][continent]["countries"]:
                        exit_with_error("  Error found on team:", team, "the country", country, "is missing on locations list")
                    if not region in locations["world"]["confederations"][continent]["countries"][country]["regions"]:
                        exit_with_error("  Error found on team:", team, "the region", region, "is missing on locations list")
                    if not city in locations["world"]["confederations"][continent]["countries"][country]["regions"][region]["cities"]:
                        exit_with_error("  Error found on team:", team, "the city", city, "is missing on locations list")

                    teams[team] = {
                        "name": name,
                        "nickname": nickname,
                        "acronym": acronym,
                        "stadium": stadium,
                        "world": {
                            "continent": continent,
                            "country": country,
                            "region": region,
                            "city": city
                        }
                    }
                except Exception as e:
                    exit_with_error("  Error found on team:", team, "error parsing json data", e)
        else:
            exit_with_error("  Error found on team:", team, "the data.json file is missing")
    return teams


def check_competitions(teams):
    print("Checking competitions")
    result = {
        "dates": {},
        "competitions": {}
    }

    json_file = "competitions/data.json"
    if (os.path.isfile(json_file)):
        with open(json_file) as json_file:
            try:
                data = json.load(json_file)

                for date, competitions in data.items():
                    for competition in competitions:
                        if competition in result["dates"]:
                            result["dates"][competition].append(date)
                        else:
                            result["dates"][competition] = [date]
                        if not competition in result["competitions"]:
                            result["competitions"][competition] = {}
            except Exception as e:
                exit_with_error("  Error found on competitions: error parsing json data", e)
    else:
        exit_with_error("  Error found on competitions: the data.json file is missing")

    for competition in os.listdir("competitions"):
        if not os.path.isdir(os.path.join("competitions", competition)):
            continue
        if not competition in result["competitions"]:
            exit_with_error("  Error found on competition:", competition, "the competition is not in the list of competitions")
        if not verify_image("logo", "competitions/{competition}".format(competition=competition)):
            exit_with_error("  Error found on competition:", competition, "the logo is missing")

        json_file = "competitions/{competition}/data.json".format(competition=competition)
        if (os.path.isfile(json_file)):
            with open(json_file) as json_file:
                try:
                    data = json.load(json_file)

                    name = data["name"] if "name" in data else exit_with_error("  Error found on competition:", competition, "the name is missing")
                    if (len(name) == 0):
                        exit_with_error("  Error found on competition:", competition, "the name is empty")
                    for language, localizedName in name.items():
                        if (language not in SUPPORTED_LANGUAGES):
                            exit_with_error("  Error found on competition:", competition, "unknown language:", language, "on name")
                        if len(localizedName) == 0:
                            exit_with_error("  Error found on competition:", competition, "the name is empty", localizedName)

                    nickname = data["nickname"] if "nickname" in data else exit_with_error("  Error found on competition:", competition, "the nickname is missing")
                    if (len(nickname) == 0):
                        exit_with_error("  Error found on competition:", competition, "the nickname is empty")
                    for language, localizedNickname in nickname.items():
                        if (language not in SUPPORTED_LANGUAGES):
                            exit_with_error("  Error found on competition:", competition, "unknown language:", language, "on nickname")
                        if len(localizedNickname) == 0:
                            exit_with_error("  Error found on competition:", competition, "the nickname is empty", localizedNickname)

                    mechanics = data["mechanics"] if "mechanics" in data else exit_with_error("  Error found on competition:", competition, "the mechanics is missing")
                    if (len(mechanics) == 0):
                        exit_with_error("  Error found on competition:", competition, "the mechanics is empty")
                    if not mechanics in SUPPORTED_MECHANICS:
                        exit_with_error("  Error found on competition:", competition, "the mechanics is invalid")

                    relegation = None
                    if "relegation" in data:
                        relegation = data["relegation"]
                        if not relegation in result["competitions"]:
                            exit_with_error("  Error found on competition:", competition, "the relegation", relegation, "is not in the list of competitions")

                    promotion = None
                    if "promotion" in data:
                        promotion = data["promotion"]
                        if not promotion in result["competitions"]:
                            exit_with_error("  Error found on competition:", competition, "the promotion", promotion, "is not in the list of competitions")

                    competition_teams = data["teams"] if "teams" in data else exit_with_error("  Error found on competition:", competition, "the teams is missing")
                    for team in competition_teams:
                        if not team in teams:
                            exit_with_error("  Error found on competition:", competition, "the team", team, "is not in the list of teams")

                    result["competitions"][competition] = {
                        "name": name,
                        "nickname": nickname,
                        "mechanics": mechanics,
                        "relegation": relegation,
                        "promotion": promotion,
                        "teams": competition_teams
                    }
                except Exception as e:
                    exit_with_error("  Error found on competition:", competition, "error parsing json data", e)
        else:
            exit_with_error("  Error found on competition:", competition, "the data.json file is missing")

    return result


def check_teams_has_competitions(teams, competitions):
    for team in teams:
        found = False
        for _, competition in competitions["competitions"].items():
            if not "teams" in competition:
                continue
            if team in competition["teams"]:
                found = True
                break
        if not found:
            exit_with_error("  Error found on team:", team, "the team is not in the list of competitions")
    return True


def check_mechanics(competitions):
    print("Checking mechanics")
    for competition in competitions["competitions"]:
        if competition == "vacation":
            continue
        comp = competitions["competitions"][competition]
        if len(comp) == 0:
            print("Skipping for now empty competition", competition)
            continue
        dates = competitions["dates"][competition]
        mechanics = SUPPORTED_MECHANICS[comp["mechanics"]]
        if len(comp["teams"]) != mechanics["teams"]:
            exit_with_error("  Error found on competition:", competition, "the number of teams is invalid")
        if len(dates) != mechanics["dates"]:
            exit_with_error("  Error found on competition:", competition, "the number of dates is invalid")


stadiums = check_stadiums()
locations = check_locations()
teams = check_teams(stadiums, locations)
competitions = check_competitions(teams)
check_teams_has_competitions(teams, competitions)
check_mechanics(competitions)

print("\nReport:")

confs = locations["world"]["confederations"]
print(len(confs), "continents")
print(sum([len(confs[conf]["countries"]) for conf in confs]), "countries")
print(sum([sum([len(confs[conf]["countries"][country]["regions"]) for country in confs[conf]["countries"]]) for conf in confs]), "regions")
print(sum([sum([sum([len(confs[conf]["countries"][country]["regions"][region]["cities"]) for region in confs[conf]["countries"][country]["regions"]]) for country in confs[conf]["countries"]]) for conf in confs]), "cities")
print(len(teams), "teams")
print(len(competitions["competitions"]) -1, "competitions") # -1 because of vacation

print("\nAll done, everything looks good!")
