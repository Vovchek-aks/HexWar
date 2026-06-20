from typing import Callable

from attrs import frozen, Factory

from appearance.UI.box import BoxUi
from appearance.UI.button import ButtonUi, SwitchButtonUi, get_image_rectangle
from appearance.UI.image import ImageUi
from appearance.UI.layouts import VerticalLayoutUi, HorizontalLayoutUi
from appearance.UI.layouts.layout import LayoutUi
from appearance.UI.number_shortener import NumberShortener
from appearance.UI.stretcher import StretcherUi
from appearance.UI.text import TextUi, TextData, TextDataBuilder
from appearance.UI.text.test_size_synchroniser import TextSizeSynchroniser
from appearance.graphics.sprites import SpritesLoader
from appearance.UI.drawer import UiDrawer
from appearance.input.clicks_catcher.click import Click, MouseButtons
from appearance.input.mouse_movement_observer import MouseMovementObserver
from appearance.input.moves_inputer.actions_reader import InputActionsReader
from appearance.input.moves_inputer.input_actions import ButtonPressAction, CreationButtonPressAction, \
    ConversionButtonPressAction, CaptureButtonPressAction, AttackButtonPressAction, PullingInitiationButtonPressAction, \
    PullingTerminationButtonPressAction, OreshnikLaunchButtonPressAction, CombinationButtonPressAction
from appearance.language import Language, ARTILLERY_ATTACK, TANK_ATTACK, MOTORIZATION_TO_INFANTRY, INFANTRY_CAPTURE, \
    INFANTRY_TO_MOTORIZATION, ARTILLERY_INITIATE_PULLING, ARTILLERY_TERMINATE_PULLING, LAUNCH_ORESHNIK, \
    CAPITAL_TO_TALL_CAPITAL, CAPITAL_TO_WIDE_CAPITAL, PURCHASE_SETTLEMENT, PURCHASE_PRIVATE_LIGHT_FACTORY, \
    PURCHASE_PRIVATE_HEAVY_FACTORY, MOBILISE_TOWN, TANK_AND_ARTILLERY_TO_HOWITZER, HOWITZER_ATTACK
from appearance.layer import Layer
from appearance.protocols import CellSelector, InputAction
from core.figures.resources_flow_flags import get_resource_flow
from core.player.inputers.bot_player_inputer import BotPlayerInputer
from core.protocols import GameSession, Player, MovesMaker, ValidMove, Creatable, Resource, Movable, ResourcesChanger, \
    ResourcesTaker, ResourcesAdder
from core.resources import Dollars, LightIndustryProducts, HeavyIndustryProducts, ResourcesGroup
from mathematics.rectangle import Rectangle, RectangleBuilder
from mathematics.vector import Vector2, Vector2Int
import core.figures.figure as fig
from observer import Event
from statuses import MISSING, Status


@frozen
class GameUiLayerMaker:
    _drawer: UiDrawer
    _screen_shape: Vector2Int
    _session: GameSession
    _cell_selector: CellSelector
    _mouse_movement_observer: MouseMovementObserver
    _button_press_action_happened: Event[ButtonPressAction, None]
    _moves_maker: MovesMaker
    _actions_reader: InputActionsReader

    _language: Language = Factory(Language.from_meta)
    _sprites_loader: SpritesLoader = Factory(SpritesLoader.from_meta)

    def make(self, on_end_turn_button_was_clicked: Callable[[], None]) -> Layer:
        resources, players_turn = self._make_resources_and_player_turn()

        end_turn_button = self._make_end_turn_button()
        end_turn_button.was_clicked.subscribe(on_end_turn_button_was_clicked)

        layers = [
            players_turn,
            self._make_player_top_list(),
            self._make_current_turn_ui(resources, end_turn_button)
        ]

        return Layer.as_multiple(layers)

    def make_for_multibot(self) -> Layer:
        resources, players_turn = self._make_resources_and_player_turn()

        layers = [
            players_turn,
            resources,
            self._make_player_top_list(),
        ]

        return Layer.as_multiple(layers)

    def make_for_tutorial(self, tutorial_index: int, on_end_turn_button_was_clicked: Callable[[], None]) -> Layer:
        if tutorial_index == 5:
            return Layer.as_multiple([self.make(on_end_turn_button_was_clicked),
                                      self._make_tutorial_hints(tutorial_index)])

        make_current_turn_ui = {
            0: self._make_current_turn_ui_tutorial_0,
            1: self._make_current_turn_ui_tutorial_1
        }.get(tutorial_index, self._make_current_turn_ui_tutorial_2)

        return self._make_for_tutorial(tutorial_index, on_end_turn_button_was_clicked, make_current_turn_ui)

    def _make_for_tutorial(self,
                           tutorial_index: int,
                           on_end_turn_button_was_clicked: Callable[[], None],
                           current_turn_ui_maker: Callable[[ButtonUi], Layer]) -> Layer:
        resources, players_turn = self._make_resources_and_player_turn()
        end_turn_button = self._make_end_turn_button()
        end_turn_button.was_clicked.subscribe(on_end_turn_button_was_clicked)

        layers = [
            players_turn,
            self._make_tutorial_hints(tutorial_index),
            current_turn_ui_maker(end_turn_button)
        ]

        return Layer.as_multiple(layers)

    def _make_current_turn_ui_tutorial_0(self, end_turn_button: ButtonUi) -> Layer:
        layer = Layer.as_multiple([
            self._make_infantry_menu_tutorial_1(),
            end_turn_button,
        ])
        self._session.master.turn_had_started.subscribe(lambda player: layer.set_activity(player.need_ui))
        return layer

    def _make_current_turn_ui_tutorial_1(self, end_turn_button: ButtonUi) -> Layer:
        layer = Layer.as_multiple([
            self._make_infantry_menu_tutorial_2(),
            self._make_artillery_menu(),
            end_turn_button,
        ])
        self._session.master.turn_had_started.subscribe(lambda player: layer.set_activity(player.need_ui))
        return layer

    def _make_current_turn_ui_tutorial_2(self, end_turn_button: ButtonUi) -> Layer:
        layer = Layer.as_multiple([
            self._make_infantry_menu(),
            self._make_motorization_menu(),
            self._make_tank_menu(),
            self._make_artillery_menu(),
            self._make_missile_silo_menu(),
            end_turn_button,
        ])
        self._session.master.turn_had_started.subscribe(lambda player: layer.set_activity(player.need_ui))
        return layer

    def _make_player_top_list(self) -> LayoutUi:
        TOP_PLACES = 5

        layout = VerticalLayoutUi(RectangleBuilder(self._screen_shape)
                                  .from_right_up()
                                  .move(Vector2(20, 10))
                                  .set_shape(Vector2(self._screen_shape.x / 5,
                                                     self._screen_shape.y / 5))
                                  .adjust_for_shape()
                                  .build(),
                                  reserved=TOP_PLACES)

        def update() -> None:
            layout.clear()
            players = self._session.master.players
            rows = sorted(zip(players, map(self._session.cells.get_territories_and_production_ratios_of, players)),
                          key=lambda row: max(row[-1]), reverse=True)[:TOP_PLACES]
            first_element_synchroniser = TextSizeSynchroniser()
            first_row_synchroniser = TextSizeSynchroniser()
            synchroniser = TextSizeSynchroniser()
            add_row(first_element_synchroniser,
                    first_row_synchroniser,
                    self._language.get_player_top_message(),
                    self._language.get_territories_message(),
                    self._language.get_economy_message())
            for player, ratios in rows:
                add_row(synchroniser, synchroniser, player.data.name, *(f"{ratio:.0%}" for ratio in ratios))
            synchroniser.synchronise(first_element_synchroniser.size * .8)
            first_row_synchroniser.synchronise()

        def add_row(first_synchroniser: TextSizeSynchroniser,
                    synchroniser: TextSizeSynchroniser,
                    first: str,
                    second: str,
                    third: str) -> None:
            row_ui = HorizontalLayoutUi(Rectangle.zero(), reserved=2)
            layout.append(row_ui)
            text = TextUi.make(self._drawer, Rectangle.zero(), TextData.debug(first), is_center=True)
            first_synchroniser.append(text)
            row_ui.append(text)
            ratios_ui = HorizontalLayoutUi(Rectangle.zero(), reserved=2, margin_ratio=0.01)
            row_ui.append(ratios_ui)
            ratios_texts = [TextUi.make(self._drawer, Rectangle.zero(), TextData.debug(line), is_center=True)
                            for line in (second, third)]
            synchroniser.extend(*ratios_texts)
            ratios_ui.extend(ratios_texts)

        self._session.master.turn_had_started.subscribe(lambda _: update())
        update()

        return layout

    def _make_resources_and_player_turn(self) -> tuple[VerticalLayoutUi, Layer]:
        width = self._screen_shape.x / 4
        height = self._screen_shape.y / 20
        current_player = TextUi.make(self._drawer,
                                     (RectangleBuilder(self._screen_shape)
                                      .from_left_up()
                                      .move(Vector2((self._screen_shape.x - width) / 2, 10))
                                      .set_shape(Vector2(width, height))
                                      .adjust_for_shape()
                                      .build()),
                                     TextData.debug('...'),
                                     is_center=True)
        current_turn = TextUi.make(self._drawer,
                                   (RectangleBuilder(self._screen_shape)
                                    .from_left_up()
                                    .move(Vector2((self._screen_shape.x - width) / 2, height + 20))
                                    .set_shape(Vector2(width, height))
                                    .adjust_for_shape()
                                    .build()),
                                   TextData.debug('...'),
                                   is_center=True)

        resources, update_resources = self._make_resources([
            Dollars,
            LightIndustryProducts,
            HeavyIndustryProducts,
        ])

        self._moves_maker.resources_flow_could_have_changed.subscribe(lambda: update_resources())
        for player in self._session.master.players:
            player.resources.has_changed.subscribe(lambda _: update_resources())

        def on_turn_passed(player: Player) -> None:
            name = player.data.name
            current_player.set_text(name)
            current_turn.set_text(f"{self._session.master.current_turn}")
            update_resources()

        self._session.master.turn_had_started.subscribe(on_turn_passed)

        on_turn_passed(self._session.master.current_player)
        update_resources()

        return resources, Layer.as_multiple([current_player, current_turn])

    def _make_resources(self, resources: list[type[Resource]]) -> tuple[VerticalLayoutUi, Callable[[], None]]:
        layout = VerticalLayoutUi((RectangleBuilder(self._screen_shape)
                                   .from_left_up()
                                   .move(Vector2(10, 10))
                                   .set_shape(Vector2(self._screen_shape.x / 4,
                                                      self._screen_shape.y / 7))
                                   .adjust_for_shape()
                                   .build()),
                                  margin_ratio=.2,
                                  reserved=len(resources))
        texts = list[TextUi]()
        for _ in resources:
            texts.append(TextUi.make(self._drawer, Rectangle.zero(), TextData.debug('...')))
            layout.append(texts[-1])

        synchroniser = TextSizeSynchroniser()
        synchroniser.extend(*texts)

        def update() -> None:
            player = self._session.master.current_player

            for index, resource_type in enumerate(resources):
                resource = player.resources.get(resource_type)
                current = self._language.get_message_from_resource(resource)

                if isinstance(player.inputer, BotPlayerInputer):
                    texts[index].set_text(f"{current}")
                    continue

                flow = get_resource_flow(player, resource_type, self._session)
                sign = '+' if flow >= 0 else ''
                texts[index].set_text(f"{current} ({sign}{NumberShortener().shorten(flow)})")
            synchroniser.synchronise()

        return layout, update

    def _make_current_turn_ui(self, resources: VerticalLayoutUi, end_turn_button: ButtonUi) -> Layer:
        layer = Layer.as_multiple([
            self._make_figures_creation_menu(),
            self._make_infantry_menu(),
            self._make_motorization_menu(),
            self._make_tank_menu(),
            self._make_artillery_menu(),
            self._make_howitzer_menu(),
            self._make_town_menu(),
            self._make_light_factory_menu(),
            self._make_heavy_factory_menu(),
            self._make_settlement_menu(),
            self._make_private_light_factory_menu(),
            self._make_private_heavy_factory_menu(),
            self._make_capital_menu(),
            self._make_tall_capital_menu(),
            self._make_wide_capital_menu(),
            self._make_bunker_menu(),
            self._make_abandonment_menu(),
            self._make_missile_silo_menu(),
            resources,
            end_turn_button,
        ])
        self._session.master.turn_had_started.subscribe(lambda player: layer.set_activity(player.need_ui))
        return layer

    def _make_end_turn_button(self) -> ButtonUi:
        button_background = self._sprites_loader.load_button_3_to_2()
        button_text = TextData.for_button(self._language.get_end_turn_message())
        button = ButtonUi.make(self._drawer,
                               get_image_rectangle(RectangleBuilder(self._screen_shape)
                                                   .from_right_bottom()
                                                   .move(Vector2(30, 30))
                                                   .set_shape(Vector2(130, 20))
                                                   .adjust_for_shape()
                                                   .build()),
                               button_background,
                               button_text)

        return button

    def _make_figures_creation_menu(self) -> Layer:
        hint_box = BoxUi(Rectangle(Vector2.zero(), Vector2(200, 200)))

        rectangle = self._get_figures_creation_buttons_rectangle()
        buttons = BoxUi(Rectangle.zero())

        layout = HorizontalLayoutUi(RectangleBuilder(self._screen_shape)
                                    .from_left_bottom()
                                    .move(Vector2(20, 20))
                                    .set_shape(Vector2(500, rectangle.shape.y))
                                    .adjust_for_shape()
                                    .build(),
                                    reserved=2)
        layout.append(buttons)
        layout.append(hint_box)

        synchroniser = TextSizeSynchroniser()
        buttons.append(self._make_figures_creation_buttons(synchroniser, hint_box))
        synchroniser.synchronise()

        self._bind_layer_to_cell_with_figure_selection(layout.layer, fig.Land)

        return layout.layer

    def _make_figures_creation_buttons(self, synchroniser: TextSizeSynchroniser, hint_box: BoxUi) -> LayoutUi:
        layout = VerticalLayoutUi(self._get_figures_creation_buttons_rectangle(), margin_ratio=.2, reserved=6)

        self._add_two_horizontal_creation_buttons_to(synchroniser, layout, fig.Bunker, fig.Artillery, hint_box)
        layout.append(self._make_figure_creation_button(synchroniser, fig.MissileSilo, hint_box))
        self._add_two_horizontal_creation_buttons_to(synchroniser, layout, fig.Tank, fig.Infantry, hint_box)
        layout.append(self._make_figure_creation_button(synchroniser, fig.Capital, hint_box))
        self._add_two_horizontal_creation_buttons_to(synchroniser, layout, fig.LightFactory, fig.HeavyFactory, hint_box)
        layout.append(self._make_figure_creation_button(synchroniser, fig.Town, hint_box))

        return layout

    def _add_two_horizontal_creation_buttons_to(self,
                                                synchroniser: TextSizeSynchroniser,
                                                layout: VerticalLayoutUi,
                                                left: type[fig.Figure],
                                                right: type[fig.Figure],
                                                hint_box: BoxUi) -> None:
        horizontal_layout = HorizontalLayoutUi(Rectangle.zero(), margin_ratio=.03, reserved=2)
        layout.append(horizontal_layout)
        horizontal_layout.append(self._make_figure_creation_button(synchroniser, left, hint_box))
        horizontal_layout.append(self._make_figure_creation_button(synchroniser, right, hint_box))

    def _make_figure_creation_button(self,
                                     synchroniser: TextSizeSynchroniser,
                                     figure: type[fig.Figure],
                                     hint_box: BoxUi) -> ButtonUi:
        background = self._sprites_loader.load_button_3_to_2()

        text = TextData.for_button(self._language.get_figure_name(figure))
        position = Vector2.zero()
        button = ButtonUi.make(self._drawer,
                               get_image_rectangle(Rectangle.with_center_at(position, text.shape)),
                               background,
                               text)
        synchroniser.append(button.text)

        button.was_clicked.subscribe(lambda:
                                     self._button_press_action_happened
                                     .invoke(CreationButtonPressAction(self._cell_selector.get_coord(), figure)))

        hint_synchroniser = TextSizeSynchroniser()
        hint_box.append(self._make_figure_creation_button_hint(hint_synchroniser, figure, button))
        hint_synchroniser.synchronise()

        return button

    def _make_figure_creation_button_hint(self,
                                          synchroniser: TextSizeSynchroniser,
                                          figure: type[fig.Figure],
                                          button: ButtonUi) -> StretcherUi:
        title = self._language.get_figure_name(figure)
        content = [
            *self._language.get_creation_hint(figure),
            "",
            *self._language.get_cost(figure.FLAGS.get(Creatable).cost)
        ]
        hint = self._make_button_hint(synchroniser, title, content, button)

        return hint

    def _get_figures_creation_buttons_rectangle(self) -> Rectangle:
        return (RectangleBuilder(self._screen_shape)
                .from_left_bottom()
                .move(Vector2(20, 20))
                .set_shape(Vector2(200, 300))
                .adjust_for_shape()
                .build())

    def _make_infantry_menu(self) -> Layer:
        to_motorize = self._make_null_button(Language.from_meta().get_to_motorize_message())
        to_motorize.was_clicked.subscribe(lambda: self._button_press_action_happened
                                          .invoke(ConversionButtonPressAction(self._cell_selector.get_coord(),
                                                                              fig.Motorization)))

        capture = self._make_activatable_button(self._language.get_capture_message(),
                                                lambda: CaptureButtonPressAction(self._cell_selector.get_coord()))

        return self._make_figure_menu(fig.Infantry, [to_motorize, capture],
                                      [INFANTRY_TO_MOTORIZATION, INFANTRY_CAPTURE])

    def _make_infantry_menu_tutorial_1(self) -> Layer:
        return self._make_figure_menu(fig.Infantry, [], [])

    def _make_infantry_menu_tutorial_2(self) -> Layer:
        capture = self._make_activatable_button(self._language.get_capture_message(),
                                                lambda: CaptureButtonPressAction(self._cell_selector.get_coord()))

        return self._make_figure_menu(fig.Infantry, [capture], [INFANTRY_CAPTURE])

    def _make_motorization_menu(self) -> Layer:
        to_infantry = self._make_null_button(Language.from_meta().get_to_infantry_message())
        to_infantry.was_clicked.subscribe(lambda: self._button_press_action_happened
                                          .invoke(ConversionButtonPressAction(self._cell_selector.get_coord(),
                                                                              fig.Infantry)))

        return self._make_figure_menu(fig.Motorization, [to_infantry], [MOTORIZATION_TO_INFANTRY])

    def _make_town_menu(self) -> Layer:
        mobilise = self._make_null_button(Language.from_meta().get_mobilise_message())
        mobilise.was_clicked.subscribe(lambda: self._button_press_action_happened
                                       .invoke(ConversionButtonPressAction(self._cell_selector.get_coord(),
                                                                           fig.Infantry)))
        return self._make_figure_menu(fig.Town, [mobilise], [MOBILISE_TOWN])

    def _make_light_factory_menu(self) -> Layer:
        return self._make_figure_menu(fig.LightFactory, [], [])

    def _make_heavy_factory_menu(self) -> Layer:
        return self._make_figure_menu(fig.HeavyFactory, [], [])

    def _make_settlement_menu(self) -> Layer:
        purchase = self._make_null_button(Language.from_meta().get_purchase_message())
        purchase.was_clicked.subscribe(lambda: self._button_press_action_happened
                                       .invoke(ConversionButtonPressAction(self._cell_selector.get_coord(),
                                                                           fig.Town)))

        return self._make_figure_menu(fig.Settlement, [purchase], [PURCHASE_SETTLEMENT])

    def _make_private_light_factory_menu(self) -> Layer:
        purchase = self._make_null_button(Language.from_meta().get_purchase_message())
        purchase.was_clicked.subscribe(lambda: self._button_press_action_happened
                                       .invoke(ConversionButtonPressAction(self._cell_selector.get_coord(),
                                                                           fig.LightFactory)))
        return self._make_figure_menu(fig.PrivateLightFactory, [purchase], [PURCHASE_PRIVATE_LIGHT_FACTORY])

    def _make_private_heavy_factory_menu(self) -> Layer:
        purchase = self._make_null_button(Language.from_meta().get_purchase_message())
        purchase.was_clicked.subscribe(lambda: self._button_press_action_happened
                                       .invoke(ConversionButtonPressAction(self._cell_selector.get_coord(),
                                                                           fig.HeavyFactory)))
        return self._make_figure_menu(fig.PrivateHeavyFactory, [purchase], [PURCHASE_PRIVATE_HEAVY_FACTORY])

    def _make_capital_menu(self) -> Layer:
        to_tall_capital = self._make_null_button(Language.from_meta().get_to_tall_capital_message())
        to_tall_capital.was_clicked.subscribe(lambda: self._button_press_action_happened
                                              .invoke(ConversionButtonPressAction(self._cell_selector.get_coord(),
                                                                                  fig.TallCapital)))

        to_wide_capital = self._make_null_button(Language.from_meta().get_to_wide_capital_message())
        to_wide_capital.was_clicked.subscribe(lambda: self._button_press_action_happened
                                              .invoke(ConversionButtonPressAction(self._cell_selector.get_coord(),
                                                                                  fig.WideCapital)))
        return self._make_figure_menu(fig.Capital, [to_tall_capital, to_wide_capital],
                                      [CAPITAL_TO_TALL_CAPITAL, CAPITAL_TO_WIDE_CAPITAL])

    def _make_tall_capital_menu(self) -> Layer:
        return self._make_figure_menu(fig.TallCapital, [], [])

    def _make_wide_capital_menu(self) -> Layer:
        return self._make_figure_menu(fig.WideCapital, [], [])

    def _make_bunker_menu(self) -> Layer:
        return self._make_figure_menu(fig.Bunker, [], [])

    def _make_abandonment_menu(self) -> Layer:
        return self._make_figure_menu(fig.Abandonment, [], [])

    def _make_missile_silo_menu(self) -> Layer:
        launch_oreshnik = self._make_activatable_button(self._language.get_launch_oreshnik_message(),
                                                        lambda: OreshnikLaunchButtonPressAction(
                                                            self._cell_selector.get_coord()))

        return self._make_figure_menu(fig.MissileSilo, [launch_oreshnik], [LAUNCH_ORESHNIK])

    def _make_tank_menu(self) -> Layer:
        attack = self._make_activatable_button(self._language.get_attack_message(),
                                               lambda: AttackButtonPressAction(self._cell_selector.get_coord()))
        combine = self._make_activatable_button(self._language.get_combine_message(),
                                                lambda: CombinationButtonPressAction(self._cell_selector.get_coord(),
                                                                                     fig.Howitzer))

        return self._make_figure_menu(fig.Tank, [attack, combine], [TANK_ATTACK, TANK_AND_ARTILLERY_TO_HOWITZER])

    def _make_artillery_menu(self) -> Layer:
        attack = self._make_activatable_button(self._language.get_attack_message(),
                                               lambda: AttackButtonPressAction(self._cell_selector.get_coord()))

        attach = self._make_activatable_button(self._language.get_initiate_pulling_message(),
                                               lambda: PullingInitiationButtonPressAction(
                                                   self._cell_selector.get_coord()))

        detach = self._make_null_button(self._language.get_terminate_pulling_message())
        detach.was_clicked.subscribe(lambda: self._button_press_action_happened
                                     .invoke(PullingTerminationButtonPressAction(self._cell_selector.get_coord())))

        attach_detach = SwitchButtonUi.make(Rectangle(Vector2.zero(), Vector2.ones()), attach, detach)

        def switch_if_needed() -> None:
            coord = self._cell_selector.get_coord()
            if coord is MISSING:
                return

            cell = self._session.board[coord]
            if not isinstance(figure := cell.figure, fig.Artillery):
                return

            is_pullable = self._session.pulling_connections.is_pullable(figure)
            is_attach_button_active = attach.layer.is_active

            if is_pullable == is_attach_button_active:
                attach_detach.next()

        self._cell_selector.cell_was_selected.subscribe(lambda _: switch_if_needed())
        self._moves_maker.board_move_was_made.subscribe(lambda _: switch_if_needed())

        return self._make_figure_menu(fig.Artillery,
                                      [attack, attach_detach],
                                      [ARTILLERY_ATTACK, (ARTILLERY_INITIATE_PULLING, ARTILLERY_TERMINATE_PULLING)])

    def _make_howitzer_menu(self) -> Layer:
        attack = self._make_activatable_button(self._language.get_attack_message(),
                                               lambda: AttackButtonPressAction(self._cell_selector.get_coord()))

        return self._make_figure_menu(fig.Howitzer, [attack], [HOWITZER_ATTACK])

    def _make_figure_menu(self,
                          figure: type[fig.Figure],
                          buttons: list[ButtonUi | SwitchButtonUi],
                          button_tags: list[str | tuple[str, ...]]) -> Layer:
        assert len(buttons) == len(button_tags)

        menu = self._make_figure_menu_without_hints(figure, buttons)
        menu_width, menu_height = menu.rectangle.shape
        hint_box = BoxUi(Rectangle(menu.rectangle.position + Vector2.right() * (10 + menu_width),
                                   Vector2(menu_height, menu_height)))

        for button, tag in zip(buttons, button_tags):
            if not isinstance(button, SwitchButtonUi):
                synchroniser = TextSizeSynchroniser()
                hint_box.append(self._make_figure_menu_button_hint(synchroniser, button, tag))
                synchroniser.synchronise()
                continue
            for button_, tag_ in zip(button.buttons, tag):
                synchroniser = TextSizeSynchroniser()
                hint_box.append(self._make_figure_menu_button_hint(synchroniser, button_, tag_))
                synchroniser.synchronise()


        layer = Layer.as_multiple([
            menu,
            hint_box,
        ])

        self._bind_layer_to_cell_with_figure_selection(layer, figure)
        return layer

    def _make_figure_menu_without_hints(self,
                                        figure_type: type[fig.Figure],
                                        buttons: list[ButtonUi | SwitchButtonUi]) -> StretcherUi:
        background_margin = Vector2(20, 20)
        background = ImageUi.make(self._drawer,
                                  RectangleBuilder(self._screen_shape)
                                  .from_left_bottom()
                                  .move(background_margin)
                                  .set_shape(Vector2(375, 250))
                                  .adjust_for_shape()
                                  .build(),
                                  self._sprites_loader.load_background_3_to_2())

        title_height = background.rectangle.shape.y / 6
        title_margin = Vector2(15, background.rectangle.shape.y - 10 - title_height)
        title = TextUi.make(self._drawer,
                            RectangleBuilder(self._screen_shape)
                            .move(background.rectangle.position + title_margin)
                            .set_shape(Vector2(background.rectangle.shape.x - title_margin.x * 2,
                                               title_height))
                            .build(),
                            TextDataBuilder()
                            .set_text(self._language.get_figure_name(figure_type))
                            .hints_font()
                            .black_colored()
                            .build())

        layout_margin = Vector2(15, 15)
        buttons_position = background_margin + layout_margin
        buttons_width = background.rectangle.shape.x - layout_margin.x * 2
        buttons_height = background.rectangle.shape.y / 4
        buttons_layout = HorizontalLayoutUi(RectangleBuilder(self._screen_shape)
                                            .from_left_bottom()
                                            .move(buttons_position)
                                            .set_shape(Vector2(buttons_width, buttons_height))
                                            .adjust_for_shape()
                                            .build(),
                                            reserved=len(buttons))
        buttons_layout.extend(buttons)

        title_bottom = title.rectangle.position.y
        stats_margin = 15
        stats_height = title_bottom - buttons_position.y - buttons_height - stats_margin * 2
        stats_position = Vector2(title.rectangle.position.x, title_bottom - stats_margin - stats_height)
        stats_and_flow_rectangle = (RectangleBuilder(self._screen_shape)
                                    .move(stats_position)
                                    .set_shape(Vector2(background.rectangle.shape.x - title_margin.x * 2,
                                                       stats_height))
                                    .adjust_for_shape()
                                    .build())

        stats = VerticalLayoutUi(Rectangle.zero(), margin_ratio=.2, reserved=3)
        flow = VerticalLayoutUi(Rectangle.zero(), margin_ratio=.2, reserved=3)
        stats_and_flow = HorizontalLayoutUi(stats_and_flow_rectangle, reserved=2)
        stats_and_flow.extend([stats, flow])

        text_data = TextDataBuilder().set_text("...").hints_font().black_colored()

        synchroniser = TextSizeSynchroniser()
        update_stats = self._fill_figure_menu_stats(synchroniser, stats, text_data, figure_type)
        update_flow = self._fill_figure_menu_flow(synchroniser, flow, text_data, figure_type)
        synchroniser.synchronise()

        def update(coord: Vector2Int | Status) -> None:
            update_stats(coord)
            update_flow(coord)

        self._cell_selector.cell_was_selected.subscribe(update)
        self._moves_maker.board_move_was_made.subscribe(
            lambda _: update(self._cell_selector.get_coord()))
        self._session.master.turn_had_started.subscribe(
            lambda _: update(self._cell_selector.get_coord()))

        menu = StretcherUi(background.rectangle)
        menu.extend([
            title,
            stats_and_flow,
            buttons_layout,
            background,
        ])

        return menu

    def _fill_figure_menu_stats(self,
                                synchroniser: TextSizeSynchroniser,
                                stats: VerticalLayoutUi,
                                text_data: TextDataBuilder,
                                figure_type: type[fig.Figure]) -> Callable[[Vector2Int | Status], None]:
        combat_ability = TextUi.make(self._drawer, Rectangle.zero(), text_data.build())
        strength = TextUi.make(self._drawer, Rectangle.zero(), text_data.build())
        hardness = TextUi.make(self._drawer, Rectangle.zero(), text_data.build())

        stats.append(combat_ability)
        stats.append(hardness)
        stats.append(strength)
        synchroniser.append(combat_ability)
        synchroniser.append(hardness)
        synchroniser.append(strength)

        def update_stats(coord: Vector2Int | Status) -> None:
            if coord is MISSING:
                return

            figure = self._session.board[coord].figure
            if not isinstance(figure, figure_type):
                return

            update_combat_ability(figure)
            update_strength(figure, coord)
            update_hardness(figure, coord)

        def update_combat_ability(figure: fig.Figure) -> None:
            if figure.MOVES_BUDGET == 0:
                combat_ability.set_text('')
                return

            spent = self._session.figures_budget.of(figure)
            combat_ability.set_text(self._language.get_combat_ability_message(figure, spent))

        def update_strength(figure: fig.Figure, coord: Vector2Int) -> None:
            if (movable := figure.FLAGS.get(Movable)) is MISSING:
                strength.set_text('')
                return

            base = movable.base_strength
            additional = movable.strength(coord, self._session.board) - base

            strength.set_text(self._language.get_strength_message(base, additional))

        def update_hardness(figure: fig.Figure, coord: Vector2Int) -> None:
            board = self._session.board
            base = figure.base_hardness()
            additional = board[coord].hardness(board) - base

            hardness.set_text(self._language.get_hardness_message(base, additional))

        return update_stats

    def _fill_figure_menu_flow(self,
                               synchroniser: TextSizeSynchroniser,
                               flow: VerticalLayoutUi,
                               text_data: TextDataBuilder,
                               figure_type: type[fig.Figure]) -> Callable[[Vector2Int | Status], None]:
        if (changer := figure_type.FLAGS.get(ResourcesChanger)) is MISSING:
            return lambda _: None

        text_of = {resource: TextUi.make(self._drawer, Rectangle.zero(), text_data.build())
                   for resource in changer.changeable_resources}

        if len(text_of) < 2:
            flow.append(BoxUi(Rectangle.zero()))

        flow.extend(text_of.values())
        synchroniser.extend(*text_of.values())

        def update(coord: Vector2Int | Status) -> None:
            if coord is MISSING:
                return

            figure = self._session.board[coord].figure
            if not isinstance(figure, figure_type):
                return

            resources = ResourcesGroup()
            if isinstance(changer, ResourcesAdder):
                resources += changer.get_resources_with_buffs(coord, self._session)
            if isinstance(changer, ResourcesTaker):
                resources -= changer.resources_to_take

            if not resources:
                return

            for resource in resources.not_zero:
                text_of[type(resource)].set_text(self._language.get_message_from_resource(resource))

        return update

    def _make_figure_menu_button_hint(self,
                                      synchroniser: TextSizeSynchroniser,
                                      button: ButtonUi,
                                      tag: str) -> StretcherUi:
        return self._make_button_hint(synchroniser, button.text.text, self._language.get_figure_menu_hint_for(tag),
                                      button, Vector2(200, 220))

    def _make_button_hint(self,
                          synchroniser: TextSizeSynchroniser,
                          title: str,
                          content: list[str],
                          button: ButtonUi,
                          shape: Vector2 = Vector2(200, 300)) -> StretcherUi:
        hint = self._make_null_hint(synchroniser, title, content, shape)

        def get_hint_activity() -> bool:
            if not button.layer.is_active:
                return False

            fake_click = Click(self._mouse_movement_observer.mouse_position, MouseButtons())
            return button.layer.can_catch(fake_click)

        hint.layer.set_activity(False)
        self._mouse_movement_observer.mouse_was_moved.subscribe(lambda _: hint.layer.set_activity(get_hint_activity()))
        button.was_clicked.subscribe(lambda: hint.layer.set_activity(get_hint_activity()))

        return hint

    def _make_tutorial_hints(self, tutorial_index: int) -> BoxUi:
        margin = 20
        box = BoxUi(RectangleBuilder(self._screen_shape)
                    .from_right_up()
                    .set_shape(Vector2(self._screen_shape.x / 4.7,
                                       self._screen_shape.x / 4))
                    .move(Vector2.ones() * margin)
                    .adjust_for_shape()
                    .build())
        for index, content in enumerate(self._language.get_tutorial_hints(tutorial_index)):
            synchroniser = TextSizeSynchroniser()
            box.append(self._make_tutorial_hint(synchroniser, index, content))
            synchroniser.synchronise()

        return box

    def _make_tutorial_hint(self,
                            synchroniser: TextSizeSynchroniser,
                            content_index: int,
                            content: list[str]) -> StretcherUi:
        hint = self._make_null_hint(synchroniser, self._language.get_page_message(content_index), content)
        rectangle = hint.rectangle
        position = rectangle.position
        shape = rectangle.shape

        top_margin = 10
        width = shape.x / 3
        height = width * .7
        skip = self._make_null_button(self._language.get_next_message())
        skip.set_rectangle(Rectangle(
            position.with_y(position.y - top_margin - height),
            Vector2(width, height)
        ))

        stretcher = StretcherUi(Rectangle(
            skip.rectangle.position, shape.with_y(shape.y + top_margin + height)
        ))
        stretcher.append(hint)
        stretcher.append(skip)

        skip.was_clicked.subscribe(lambda: stretcher.layer.set_activity(False))

        return stretcher

    def _make_null_hint(self,
                        synchroniser: TextSizeSynchroniser,
                        title: str,
                        content: list[str],
                        shape: Vector2 = Vector2(200, 300)) -> StretcherUi:
        MIN_LINES_COUNT = 8
        MAX_LINE_LENGTH = 25

        background = ImageUi.make(self._drawer,
                                  Rectangle(Vector2.zero(), shape),
                                  self._sprites_loader.load_background_2_to_3())

        title_margin = Vector2(15, 10)
        title_height = shape.y / 10
        title_ui = TextUi.make(self._drawer,
                               RectangleBuilder(Vector2Int.from_vector2(background.rectangle.shape))
                               .from_left_up()
                               .move(title_margin)
                               .set_shape(Vector2(shape.x - title_margin.x * 2,
                                                  title_height))
                               .adjust_for_shape()
                               .build(),
                               TextDataBuilder()
                               .set_text(title)
                               .hints_font()
                               .black_colored()
                               .build())

        white_spaces = [" "] * (MIN_LINES_COUNT - len(content))
        content = white_spaces[:len(white_spaces) // 2] + content + white_spaces[len(white_spaces) // 2:]
        content_margin = Vector2(title_margin.x, 10 + title_margin.y + title_height)
        bottom_margin = 30
        content_ui = VerticalLayoutUi(RectangleBuilder(Vector2Int.from_vector2(background.rectangle.shape))
                                      .from_left_up()
                                      .move(content_margin)
                                      .set_shape(Vector2(title_ui.rectangle.shape.x,
                                                         shape.y - content_margin.y - bottom_margin))
                                      .adjust_for_shape()
                                      .build(),
                                      reserved=len(content))

        for line in content:
            line_ui = TextUi.make(self._drawer,
                                  Rectangle.zero(),
                                  TextDataBuilder()
                                  .set_text(line.ljust(MAX_LINE_LENGTH, " "))
                                  .hints_font()
                                  .black_colored()
                                  .build())
            content_ui.append(line_ui)
            synchroniser.append(line_ui)

        stretcher = StretcherUi(background.rectangle)
        stretcher.append(title_ui)
        stretcher.append(content_ui)
        stretcher.append(background)
        return stretcher

    def _bind_layer_to_cell_with_figure_selection(self, layer: Layer, figure: type[fig.Figure]) -> None:
        layer.set_activity(False)

        self._cell_selector.cell_was_selected.subscribe(
            lambda coord: layer.set_activity(self._is_ui_needed(coord, figure)))
        self._cell_selector.cell_was_unselected.subscribe(lambda: layer.set_activity(False))

        def on_board_move_was_made(_: ValidMove) -> None:
            if (coord := self._cell_selector.get_coord()) is MISSING:
                layer.set_activity(False)
                return

            return layer.set_activity(self._is_ui_needed(coord, figure))

        self._moves_maker.board_move_was_made.subscribe(on_board_move_was_made)

    def _make_activatable_button(self,
                                 text: str,
                                 action_maker: Callable[[], ButtonPressAction]) -> ButtonUi:
        button = self._make_null_button(text)
        image = button.image
        not_active = image.sprite
        active = self._sprites_loader.load_button_3_to_2_active()

        def set_active() -> None:
            image.set_sprite(active)
            self._button_press_action_happened.invoke(action_maker())

        def set_not_active(action: InputAction, is_last: bool) -> None:
            if not isinstance(action, type(action_maker())):
                return
            if not is_last:
                return

            image.set_sprite(not_active)

        button.was_clicked.subscribe(set_active)
        self._actions_reader.action_was_removed.subscribe(set_not_active)

        return button

    def _make_null_button(self, text: str) -> ButtonUi:
        background = self._sprites_loader.load_button_3_to_2()
        text_data = TextData.for_button(text)
        button = ButtonUi.make(self._drawer,
                               Rectangle(Vector2.zero(), text_data.shape),
                               background,
                               text_data)
        return button

    def _is_ui_needed(self, cell_coord: Vector2Int, figure: type[fig.Figure]) -> bool:
        cell = self._session.board[cell_coord]
        player = self._session.master.current_player
        return (self._is_current_player_need_ui() and
                cell.owner is player and
                type(cell.figure) is figure)  # not isinstance

    def _is_current_player_need_ui(self) -> bool:
        return self._session.master.current_player.need_ui
