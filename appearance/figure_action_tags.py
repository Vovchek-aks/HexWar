import core.figures.figure as fig
from core.moves.attack import Attack
from core.moves.capture import Capture
from core.moves.grad_attack import GradAttack
from core.moves.oreshnik_launch import OreshnikLaunch
from core.moves.pulling import PullingInitiation, PullingTermination
from core.protocols import CanLaunchOreshnik, CanGradAttack, Figure
from mathematics.vector import Vector2Int

ARTILLERY_ATTACK = "ARTILLERY_ATTACK"
HOWITZER_ATTACK = "HOWITZER_ATTACK"
GRAD_ATTACK = "GRAD_ATTACK"
TANK_ATTACK = "TANK_ATTACK"
ARTILLERY_INITIATE_PULLING = "ARTILLERY_INITIATE_PULLING"
ARTILLERY_TERMINATE_PULLING = "ARTILLERY_TERMINATE_PULLING"
MOTORIZATION_TO_INFANTRY = "MOTORIZATION_TO_INFANTRY"
CAPITAL_TO_TALL_CAPITAL = "CAPITAL_TO_TALL_CAPITAL"
CAPITAL_TO_WIDE_CAPITAL = "CAPITAL_TO_WIDE_CAPITAL"
TANK_AND_ARTILLERY_TO_HOWITZER = "TANK_AND_ARTILLERY_TO_HOWITZER"
MOTORIZATION_AND_ARTILLERY_TO_GRAD = "MOTORIZATION_AND_ARTILLERY_TO_GRAD"
PURCHASE_SETTLEMENT = "PURCHASE_SETTLEMENT"
PURCHASE_PRIVATE_LIGHT_FACTORY = "PURCHASE_PRIVATE_LIGHT_FACTORY"
PURCHASE_PRIVATE_HEAVY_FACTORY = "PURCHASE_PRIVATE_HEAVY_FACTORY"
MOBILISE_TOWN = "MOBILISE_TOWN"
MOBILISE_SETTLEMENT = "MOBILISE_SETTLEMENT"
INFANTRY_SETTLE = "INFANTRY_SETTLE"
INFANTRY_CAPTURE = "INFANTRY_CAPTURE"
INFANTRY_TO_MOTORIZATION = "INFANTRY_TO_MOTORIZATION"
LAUNCH_ORESHNIK = "LAUNCH_ORESHNIK"

CONVERSIONS = {
    INFANTRY_TO_MOTORIZATION: (fig.Infantry, fig.Motorization),
    MOTORIZATION_TO_INFANTRY: (fig.Motorization, fig.Infantry),
    CAPITAL_TO_TALL_CAPITAL: (fig.TierOneCapital, fig.TallCapital),
    CAPITAL_TO_WIDE_CAPITAL: (fig.TierOneCapital, fig.WideCapital),
    PURCHASE_SETTLEMENT: (fig.Settlement, fig.Town),
    PURCHASE_PRIVATE_LIGHT_FACTORY: (fig.PrivateLightFactory, fig.LightFactory),
    PURCHASE_PRIVATE_HEAVY_FACTORY: (fig.PrivateHeavyFactory, fig.HeavyFactory),
    MOBILISE_TOWN: (fig.Town, fig.Infantry),
    MOBILISE_SETTLEMENT: (fig.Settlement, fig.Infantry),
    INFANTRY_SETTLE: (fig.Infantry, fig.Settlement),
}

COMBINATIONS = {
    TANK_AND_ARTILLERY_TO_HOWITZER: (fig.Tank, fig.Artillery, fig.Howitzer),
    MOTORIZATION_AND_ARTILLERY_TO_GRAD: (fig.Motorization, fig.Artillery, fig.Grad)
}

TAGS_OF: dict[type[fig.Figure], tuple[str]] = {
    fig.Town: (MOBILISE_TOWN,),
    fig.Settlement: (PURCHASE_SETTLEMENT, MOBILISE_SETTLEMENT),
    fig.PrivateLightFactory: (PURCHASE_PRIVATE_LIGHT_FACTORY,),
    fig.PrivateHeavyFactory: (PURCHASE_PRIVATE_HEAVY_FACTORY,),
    fig.TierOneCapital: (CAPITAL_TO_TALL_CAPITAL, CAPITAL_TO_WIDE_CAPITAL),
    fig.MissileSilo: (LAUNCH_ORESHNIK,),
    fig.Infantry: (INFANTRY_TO_MOTORIZATION, INFANTRY_CAPTURE, INFANTRY_SETTLE),
    fig.Motorization: (MOTORIZATION_TO_INFANTRY, MOTORIZATION_AND_ARTILLERY_TO_GRAD),
    fig.Tank: (TANK_ATTACK, TANK_AND_ARTILLERY_TO_HOWITZER),
    fig.Artillery: (ARTILLERY_ATTACK, ARTILLERY_INITIATE_PULLING, ARTILLERY_TERMINATE_PULLING),
    fig.Howitzer: (HOWITZER_ATTACK,),
    fig.Grad: (GRAD_ATTACK,),
}

FIGURE_OF_TAG: dict[str, type[Figure]] = {tag: figure
                                          for figure in TAGS_OF
                                          for tag in TAGS_OF[figure]}

MOVE_OF_TAG = {
    INFANTRY_CAPTURE: lambda: Capture(Vector2Int.zero(), Vector2Int.zero()),
    TANK_ATTACK: lambda: Attack(Vector2Int.zero(), Vector2Int.zero()),
    HOWITZER_ATTACK: lambda: Attack(Vector2Int.zero(), Vector2Int.zero()),
    GRAD_ATTACK: lambda: GradAttack(Vector2Int.zero(), Vector2Int.zero()),
    ARTILLERY_ATTACK: lambda: Attack(Vector2Int.zero(), Vector2Int.zero()),
    ARTILLERY_INITIATE_PULLING: lambda: PullingInitiation(Vector2Int.zero(), Vector2Int.zero()),
    ARTILLERY_TERMINATE_PULLING: lambda: PullingTermination(Vector2Int.zero()),
    LAUNCH_ORESHNIK: lambda: OreshnikLaunch(Vector2Int.zero(), Vector2Int.zero())
}

FLAG_OF_RESOURCE_TAKER = {
    LAUNCH_ORESHNIK: CanLaunchOreshnik,
    GRAD_ATTACK: CanGradAttack,
}
