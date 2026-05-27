import reflex as rx
from rxconfig import config
from .llm_client import get_autocomplete_suggestions
import asyncio


class State(rx.State):
    """The app state."""

    user_input: str = ""
    suggestions: list[str] = []
    _pending_request: asyncio.Task | None = None
    _current_request_id: int = 0

    async def handle_input_change(self, text: str):
        """Попробуем не вызывать модель слишком часто и без повода"""
        self.user_input = text

        if len(text) < 3:
            self.suggestions = []
            return

        self._current_request_id += 1
        current_id = self._current_request_id

        # Отменяем предыдущий запрос если он есть
        if self._pending_request and not self._pending_request.done():
            self._pending_request.cancel()
            try:
                await self._pending_request
            except asyncio.CancelledError:
                pass

        await asyncio.sleep(0.3)

        # Проверяем, не был ли запрос отменен
        if current_id != self._current_request_id:
            return

        try:
            self._pending_request = asyncio.create_task(get_autocomplete_suggestions(text, current_id))
            suggestions = await self._pending_request
            # Проверяем, что это самый свежий запрос
            if current_id == self._current_request_id:
                self.suggestions = suggestions
        except asyncio.CancelledError:
            pass
        finally:
            if self._pending_request and self._pending_request.done():
                self._pending_request = None

    def accept_suggestion(self, suggestion: str):
        """Применяет подсказку при клике на нее"""
        base = self.user_input.rstrip()
        if not base.endswith(" "):
            base += " "
        self.user_input = base + suggestion.get("item", "").lstrip()
        self.suggestions = []

    def accept_first_suggestion(self):
        """Применяет подсказку по Tab"""
        if self.suggestions:
            self.accept_suggestion(self.suggestions[0])


def index() -> rx.Component:
    """Это писал Gemini"""
    return rx.center(
        rx.vstack(
            rx.heading("LLM Real-time Autocomplete", size="7", margin_bottom="1rem"),
            rx.text("Начните вводить текст:", color_scheme="gray"),
            # Контейнер для ввода
            rx.box(
                rx.input(
                    value=State.user_input,
                    on_change=State.handle_input_change,
                    on_key_down=rx.call_script("""
                    (e) => {
                        if (e.key === 'Tab') {
                            e.preventDefault();
                            window.quote_app_state.accept_first_suggestion();
                            return true;
                        }
                        return false;
                    }
                    """),
                    placeholder="Начните писать что-нибудь...",
                    width="500px",
                    size="3",
                ),
                width="100%",
            ),
            # Индикатор загрузки
            rx.cond(
                State._pending_request,
                rx.text("Загрузка...", color_scheme="blue", size="2"),
            ),
            # Блок отображения подсказки
            rx.cond(
                State.suggestions,
                rx.flex(
                    rx.foreach(
                        State.suggestions,
                        lambda s: rx.button(
                            s,
                            on_click=lambda s=s: State.accept_suggestion(s),
                            variant="surface",
                            color_scheme="blue",
                            cursor="pointer",
                            size="2",
                        ),
                    ),
                    spacing="2",
                    margin_top="10px",
                    flex_wrap="wrap",
                    width="500px",
                ),
            ),
        ),
        height="100vh",
    )


def result_display() -> rx.Component:
    """Экран с результатом (для демонстрации)."""
    return rx.center(
        rx.vstack(
            rx.heading("Ваш текст:", size="4"),
            rx.text(State.user_input, font_family="monospace", white_space="pre-wrap"),
            rx.button("Перейти к автодополнению", on_click=rx.redirect("/")),
            margin_top="2rem",
        ),
        height="100vh",
    )


app = rx.App()
app.add_page(index, route="/")
app.add_page(result_display, route="/result")
