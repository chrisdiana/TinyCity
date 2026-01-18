"""
TinyCity command-line interface REPL.

Provides a simple text-based interface to interact with the TinyCity simulation.

How to use:
- Run the script to start the REPL.
- Type 'help' to see available commands.
"""

import shlex
try:
    import readline  # Enables arrow-key history in most terminals.
except ImportError:
    readline = None

from data import TERRAIN_MAPS, DEFAULT_TERRAIN
from sim import (
    Sim,
    BUILDING_INFO,
    BUILDING_RESIDENTIAL,
    BUILDING_COMMERCIAL,
    BUILDING_INDUSTRIAL,
    BUILDING_POWERPLANT,
    BUILDING_PARK,
    BUILDING_POLICE,
    BUILDING_FIRE,
    BUILDING_STADIUM,
    BUILDING_THEME_PARK,
    BUILDING_SKYSCRAPER,
    BUILDING_TREES,
    BUILDING_SCHOOL,
    BUILDING_RUBBLE,
    MAX_BUILDINGS,
    ROAD_MASK,
    POWER_MASK,
    ROAD_COST,
    POWERLINE_COST,
    BULLDOZER_COST,
)

BUILDING_NAME_TO_ID = {
    "res": BUILDING_RESIDENTIAL,
    "residential": BUILDING_RESIDENTIAL,
    "com": BUILDING_COMMERCIAL,
    "commercial": BUILDING_COMMERCIAL,
    "ind": BUILDING_INDUSTRIAL,
    "industrial": BUILDING_INDUSTRIAL,
    "power": BUILDING_POWERPLANT,
    "park": BUILDING_PARK,
    "police": BUILDING_POLICE,
    "fire": BUILDING_FIRE,
    "stadium": BUILDING_STADIUM,
    "theme": BUILDING_THEME_PARK,
    "theme_park": BUILDING_THEME_PARK,
    "skyscraper": BUILDING_SKYSCRAPER,
    "trees": BUILDING_TREES,
    "school": BUILDING_SCHOOL,
}

DEFAULT_VIEW_W = 24
DEFAULT_VIEW_H = 16


def notify_callback(message):
    if isinstance(message, tuple):
        text, x, y = message[0], message[1], message[2]
        print("NOTICE:", text, "at", x, y)
    else:
        print("NOTICE:", message)


def parse_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def build_sim(terrain_index=0):
    if terrain_index is None:
        terrain = DEFAULT_TERRAIN
    elif 0 <= terrain_index < len(TERRAIN_MAPS):
        terrain = TERRAIN_MAPS[terrain_index]
    else:
        terrain = DEFAULT_TERRAIN
    return Sim(terrain, notify_callback=notify_callback)


def symbol_for_tile(sim, x, y):
    terrain = sim.terrain_map[y][x]
    connections = sim.get_connections(x, y)
    building = sim.get_building_at(x, y)
    if building:
        if building.type == BUILDING_RESIDENTIAL:
            return "R"
        if building.type == BUILDING_COMMERCIAL:
            return "C"
        if building.type == BUILDING_INDUSTRIAL:
            return "I"
        if building.type == BUILDING_POWERPLANT:
            return "P"
        if building.type == BUILDING_PARK:
            return "K"
        if building.type == BUILDING_POLICE:
            return "L"
        if building.type == BUILDING_FIRE:
            return "F"
        if building.type == BUILDING_STADIUM:
            return "S"
        if building.type == BUILDING_THEME_PARK:
            return "T"
        if building.type == BUILDING_SKYSCRAPER:
            return "Y"
        if building.type == BUILDING_TREES:
            return "t"
        if building.type == BUILDING_SCHOOL:
            return "H"
        if building.type == BUILDING_RUBBLE:
            return "x"
        return "B"
    if connections & ROAD_MASK:
        return "=" if terrain == 0 else "#"
    if connections & POWER_MASK:
        return "+"
    return "." if terrain == 0 else "~"


def show_map(sim, view_x, view_y, view_w, view_h):
    view_x = max(0, min(view_x, sim.map_width - 1))
    view_y = max(0, min(view_y, sim.map_height - 1))
    view_w = max(1, min(view_w, sim.map_width - view_x))
    view_h = max(1, min(view_h, sim.map_height - view_y))
    header = "   "
    for x in range(view_x, view_x + view_w):
        header += str(x % 10)
    print(header)
    for y in range(view_y, view_y + view_h):
        row = []
        for x in range(view_x, view_x + view_w):
            row.append(symbol_for_tile(sim, x, y))
        print("{:>2} {}".format(y % 100, "".join(row)))


def print_stats(sim):
    print("{} Money ${}".format(sim.get_month_year(), sim.money))
    print(
        "Pop R{} C{} I{}".format(
            sim.residential_population,
            sim.commercial_population,
            sim.industrial_population,
        )
    )


def print_help():
    print("Commands:")
    print("  help")
    print("  new [terrain_index]")
    print("  show [x y w h]")
    print("  view [x y w h]  (set viewport)")
    print("  step [n]")
    print("  stats")
    print("  info x y")
    print("  road x y")
    print("  power x y")
    print("  bulldoze x y")
    print("  build <type> x y  (type: res/com/ind/power/park/...)")
    print("  quit")


def repl():
    sim = build_sim(0)
    view_x = 0
    view_y = 0
    view_w = DEFAULT_VIEW_W
    view_h = DEFAULT_VIEW_H
    print("TinyCity sim REPL. Type 'help' for commands.")

    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line:
            continue
        parts = shlex.split(line)
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in ("quit", "exit"):
            break
        if cmd == "help":
            print_help()
            continue
        if cmd == "new":
            terrain_index = parse_int(args[0], 0) if args else 0
            sim = build_sim(terrain_index)
            print("New game started.")
            continue
        if cmd == "show":
            if len(args) >= 2:
                view_x = parse_int(args[0], view_x)
                view_y = parse_int(args[1], view_y)
            if len(args) >= 4:
                view_w = parse_int(args[2], view_w)
                view_h = parse_int(args[3], view_h)
            show_map(sim, view_x, view_y, view_w, view_h)
            continue
        if cmd == "view":
            if len(args) >= 2:
                view_x = parse_int(args[0], view_x)
                view_y = parse_int(args[1], view_y)
            if len(args) >= 4:
                view_w = parse_int(args[2], view_w)
                view_h = parse_int(args[3], view_h)
            print("View set to", view_x, view_y, view_w, view_h)
            continue
        if cmd == "step":
            steps_per_month = MAX_BUILDINGS + 3
            count = parse_int(args[0], steps_per_month) if args else steps_per_month
            for _ in range(max(1, count)):
                sim.simulate_step()
            print(sim.get_month_year())
            continue
        if cmd == "stats":
            print_stats(sim)
            continue
        if cmd == "info":
            if len(args) < 2:
                print("Usage: info x y")
                continue
            x = parse_int(args[0], 0)
            y = parse_int(args[1], 0)
            building = sim.get_building_at(x, y)
            connections = sim.get_connections(x, y)
            print("Terrain:", "land" if sim.is_terrain_clear(x, y) else "water")
            print("Connections:", connections)
            if building:
                info = BUILDING_INFO[building.type]
                print("Building:", info["name"])
                print("Density:", building.population_density)
                print("Power:", int(building.has_power))
                print("Traffic:", int(building.heavy_traffic))
            else:
                print("Building: none")
            continue
        if cmd == "road":
            if len(args) < 2:
                print("Usage: road x y")
                continue
            x = parse_int(args[0], 0)
            y = parse_int(args[1], 0)
            if sim.money < ROAD_COST:
                print("No money")
                continue
            if sim.place_road(x, y):
                sim.money -= ROAD_COST
                print("Road placed.")
            else:
                print("Invalid.")
            continue
        if cmd == "power":
            if len(args) < 2:
                print("Usage: power x y")
                continue
            x = parse_int(args[0], 0)
            y = parse_int(args[1], 0)
            if sim.money < POWERLINE_COST:
                print("No money")
                continue
            if sim.place_powerline(x, y):
                sim.money -= POWERLINE_COST
                print("Power line placed.")
            else:
                print("Invalid.")
            continue
        if cmd == "bulldoze":
            if len(args) < 2:
                print("Usage: bulldoze x y")
                continue
            x = parse_int(args[0], 0)
            y = parse_int(args[1], 0)
            if sim.money < BULLDOZER_COST:
                print("No money")
                continue
            if sim.bulldoze_at(x, y):
                sim.money -= BULLDOZER_COST
                print("Bulldozed.")
            else:
                print("Nothing to bulldoze.")
            continue
        if cmd == "build":
            if len(args) < 3:
                if args and args[0].lower() in ("help", "?"):
                    buildable = {}
                    for name, building_id in BUILDING_NAME_TO_ID.items():
                        if sim.is_tool_unlocked(building_id):
                            buildable.setdefault(building_id, []).append(name)
                    print("Buildable types:")
                    for building_id in sorted(
                        buildable, key=lambda bid: BUILDING_INFO[bid]["name"].lower()
                    ):
                        info = BUILDING_INFO[building_id]
                        aliases = ", ".join(sorted(set(buildable[building_id])))
                        print(
                            "  {}: {} (${})".format(info["name"], aliases, info["cost"])
                        )
                else:
                    print("Usage: build <type> x y")
                    print("Try: build help")
                continue
            name = args[0].lower()
            building_type = BUILDING_NAME_TO_ID.get(name)
            if building_type is None:
                print("Unknown building type:", name)
                continue
            if not sim.is_tool_unlocked(building_type):
                print("Building locked for current year.")
                continue
            x = parse_int(args[1], 0)
            y = parse_int(args[2], 0)
            cost = BUILDING_INFO[building_type]["cost"]
            if sim.money < cost:
                print("No money")
                continue
            if sim.place_building(building_type, x, y):
                sim.money -= cost
                print("Building placed.")
            else:
                print("Invalid.")
            continue

        print("Unknown command:", cmd)


if __name__ == "__main__":
    repl()
